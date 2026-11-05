// Public roadmap. Data: GET /api/roadmap (D1, edge-cached); if that fails, the static roadmap.json built at deploy.
// Past releases for the timeline come from the static releases.json (built from the Steam changelog).
// All text is inserted with textContent: nothing from the API is ever parsed as HTML.
(function () {
  'use strict';

  var COLUMNS = [
    { key: 'live', title: 'In the game', blurb: 'Already live in the current build.' },
    { key: 'next', title: 'Next update', blurb: 'Being built or tested now.' },
    { key: 'planned', title: 'Planned', blurb: 'Agreed, not started.' },
    { key: 'idea', title: 'Ideas', blurb: 'Not decided yet.' }
  ];
  var CATEGORIES = ['Mod', 'Map', 'Script Extender', 'Mod Manager', 'Wiki'];
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  var board = document.getElementById('rm-board');
  var filters = document.getElementById('rm-filters');
  var updatedEl = document.getElementById('rm-updated');
  var draftEl = document.getElementById('rm-draft');
  var errorEl = document.getElementById('rm-error');
  var timelineEl = document.getElementById('rm-timeline');
  var shippedEl = document.getElementById('rm-shipped');
  var shippedList = document.getElementById('rm-shipped-list');
  var activeCategory = 'All';
  var items = [];
  var releases = [];

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null && text !== '') n.textContent = String(text);
    return n;
  }

  function fmtDate(s) {
    if (!s) return '';
    var m = /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$/.exec(s);
    if (!m) return '';
    var mo = m[2] ? MONTHS[Number(m[2]) - 1] : '';
    return [m[3] ? Number(m[3]) : '', mo, m[1]].filter(Boolean).join(' ');
  }

  // links are validated server-side, but only ever follow same-site paths here as well
  function safeLink(href) {
    return typeof href === 'string' && /^\/(total_war|tools)\/[A-Za-z0-9_./?=&#%~+-]+$/.test(href) && href.indexOf('..') < 0 && href.indexOf('//') < 0 ? href : null;
  }

  function progressBar(pct) {
    var wrap = el('div', 'rm-progress');
    wrap.setAttribute('role', 'progressbar');
    wrap.setAttribute('aria-valuemin', '0');
    wrap.setAttribute('aria-valuemax', '100');
    wrap.setAttribute('aria-valuenow', String(pct));
    wrap.setAttribute('aria-label', 'Progress');
    var fill = el('span', 'rm-progress-fill');
    fill.style.width = pct + '%';
    wrap.appendChild(fill);
    var label = el('span', 'rm-progress-label', pct + '%');
    var row = el('div', 'rm-progress-row');
    row.appendChild(wrap);
    row.appendChild(label);
    return row;
  }

  function card(it) {
    var c = el('article', 'rm-card');
    c.setAttribute('data-status', it.status);
    var head = el('div', 'rm-card-head');
    head.appendChild(el('h3', 'rm-title', it.title));
    if (it.draft) head.appendChild(el('span', 'rm-draft-mark', 'Draft'));
    c.appendChild(head);
    if (it.description) c.appendChild(el('p', 'rm-desc', it.description));
    if (typeof it.progress === 'number' && it.status !== 'live') c.appendChild(progressBar(it.progress));
    var meta = el('div', 'rm-meta');
    meta.appendChild(el('span', 'rm-chip', it.category));
    var when = [it.version, fmtDate(it.release_date)].filter(Boolean).join(' · ');
    if (when) meta.appendChild(el('span', 'rm-when', when));
    var href = safeLink(it.link);
    if (href) {
      var a = el('a', 'rm-more', 'Read more');
      a.href = href;
      a.setAttribute('aria-label', 'Read more about ' + it.title);
      meta.appendChild(a);
    }
    c.appendChild(meta);
    return c;
  }

  // ---------- just shipped ----------

  function renderShipped() {
    var live = items.filter(function (i) { return i.status === 'live'; }).sort(function (a, b) {
      return (b.release_date || '').localeCompare(a.release_date || '');
    }).slice(0, 3);
    shippedList.textContent = '';
    if (!live.length) { shippedEl.hidden = true; return; }
    live.forEach(function (it) {
      var c = el('article', 'rm-ship');
      var top = el('div', 'rm-ship-top');
      top.appendChild(el('span', 'rm-ship-badge', 'Live'));
      var when = [it.version, fmtDate(it.release_date)].filter(Boolean).join(' · ');
      if (when) top.appendChild(el('span', 'rm-when', when));
      c.appendChild(top);
      c.appendChild(el('h3', 'rm-ship-title', it.title));
      if (it.description) c.appendChild(el('p', 'rm-desc', it.description));
      var href = safeLink(it.link);
      if (href) { var a = el('a', 'rm-more', 'What changed'); a.href = href; a.setAttribute('aria-label', 'What changed in ' + it.title); c.appendChild(a); }
      shippedList.appendChild(c);
    });
    shippedEl.hidden = false;
  }

  // ---------- timeline ----------

  function releaseLabel(r) {
    var m = /^(\d{4})-(\d{2})/.exec(r.date || '');
    var when = m ? MONTHS[Number(m[2]) - 1] + ' ' + m[1] : (r.display_date || '');
    var t = String(r.title || '');
    var meaningful = t && !/^(update|patch|new content|minor update|update notes)\b/i.test(t) && t.charAt(0) !== '[';
    return { when: when, text: meaningful ? t : 'Update' };
  }

  function node(kind, when, text, sub) {
    var n = el('div', 'rm-node rm-node-' + kind);
    n.appendChild(el('span', 'rm-dot'));
    n.appendChild(el('span', 'rm-node-when', when));
    n.appendChild(el('span', 'rm-node-text', text));
    if (sub) n.appendChild(el('span', 'rm-node-sub', sub));
    return n;
  }

  function renderTimeline() {
    timelineEl.textContent = '';
    var track = el('div', 'rm-track');
    var seen = {};
    var past = releases.filter(function (r) { if (seen[r.date]) return false; seen[r.date] = true; return true; }).slice(-10);
    past.forEach(function (r) {
      var l = releaseLabel(r);
      track.appendChild(node('past', l.when, l.text, ''));
    });

    var nowNode = node('now', 'Now', 'Current build', '');
    track.appendChild(nowNode);

    var next = items.filter(function (i) { return i.status === 'next'; });
    var planned = items.filter(function (i) { return i.status === 'planned'; });
    var ideas = items.filter(function (i) { return i.status === 'idea'; });
    var withProgress = next.filter(function (i) { return typeof i.progress === 'number'; });
    var avg = withProgress.length ? Math.round(withProgress.reduce(function (s, i) { return s + i.progress; }, 0) / withProgress.length) : null;
    track.appendChild(node('next', 'Next update', next.length + (next.length === 1 ? ' item' : ' items'), avg === null ? '' : 'about ' + avg + '% done'));
    track.appendChild(node('planned', 'Planned', planned.length + (planned.length === 1 ? ' item' : ' items'), ''));
    track.appendChild(node('idea', 'Ideas', ideas.length + (ideas.length === 1 ? ' item' : ' items'), ''));
    timelineEl.appendChild(track);
    // bring "Now" into view, leaving some history on the left
    var left = nowNode.offsetLeft - Math.min(240, timelineEl.clientWidth / 3);
    timelineEl.scrollLeft = Math.max(0, left);
  }

  // ---------- board ----------

  function render() {
    board.textContent = '';
    COLUMNS.forEach(function (col) {
      var all = items.filter(function (i) { return i.status === col.key; });
      var list = all.filter(function (i) { return activeCategory === 'All' || i.category === activeCategory; });
      var section = el('section', 'rm-col');
      section.setAttribute('data-status', col.key);
      var h = el('div', 'rm-col-head');
      h.appendChild(el('h2', 'rm-col-title', col.title));
      h.appendChild(el('span', 'rm-count', list.length));
      section.appendChild(h);
      section.appendChild(el('p', 'rm-col-blurb', col.blurb));
      if (!list.length) section.appendChild(el('p', 'rm-empty', 'Nothing here yet.'));
      list.forEach(function (i) { section.appendChild(card(i)); });
      board.appendChild(section);
    });
  }

  function buildFilters() {
    filters.textContent = '';
    ['All'].concat(CATEGORIES).forEach(function (cat) {
      var b = el('button', 'rm-filter', cat);
      b.type = 'button';
      b.setAttribute('aria-pressed', cat === activeCategory ? 'true' : 'false');
      b.addEventListener('click', function () {
        activeCategory = cat;
        buildFilters();
        render();
      });
      filters.appendChild(b);
    });
  }

  function apply(data) {
    items = Array.isArray(data.items) ? data.items : [];
    draftEl.hidden = !items.some(function (i) { return i.draft; });
    if (data.updated_at) {
      var d = new Date(data.updated_at);
      if (!isNaN(d)) updatedEl.textContent = 'Updated ' + d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
    }
    buildFilters();
    render();
    renderShipped();
    renderTimeline();
  }

  function getJson(url) {
    return fetch(url, { headers: { Accept: 'application/json' } }).then(function (r) {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    });
  }

  // releases are optional decoration: the page works without them
  var releasesReady = getJson('data/releases.json').then(function (d) { releases = d.releases || []; }).catch(function () { releases = []; });

  getJson('/api/roadmap')
    .catch(function () { return getJson('data/roadmap.json'); })
    .then(function (data) { return releasesReady.then(function () { apply(data); }); })
    .catch(function () { errorEl.hidden = false; });
})();

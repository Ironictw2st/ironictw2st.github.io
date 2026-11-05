// Public roadmap. Data: GET /api/roadmap (D1, edge-cached); if that fails, the static roadmap.json built at deploy.
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

  var board = document.getElementById('rm-board');
  var filters = document.getElementById('rm-filters');
  var updatedEl = document.getElementById('rm-updated');
  var draftEl = document.getElementById('rm-draft');
  var errorEl = document.getElementById('rm-error');
  var activeCategory = 'All';
  var items = [];

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
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var mo = m[2] ? months[Number(m[2]) - 1] : '';
    return [m[3] ? Number(m[3]) : '', mo, m[1]].filter(Boolean).join(' ');
  }

  function card(it) {
    var c = el('article', 'rm-card');
    c.setAttribute('data-status', it.status);
    var head = el('div', 'rm-card-head');
    head.appendChild(el('h3', 'rm-title', it.title));
    if (it.draft) head.appendChild(el('span', 'rm-draft-mark', 'Draft'));
    c.appendChild(head);
    if (it.description) c.appendChild(el('p', 'rm-desc', it.description));
    var meta = el('div', 'rm-meta');
    meta.appendChild(el('span', 'rm-chip', it.category));
    var when = [it.version, fmtDate(it.release_date)].filter(Boolean).join(' · ');
    if (when) meta.appendChild(el('span', 'rm-when', when));
    c.appendChild(meta);
    return c;
  }

  function render() {
    board.textContent = '';
    COLUMNS.forEach(function (col) {
      var list = items.filter(function (i) {
        return i.status === col.key && (activeCategory === 'All' || i.category === activeCategory);
      });
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
  }

  function getJson(url) {
    return fetch(url, { headers: { Accept: 'application/json' } }).then(function (r) {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    });
  }

  getJson('/api/roadmap')
    .catch(function () { return getJson('data/roadmap.json'); })
    .then(apply)
    .catch(function () { errorEl.hidden = false; });
})();

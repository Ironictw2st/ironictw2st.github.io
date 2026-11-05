// Roadmap editor. Talks only to /api/admin/roadmap/* (guarded by Cloudflare Access + JWT check on the server).
// Everything from the server is written with textContent; there is no innerHTML and no inline handler anywhere.
(function () {
  'use strict';

  var API = '/api/admin/roadmap';
  var COLUMNS = [
    { key: 'live', title: 'In the game' },
    { key: 'next', title: 'Next update' },
    { key: 'planned', title: 'Planned' },
    { key: 'idea', title: 'Ideas' }
  ];

  var board = document.getElementById('rm-board');
  var statusEl = document.getElementById('ad-status');
  var items = [];
  var dragId = null;
  var editingId = null; // null = new item

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null && text !== '') n.textContent = String(text);
    return n;
  }

  function say(msg, isError) {
    statusEl.textContent = msg || '';
    statusEl.className = 'ad-status' + (isError ? ' is-error' : '');
  }

  function api(method, path, body) {
    var opts = { method: method, credentials: 'same-origin', headers: { Accept: 'application/json' } };
    if (body !== undefined) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    return fetch(API + path, opts).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (!r.ok) {
          var err = new Error(data.error || ('Request failed (' + r.status + ')'));
          err.field = data.field;
          err.status = r.status;
          throw err;
        }
        return data;
      });
    });
  }

  function load() {
    return api('GET', '').then(function (d) {
      items = d.items || [];
      render();
    }).catch(function (e) {
      say(e.status === 403 ? 'Access denied. Sign in through Cloudflare Access.' : 'Could not load the roadmap: ' + e.message, true);
    });
  }

  // ---------- board ----------

  function byColumn(key) { return items.filter(function (i) { return i.status === key; }); }

  function cardEl(it) {
    var c = el('article', 'rm-card');
    c.setAttribute('data-status', it.status);
    c.setAttribute('data-id', String(it.id));
    c.draggable = true;

    var head = el('div', 'rm-card-head');
    head.appendChild(el('h3', 'rm-title', it.title));
    if (it.draft) head.appendChild(el('span', 'rm-draft-mark', 'Draft'));
    c.appendChild(head);
    if (it.description) c.appendChild(el('p', 'rm-desc', it.description));
    var meta = el('div', 'rm-meta');
    meta.appendChild(el('span', 'rm-chip', it.category));
    var when = [it.version, it.release_date].filter(Boolean).join(' · ');
    if (when) meta.appendChild(el('span', 'rm-when', when));
    c.appendChild(meta);

    var acts = el('div', 'ad-card-actions');
    acts.appendChild(miniBtn('Edit', function () { openEdit(it); }));
    acts.appendChild(miniBtn('Up', function () { nudge(it.id, -1); }, 'Move ' + it.title + ' up'));
    acts.appendChild(miniBtn('Down', function () { nudge(it.id, 1); }, 'Move ' + it.title + ' down'));
    var del = miniBtn('Delete', null, 'Delete ' + it.title);
    del.addEventListener('click', function () {
      if (!del.classList.contains('is-armed')) {
        del.classList.add('is-armed');
        del.textContent = 'Confirm delete';
        setTimeout(function () { del.classList.remove('is-armed'); del.textContent = 'Delete'; }, 4000);
        return;
      }
      api('DELETE', '/' + it.id).then(function () { say('Deleted.'); return load(); }).catch(function (e) { say(e.message, true); });
    });
    acts.appendChild(del);
    c.appendChild(acts);

    c.addEventListener('dragstart', function (ev) {
      dragId = it.id;
      c.classList.add('is-dragging');
      ev.dataTransfer.effectAllowed = 'move';
      ev.dataTransfer.setData('text/plain', String(it.id));
    });
    c.addEventListener('dragend', function () {
      dragId = null;
      c.classList.remove('is-dragging');
      Array.prototype.forEach.call(board.querySelectorAll('.is-over'), function (n) { n.classList.remove('is-over'); });
    });
    return c;
  }

  function miniBtn(label, fn, aria) {
    var b = el('button', 'ad-mini', label);
    b.type = 'button';
    if (aria) b.setAttribute('aria-label', aria);
    if (fn) b.addEventListener('click', fn);
    return b;
  }

  function render() {
    board.textContent = '';
    COLUMNS.forEach(function (col) {
      var list = byColumn(col.key);
      var section = el('section', 'rm-col');
      section.setAttribute('data-status', col.key);
      var h = el('div', 'rm-col-head');
      h.appendChild(el('h2', 'rm-col-title', col.title));
      h.appendChild(el('span', 'rm-count', list.length));
      section.appendChild(h);
      var body = el('div', 'ad-col-body');
      list.forEach(function (i) { body.appendChild(cardEl(i)); });
      if (!list.length) body.appendChild(el('p', 'rm-empty', 'Drop a card here.'));
      section.appendChild(body);

      section.addEventListener('dragover', function (ev) {
        if (dragId === null) return;
        ev.preventDefault();
        section.classList.add('is-over');
      });
      section.addEventListener('dragleave', function (ev) {
        if (!section.contains(ev.relatedTarget)) section.classList.remove('is-over');
      });
      section.addEventListener('drop', function (ev) {
        ev.preventDefault();
        section.classList.remove('is-over');
        if (dragId === null) return;
        var before = null;
        var cards = body.querySelectorAll('.rm-card');
        for (var k = 0; k < cards.length; k++) {
          var r = cards[k].getBoundingClientRect();
          if (ev.clientY < r.top + r.height / 2) { before = Number(cards[k].getAttribute('data-id')); break; }
        }
        moveTo(dragId, col.key, before);
      });
      board.appendChild(section);
    });
  }

  // ---------- reorder ----------

  function orderPayload(next) {
    var order = [];
    COLUMNS.forEach(function (c) {
      next.filter(function (i) { return i.status === c.key; }).forEach(function (i) { order.push({ id: i.id, status: i.status }); });
    });
    return order;
  }

  function saveOrder(next) {
    say('Saving…');
    return api('POST', '/reorder', { order: orderPayload(next) })
      .then(function () { say('Saved.'); return load(); })
      .catch(function (e) { say(e.message, true); return load(); });
  }

  // move item `id` into column `status`, before item `beforeId` (or at the end)
  function moveTo(id, status, beforeId) {
    var moving = items.filter(function (i) { return i.id === id; })[0];
    if (!moving || id === beforeId) return;
    var rest = items.filter(function (i) { return i.id !== id; });
    var copy = {};
    Object.keys(moving).forEach(function (k) { copy[k] = moving[k]; });
    copy.status = status;
    var at = -1;
    if (beforeId !== null) {
      for (var k = 0; k < rest.length; k++) { if (rest[k].id === beforeId) { at = k; break; } }
    }
    if (at < 0) {
      // end of the target column
      var last = -1;
      for (var j = 0; j < rest.length; j++) { if (rest[j].status === status) last = j; }
      at = last + 1;
    }
    rest.splice(at, 0, copy);
    saveOrder(rest);
  }

  function nudge(id, dir) {
    var it = items.filter(function (i) { return i.id === id; })[0];
    if (!it) return;
    var col = byColumn(it.status);
    var pos = col.map(function (i) { return i.id; }).indexOf(id);
    var target = pos + dir;
    if (target < 0 || target >= col.length) return;
    var beforeId = dir < 0 ? col[target].id : (col[target + 1] ? col[target + 1].id : null);
    moveTo(id, it.status, beforeId);
  }

  // ---------- add / edit ----------

  var dlg = document.getElementById('ad-edit');
  var form = document.getElementById('ad-form');
  var formError = document.getElementById('ad-form-error');
  var F = {
    title: document.getElementById('f-title'),
    description: document.getElementById('f-description'),
    status: document.getElementById('f-status'),
    category: document.getElementById('f-category'),
    version: document.getElementById('f-version'),
    release_date: document.getElementById('f-date'),
    draft: document.getElementById('f-draft')
  };

  function openEdit(it) {
    editingId = it ? it.id : null;
    document.getElementById('ad-edit-title').textContent = it ? 'Edit item' : 'Add item';
    F.title.value = it ? it.title : '';
    F.description.value = it ? it.description : '';
    F.status.value = it ? it.status : 'next';
    F.category.value = it ? it.category : 'Mod';
    F.version.value = it ? it.version : '';
    F.release_date.value = it ? it.release_date : '';
    F.draft.checked = it ? !!it.draft : false;
    formError.hidden = true;
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    F.title.focus();
  }

  function closeDlg(d) { if (typeof d.close === 'function') d.close(); else d.removeAttribute('open'); }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var body = {
      title: F.title.value, description: F.description.value, status: F.status.value, category: F.category.value,
      version: F.version.value, release_date: F.release_date.value, draft: F.draft.checked
    };
    var req = editingId === null ? api('POST', '', body) : api('PUT', '/' + editingId, body);
    document.getElementById('ad-save').disabled = true;
    req.then(function () {
      closeDlg(dlg);
      say('Saved.');
      return load();
    }).catch(function (e) {
      formError.textContent = e.message;
      formError.hidden = false;
      if (e.field && F[e.field]) F[e.field].focus();
    }).then(function () { document.getElementById('ad-save').disabled = false; });
  });

  document.getElementById('ad-add').addEventListener('click', function () { openEdit(null); });
  document.getElementById('ad-cancel').addEventListener('click', function () { closeDlg(dlg); });

  // ---------- history / restore ----------

  var hist = document.getElementById('ad-hist');
  var histList = document.getElementById('ad-hist-list');

  function openHistory() {
    histList.textContent = '';
    api('GET', '/history').then(function (d) {
      (d.history || []).forEach(function (h) {
        var li = el('li');
        var main = el('div', 'ad-hist-main');
        main.appendChild(el('span', 'ad-hist-sum', h.summary || h.action));
        var when = new Date(h.saved_at);
        main.appendChild(el('span', 'ad-hist-meta', (isNaN(when) ? h.saved_at : when.toLocaleString('en-GB')) + ' · ' + h.saved_by + ' · ' + h.action));
        li.appendChild(main);
        var b = miniBtn('Restore this version', null, 'Restore the version saved at ' + h.saved_at);
        b.addEventListener('click', function () {
          if (!b.classList.contains('is-armed')) {
            b.classList.add('is-armed');
            b.textContent = 'Confirm restore';
            setTimeout(function () { b.classList.remove('is-armed'); b.textContent = 'Restore this version'; }, 4000);
            return;
          }
          api('POST', '/restore', { history_id: h.id }).then(function () {
            closeDlg(hist);
            say('Restored. The restore is saved in History too.');
            return load();
          }).catch(function (e) { say(e.message, true); });
        });
        li.appendChild(b);
        histList.appendChild(li);
      });
      if (!(d.history || []).length) histList.appendChild(el('li', null, 'No saved versions yet.'));
      if (typeof hist.showModal === 'function') hist.showModal(); else hist.setAttribute('open', '');
    }).catch(function (e) { say(e.message, true); });
  }

  document.getElementById('ad-history').addEventListener('click', openHistory);
  document.getElementById('ad-hist-close').addEventListener('click', function () { closeDlg(hist); });

  load();
})();

// Light / dark mode. Loaded synchronously in <head> so the right theme is set before first paint (no flash).
// Choice order: saved choice (localStorage "theme") > the system setting (prefers-color-scheme).
(function () {
  'use strict';
  var KEY = 'theme';
  var root = document.documentElement;

  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function system() { return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; }
  function current() { var s = saved(); return s === 'dark' || s === 'light' ? s : system(); }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    root.style.colorScheme = theme;
  }
  apply(current());

  // follow the system if the reader has not chosen
  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var onChange = function () { if (!saved()) { apply(system()); refreshButton(); } };
    if (mq.addEventListener) mq.addEventListener('change', onChange);
  }

  var button = null;

  function label() { return current() === 'dark' ? 'Light mode' : 'Dark mode'; }
  function refreshButton() {
    if (!button) return;
    var dark = current() === 'dark';
    button.textContent = dark ? '☀ Light' : '☾ Dark';
    button.setAttribute('aria-label', 'Switch to ' + (dark ? 'light' : 'dark') + ' mode');
    button.setAttribute('aria-pressed', dark ? 'true' : 'false');
    button.title = label();
  }

  function toggle() {
    var next = current() === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(KEY, next); } catch (e) { /* private mode: still switch for this page */ }
    apply(next);
    refreshButton();
  }

  function mount() {
    button = document.createElement('button');
    button.type = 'button';
    button.className = 'theme-toggle';
    button.addEventListener('click', toggle);
    var navList = document.querySelector('nav.main-nav ul');
    if (navList) {
      var li = document.createElement('li');
      li.className = 'theme-item';
      li.appendChild(button);
      navList.appendChild(li);
    } else {
      var top = document.querySelector('.top-nav') || document.body;
      button.classList.add('theme-toggle-floating');
      top.appendChild(button);
    }
    refreshButton();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();

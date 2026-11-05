// Support buttons (Ko-fi, Patreon). Edit the two addresses below; a button only appears when its address is set.
// Links open in a new tab with rel="noopener noreferrer". Nothing is loaded from those sites.
(function () {
  'use strict';

  var SUPPORT = {
    kofi: 'https://ko-fi.com/ironictw1st',
    patreon: 'https://www.patreon.com/c/ironictw2st'
  };

  var items = [];
  if (/^https:\/\/(www\.)?ko-fi\.com\//.test(SUPPORT.kofi)) items.push({ cls: 'kofi', text: 'Support on Ko-fi', href: SUPPORT.kofi });
  if (/^https:\/\/(www\.)?patreon\.com\//.test(SUPPORT.patreon)) items.push({ cls: 'patreon', text: 'Support on Patreon', href: SUPPORT.patreon });
  if (!items.length) return;

  function link(it) {
    var a = document.createElement('a');
    a.className = 'support-btn ' + it.cls;
    a.href = it.href;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = it.text;
    return a;
  }

  function mount() {
    // home page: next to the Steam / Nexus / Discord buttons
    var row = document.querySelector('.links-row');
    if (row) items.forEach(function (it) { var a = link(it); a.classList.add('link-btn'); row.appendChild(a); });

    // every page: a line in the footer
    var footer = document.querySelector('footer');
    if (footer) {
      var p = document.createElement('p');
      p.className = 'support-row';
      var lead = document.createElement('span');
      lead.textContent = 'Enjoy the mod? ';
      p.appendChild(lead);
      items.forEach(function (it) { p.appendChild(link(it)); });
      footer.insertBefore(p, footer.firstChild);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();

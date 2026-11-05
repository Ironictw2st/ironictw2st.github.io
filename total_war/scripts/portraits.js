// Portrait size variants. The originals (data/images/db/*.png, 0.6-1.3 MB each) stay the source of truth;
// scripts/make_thumbs.py writes small WebP copies next to them:
//   thumb: 160 px wide (~8 KB)  for lists, family trees and faction leaders
//   med:   640 px wide (~40 KB) for the character page hero
// Anything that is not a db portrait PNG is returned unchanged.
window.portraitVariant = function (url, kind) {
  'use strict';
  if (typeof url !== 'string') return url;
  var folder = kind === 'med' ? 'db_med' : 'db_thumb';
  var m = /^(.*\/images\/)db\/(.+)\.png$/i.exec(url);
  return m ? m[1] + folder + '/' + m[2] + '.webp' : url;
};

// File name for a per-item data file (data/details/<key>.js, data/skill_trees/<key>.js).
// Same rule as scripts/split_data.mjs: anything outside [A-Za-z0-9_] becomes ~<hex code point>.
window.dataFileKey = function (key) {
  'use strict';
  return String(key).replace(/[^A-Za-z0-9_]/g, function (ch) { return '~' + ch.codePointAt(0).toString(16); });
};

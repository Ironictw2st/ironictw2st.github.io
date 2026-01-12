/* family_tree_graph_v4.js
   Fixes:
   - Spouses are rendered next to SELF (inside the siblings row cluster), not as a separate column.
   - Children buckets are positioned under their actual parent node (absolute positioning),
     so sibling-children (e.g., Cao De -> Cao Anmin) sit under the sibling, not the root spread.
   - If a child appears under both SELF and a sibling, it is assigned to the sibling (and removed from SELF),
     preventing "nephews" from showing as self-children when the sibling-parent exists.
*/
(function () {
  "use strict";

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  const cssEscape = (function () {
    if (typeof CSS !== "undefined" && CSS && typeof CSS.escape === "function") return CSS.escape.bind(CSS);
    return function (ident) {
      const s = String(ident ?? "");
      if (!s) return "";
      let out = s.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/'/g, "\\'");
      out = out.replace(/[^a-zA-Z0-9_-]/g, (m) => "\\" + m);
      out = out.replace(/^([0-9])/, "\\3" + "$1" + " ");
      return out;
    };
  })();

  function toTemplateKey(raw) {
    const s = String(raw || "");
    if (!s) return "";
    if (s.includes("#")) return s.split("#")[0];
    if (s.includes(":")) return s.split(":")[0].trim();
    return s.trim();
  }

  function findCharacterByTemplate(templateKey) {
    if (!templateKey || typeof CHARACTER_DATA === "undefined") return null;
    return CHARACTER_DATA.find((c) => c && c.key === templateKey) || null;
  }

  function getPortraitUrl(templateKey) {
    if (typeof CHARACTER_DETAILS_LOOKUP === "undefined") return "";
    const d = CHARACTER_DETAILS_LOOKUP[templateKey];
    return d?.portrait?.url || "";
  }

  function getRelationshipLabel(relationship, targetCharacter, isMissing = false) {
    if (isMissing || !targetCharacter) {
      const d = { parent: "Parent", child: "Child", spouse: "Spouse", sibling: "Sibling" };
      return d[relationship] || relationship.charAt(0).toUpperCase() + relationship.slice(1);
    }
    const isMale = targetCharacter.is_male !== false;
    const g = {
      parent: isMale ? "Father" : "Mother",
      child: isMale ? "Son" : "Daughter",
      spouse: isMale ? "Husband" : "Wife",
      sibling: isMale ? "Brother" : "Sister",
    };
    return g[relationship] || relationship.charAt(0).toUpperCase() + relationship.slice(1);
  }

  function extractNameForMissingCharacter(characterKey, currentFamilyName, relationship) {
    if (!characterKey) return "Unknown";
    const templateKey = characterKey.includes("#") ? characterKey.split("#")[0] : characterKey;
    const isGeneric =
      templateKey.toLowerCase().includes("generic") ||
      templateKey.toLowerCase().includes("villager") ||
      templateKey.toLowerCase().includes("normal");

    if (isGeneric) {
      if (currentFamilyName) {
        if (relationship === "parent" || relationship === "sibling" || relationship === "child") return `${currentFamilyName} ???`;
        if (relationship === "spouse") return "Unknown Spouse";
      }
      return "Unknown Relative";
    }
    return templateKey.replace(/^.*template_/, "").replace(/_/g, " ");
  }

  // ---------- family rels ----------
  function resolveFamilyRelsForChar(char) {
    const hasUidData = typeof FAMILY_BY_UID !== "undefined" && typeof TEMPLATE_TO_UIDS !== "undefined";
    const hasTemplateData = typeof FAMILY_BY_TEMPLATE !== "undefined";
    const hasLegacyData = typeof FAMILY_BY_CHARACTER !== "undefined";

    let familyMembers = null;

    if (hasUidData) {
      const details = typeof CHARACTER_DETAILS_LOOKUP !== "undefined" ? (CHARACTER_DETAILS_LOOKUP[char.key] || null) : null;
      let uid = details && (details.template_id || details.templateId || details.templateID)
        ? String(details.template_id || details.templateId || details.templateID)
        : null;

      if (!uid) {
        const uids = (TEMPLATE_TO_UIDS && TEMPLATE_TO_UIDS[char.key]) ? TEMPLATE_TO_UIDS[char.key] : [];
        if (uids.length > 0) uid = uids[0];
      }
      if (uid && FAMILY_BY_UID[uid]) familyMembers = FAMILY_BY_UID[uid];

      if ((!familyMembers || familyMembers.length === 0) && hasTemplateData) {
        familyMembers = FAMILY_BY_TEMPLATE[char.key] || null;
      }
    } else if (hasTemplateData) {
      familyMembers = FAMILY_BY_TEMPLATE[char.key] || null;
    } else if (hasLegacyData) {
      if (FAMILY_BY_CHARACTER[char.key]) familyMembers = FAMILY_BY_CHARACTER[char.key];
      else {
        for (const k in FAMILY_BY_CHARACTER) {
          const templatePart = k.includes("#") ? k.split("#")[0] : k;
          if (templatePart === char.key) { familyMembers = FAMILY_BY_CHARACTER[k]; break; }
        }
      }
    }

    return Array.isArray(familyMembers) ? familyMembers : [];
  }

  function buildRelIndex(char) {
    const rels = resolveFamilyRelsForChar(char);
    const out = { parents: [], spouses: [], siblings: [], children: [] };

    for (const r of rels) {
      const t = r.relationship;
      const template = toTemplateKey(r.related_template || r.related_to || "");
      if (!t) continue;
      if ((t === "child" || t === "parent" || t === "spouse" || t === "sibling") && !template) continue;

      const target = template ? findCharacterByTemplate(template) : null;
      const isMissing = !!template && !target;

      const rec = {
        templateKey: template,
        character: target || (template ? {
          key: template,
          display_name: extractNameForMissingCharacter(template, char.family_name, t),
          display_name_alt: "",
          is_male: null,
        } : null),
        isMissing,
        raw: r,
      };

      if (t === "parent") out.parents.push(rec);
      else if (t === "spouse") out.spouses.push(rec);
      else if (t === "sibling") out.siblings.push(rec);
      else if (t === "child") out.children.push(rec);
    }
    return out;
  }

  function uniqueByTemplate(records) {
    const seen = new Set();
    const out = [];
    for (const r of records) {
      if (!r || !r.templateKey) continue;
      if (seen.has(r.templateKey)) continue;
      seen.add(r.templateKey);
      out.push(r);
    }
    return out;
  }

  function relsForTemplate(templateKey) {
    const c = findCharacterByTemplate(templateKey);
    if (!c) return null;
    return buildRelIndex(c);
  }

  // ---------- node html ----------
  function nodeHtml(node, role, opts = {}) {
    const { templateKey, character, isMissing } = node;
    const name = character?.display_name || "Unknown";
    const alt = character?.display_name_alt || "";
    const portraitUrl = isMissing ? "" : getPortraitUrl(templateKey);

    const clickable = !isMissing && opts.clickable !== false;
    const href = clickable ? `character.html?key=${encodeURIComponent(templateKey)}` : null;

    const cls = ["ftg4-node", isMissing ? "ftg4-missing" : "", opts.kind ? `ftg4-${opts.kind}` : ""].filter(Boolean).join(" ");
    const rel = role ? `<div class="ftg4-rel">${escapeHtml(role)}</div>` : "";

    const portrait = portraitUrl
      ? `<div class="ftg4-portrait" style="background-image:url('${escapeHtml(portraitUrl)}')"></div>`
      : `<div class="ftg4-portrait ftg4-portrait-missing">?</div>`;

    const label = `
      <div class="ftg4-name">
        ${escapeHtml(name)}
        ${alt ? `<div class="ftg4-name-alt">${escapeHtml(alt)}</div>` : ""}
      </div>`;

    const attrs = [
      `data-char-key="${escapeHtml(templateKey)}"`,
      opts.parentKey ? `data-parent-key="${escapeHtml(opts.parentKey)}"` : "",
      opts.group ? `data-group="${escapeHtml(opts.group)}"` : "",
    ].filter(Boolean).join(" ");

    const inner = `${rel}${portrait}${label}`;
    if (href) return `<a class="${cls}" href="${href}" ${attrs}>${inner}</a>`;
    return `<div class="${cls}" ${attrs}>${inner}</div>`;
  }

  // ---------- model ----------
  function buildModel(rootChar) {
    const root = { templateKey: rootChar.key, character: rootChar, isMissing: false };
    const idx = buildRelIndex(rootChar);

    const parents = uniqueByTemplate(idx.parents);
    const spouses = uniqueByTemplate(idx.spouses);
    const siblings = uniqueByTemplate(idx.siblings);

    const siblingsRow = [{ templateKey: root.templateKey, character: root.character, isMissing: false, kind: "self" }, ...siblings.map(s => ({ ...s, kind: "sibling" }))];

    // Children per parent in {self + siblings}
    const childrenByParent = new Map();
    const siblingChildSets = new Map(); // for reassignment

    for (const s of siblings) {
      const sidx = relsForTemplate(s.templateKey);
      if (!sidx) continue;
      const kids = uniqueByTemplate(sidx.children);
      childrenByParent.set(s.templateKey, kids);
      siblingChildSets.set(s.templateKey, new Set(kids.map(k => k.templateKey)));
    }

    // Root children, but remove any child that is also a child of a sibling (assign to sibling)
    let rootKids = uniqueByTemplate(idx.children);
    if (rootKids.length && siblingChildSets.size) {
      const siblingAllKids = new Set();
      for (const set of siblingChildSets.values()) for (const k of set) siblingAllKids.add(k);
      rootKids = rootKids.filter(k => !siblingAllKids.has(k.templateKey));
    }
    childrenByParent.set(root.templateKey, rootKids);

    return { root, parents, spouses, siblingsRow, childrenByParent };
  }

  // ---------- render ----------
  function render(targetEl, model) {
    const parentsHtml = model.parents.length
      ? `<div class="ftg4-parents-row">
           ${model.parents.map(p => nodeHtml(p, getRelationshipLabel("parent", p.character, p.isMissing), { kind: "parent", group: "parents" })).join("")}
         </div>`
      : "";

    // siblings row, but SELF becomes a cluster that also contains spouses
    const sibNodes = model.siblingsRow.map(n => {
      const role = n.kind === "self" ? "Self" : getRelationshipLabel("sibling", n.character, n.isMissing);
      const selfNode = nodeHtml(n, role, { kind: n.kind === "self" ? "self" : "sibling", group: "siblings" });

      if (n.kind !== "self") return selfNode;

      const spouseHtml = model.spouses.length
        ? `<div class="ftg4-spouses" data-row="spouses">
             ${model.spouses.map(s => nodeHtml(s, getRelationshipLabel("spouse", s.character, s.isMissing), { kind: "spouse", group: "spouses" })).join("")}
           </div>`
        : "";

      return `<div class="ftg4-self-cluster">${selfNode}${spouseHtml}</div>`;
    }).join("");

    const sibHtml = `<div class="ftg4-siblings-row" data-row="siblings">${sibNodes}</div>`;

    // children buckets container (absolute positioning)
    const bucketsHtml = model.siblingsRow.map(n => {
      const kids = model.childrenByParent.get(n.templateKey) || [];
      const isRoot = n.templateKey === model.root.templateKey;
      const bucketCls = ["ftg4-child-bucket", isRoot ? "ftg4-child-bucket-root" : ""].filter(Boolean).join(" ");
      return `
        <div class="${bucketCls}" data-parent="${escapeHtml(n.templateKey)}">
          ${kids.map(k => nodeHtml(k, getRelationshipLabel("child", k.character, k.isMissing), { kind: "child", parentKey: n.templateKey, group: "children" })).join("")}
        </div>`;
    }).join("");

    targetEl.innerHTML = `
      <div class="ftg4-wrap">
        <div class="ftg4-canvas">
          <svg class="ftg4-lines" xmlns="http://www.w3.org/2000/svg"></svg>
          ${parentsHtml}
          ${sibHtml}
          <div class="ftg4-children-row" data-row="children">${bucketsHtml}</div>
        </div>
      </div>
    `;

    requestAnimationFrame(() => layoutAndDraw(targetEl, model));
    window.addEventListener("resize", () => layoutAndDraw(targetEl, model), { passive: true });
  }

  function rect(el, canvasRect) {
    const r = el.getBoundingClientRect();
    return {
      left: r.left - canvasRect.left,
      right: r.right - canvasRect.left,
      top: r.top - canvasRect.top,
      bottom: r.bottom - canvasRect.top,
      midX: (r.left - canvasRect.left) + r.width / 2,
      midY: (r.top - canvasRect.top) + r.height / 2,
      w: r.width,
      h: r.height,
    };
  }

  function layoutBuckets(rootEl, model, canvasRect) {
    const childrenRow = rootEl.querySelector(".ftg4-children-row");
    if (!childrenRow) return;
    const rowRect = childrenRow.getBoundingClientRect();
    const rowTop = rowRect.top - canvasRect.top;

    // Place each bucket under its parent node center
    const buckets = Array.from(childrenRow.querySelectorAll(".ftg4-child-bucket"));
    let maxBottom = 0;

    for (const b of buckets) {
      const parentKey = b.getAttribute("data-parent") || "";
      const parentNode = rootEl.querySelector(`.ftg4-siblings-row .ftg4-node[data-char-key="${cssEscape(parentKey)}"]`);
      if (!parentNode) continue;
      const pR = rect(parentNode, canvasRect);

      b.style.left = `${pR.midX}px`;
      b.style.top = `${rowTop}px`;
      b.style.transform = "translateX(-50%)";

      // track bottom
      const bR = b.getBoundingClientRect();
      const bottom = (bR.bottom - canvasRect.top);
      if (bottom > maxBottom) maxBottom = bottom;
    }

    // ensure canvas has enough height for svg
    const canvas = rootEl.querySelector(".ftg4-canvas");
    if (canvas && maxBottom) {
      const pad = 18;
      canvas.style.minHeight = `${Math.ceil(maxBottom + pad)}px`;
    }
  }

  function drawLines(rootEl, model) {
    const canvas = rootEl.querySelector(".ftg4-canvas");
    const svg = rootEl.querySelector(".ftg4-lines");
    if (!canvas || !svg) return;

    const canvasRect = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.round(canvasRect.width));
    const height = Math.max(1, Math.round(canvasRect.height));
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.innerHTML = "";

    function addLine(x1, y1, x2, y2, cls = "") {
      const l = document.createElementNS("http://www.w3.org/2000/svg", "line");
      l.setAttribute("x1", x1); l.setAttribute("y1", y1);
      l.setAttribute("x2", x2); l.setAttribute("y2", y2);
      l.setAttribute("class", `ftg4-line ${cls}`.trim());
      svg.appendChild(l);
    }
    function bracket(xs, y, drop, cls="") {
      if (!xs.length) return;
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      addLine(minX, y, maxX, y, cls);
      addLine(minX, y, minX, drop, cls);
      addLine(maxX, y, maxX, drop, cls);
    }

    // Parents -> siblings bracket (across siblings row)
    const parentEls = Array.from(rootEl.querySelectorAll(".ftg4-parents-row .ftg4-node"));
    const sibEls = Array.from(rootEl.querySelectorAll(".ftg4-siblings-row .ftg4-node"));
    const selfEl = rootEl.querySelector(`.ftg4-siblings-row .ftg4-node[data-char-key="${cssEscape(model.root.templateKey)}"]`);

    if (parentEls.length && sibEls.length && selfEl) {
      const pMids = parentEls.map(el => rect(el, canvasRect)).map(r => ({x:r.midX, y:r.bottom}));
      const sibRects = sibEls.map(el => rect(el, canvasRect));
      const y = Math.min(...sibRects.map(r => r.top)) - 18;
      bracket(sibRects.map(r => r.midX), y, y + 14);
      const selfR = rect(selfEl, canvasRect);
      addLine(selfR.midX, y + 14, selfR.midX, selfR.top - 2);
      const py = Math.max(...pMids.map(p => p.y)) + 14;
      bracket(pMids.map(p => p.x), py, y - 6, "ftg4-soft");
      pMids.forEach(p => addLine(p.x, p.y, p.x, py, "ftg4-soft"));
    }

    // Spouse connector(s): self -> each spouse within self-cluster
    if (selfEl) {
      const spouseEls = Array.from(rootEl.querySelectorAll(".ftg4-spouses .ftg4-node"));
      if (spouseEls.length) {
        const selfR = rect(selfEl, canvasRect);
        spouseEls.forEach(sp => {
          const sR = rect(sp, canvasRect);
          const y = Math.min(selfR.midY, sR.midY);
          addLine(selfR.right + 10, y, sR.left - 10, y, "ftg4-soft");
        });
      }
    }

    // Children brackets per parent bucket
    const buckets = Array.from(rootEl.querySelectorAll(".ftg4-child-bucket"));
    for (const b of buckets) {
      const parentKey = b.getAttribute("data-parent") || "";
      const parentNode = rootEl.querySelector(`.ftg4-siblings-row .ftg4-node[data-char-key="${cssEscape(parentKey)}"]`);
      const kids = Array.from(b.querySelectorAll(".ftg4-node"));
      if (!parentNode || !kids.length) continue;

      const pR = rect(parentNode, canvasRect);
      const kidRects = kids.map(k => rect(k, canvasRect));
      const y = Math.min(...kidRects.map(r => r.top)) - 16;
      bracket(kidRects.map(r => r.midX), y, y + 12);
      addLine(pR.midX, pR.bottom, pR.midX, y);
      kidRects.forEach(r => addLine(r.midX, y + 12, r.midX, r.top));
    }
  }

  function layoutAndDraw(rootEl, model) {
    const canvas = rootEl.querySelector(".ftg4-canvas");
    if (!canvas) return;
    const canvasRect = canvas.getBoundingClientRect();
    layoutBuckets(rootEl, model, canvasRect);
    requestAnimationFrame(() => drawLines(rootEl, model));
  }

  // ---------- API ----------
  window.FamilyTreeGraphV4 = {
    renderInto(targetEl, char) {
      if (!targetEl || !char) return;

      const hasAny = (typeof FAMILY_BY_UID !== "undefined") ||
        (typeof FAMILY_BY_TEMPLATE !== "undefined") ||
        (typeof FAMILY_BY_CHARACTER !== "undefined");

      if (!hasAny) {
        targetEl.innerHTML = '<div class="family-tree-empty">Family tree data not available.</div>';
        return;
      }

      const model = buildModel(char);
      const any = model.parents.length || model.spouses.length || (model.siblingsRow.length > 1);
      const selfKids = model.childrenByParent.get(model.root.templateKey) || [];
      if (!any && selfKids.length === 0) {
        targetEl.innerHTML = '<div class="family-tree-empty">No known family relationships for this character.</div>';
        return;
      }

      render(targetEl, model);
    }
  };
})();
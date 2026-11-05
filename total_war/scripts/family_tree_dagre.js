(function () {
  /**
   * Extended Family Tree Dagre - Full Recursive Traversal
   * 
   * Features:
   * - Recursive BFS to show complete family tree (grandparents, grandchildren, etc.)
   * - Spouses positioned to the LEFT of their partner (for ALL characters)
   * - Zoom controls (+, -, reset)
   * - Direct children aligned on same row
   */

  const MAX_DEPTH = 6;

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function getCharacterByTemplate(templateKey) {
    if (!templateKey || typeof CHARACTER_DATA === "undefined") return null;
    return CHARACTER_DATA.find((c) => c.key === templateKey) || null;
  }

  function getRelationsForTemplate(templateKey) {
    if (!templateKey) return [];

    const hasUidData = (typeof FAMILY_BY_UID !== "undefined") && (typeof TEMPLATE_TO_UIDS !== "undefined");
    const hasTemplateData = (typeof FAMILY_BY_TEMPLATE !== "undefined");
    const hasLegacyData = (typeof FAMILY_BY_CHARACTER !== "undefined");

    if (hasUidData) {
      const uids = (TEMPLATE_TO_UIDS && TEMPLATE_TO_UIDS[templateKey]) ? TEMPLATE_TO_UIDS[templateKey] : [];
      const uid = uids.length ? String(uids[0]) : null;
      if (uid && FAMILY_BY_UID && FAMILY_BY_UID[uid]) return FAMILY_BY_UID[uid];
      if (hasTemplateData && FAMILY_BY_TEMPLATE[templateKey]) return FAMILY_BY_TEMPLATE[templateKey];
      return [];
    }

    if (hasTemplateData && FAMILY_BY_TEMPLATE[templateKey]) return FAMILY_BY_TEMPLATE[templateKey];

    if (hasLegacyData) {
      if (FAMILY_BY_CHARACTER[templateKey]) return FAMILY_BY_CHARACTER[templateKey];
      for (const k in FAMILY_BY_CHARACTER) {
        const templatePart = k.includes("#") ? k.split("#")[0] : k;
        if (templatePart === templateKey) return FAMILY_BY_CHARACTER[k];
      }
    }

    return [];
  }

  function getDetailsPortraitUrl(templateKey) {
    if (typeof CHARACTER_DETAILS_LOOKUP === "undefined") return "";
    const details = CHARACTER_DETAILS_LOOKUP[templateKey] || null;
    return details?.portrait?.url || "";
  }

  function extractRelatedTemplate(rel) {
    const t = rel.related_template || rel.related_to || "";
    if (!t) return "";
    return t.includes("#") ? t.split("#")[0] : t;
  }

  /**
   * Build complete family closure via BFS
   */
  function buildFamilyClosure(centerKey, maxDepth = MAX_DEPTH) {
    const nodes = new Set();
    const parentEdges = [];
    const spouseEdges = [];
    const parentEdgeSet = new Set();
    const spouseEdgeSet = new Set();
    const visited = new Set();
    const nodeRoles = new Map();
    const directChildren = new Set();

    const queue = [{ key: centerKey, depth: 0 }];
    nodes.add(centerKey);
    nodeRoles.set(centerKey, "self");

    function addParentEdge(parentKey, childKey) {
      const id = `${parentKey}|${childKey}`;
      if (!parentEdgeSet.has(id)) {
        parentEdgeSet.add(id);
        parentEdges.push({ from: parentKey, to: childKey });
      }
    }

    function addSpouseEdge(a, b) {
      const id = [a, b].sort().join("|");
      if (!spouseEdgeSet.has(id)) {
        spouseEdgeSet.add(id);
        spouseEdges.push({ from: a, to: b });
      }
    }

    function inferRole(relationship) {
      const r = relationship.toLowerCase();
      if (r === "parent" || r === "grandparent" || r === "great-grandparent") return "ancestor";
      if (r === "child" || r === "grandchild" || r === "great-grandchild") return "descendant";
      if (r === "spouse") return "spouse";
      if (r === "sibling") return "sibling";
      if (r === "uncle" || r === "aunt") return "uncle/aunt";
      if (r === "nephew" || r === "niece") return "nephew/niece";
      if (r === "cousin") return "cousin";
      return "family";
    }

    while (queue.length > 0) {
      const { key, depth } = queue.shift();
      
      if (visited.has(key)) continue;
      visited.add(key);

      const rels = getRelationsForTemplate(key);

      for (const rel of rels) {
        const relType = (rel.relationship || "").toLowerCase();
        const otherKey = extractRelatedTemplate(rel);
        if (!otherKey) continue;

        if (!nodes.has(otherKey)) {
          nodes.add(otherKey);
          nodeRoles.set(otherKey, inferRole(relType));
        }

        if (key === centerKey && relType === "child") {
          directChildren.add(otherKey);
        }

        if (relType === "parent") {
          addParentEdge(otherKey, key);
        } else if (relType === "child") {
          addParentEdge(key, otherKey);
        } else if (relType === "spouse") {
          addSpouseEdge(key, otherKey);
        }

        if (depth + 1 <= maxDepth && !visited.has(otherKey)) {
          queue.push({ key: otherKey, depth: depth + 1 });
        }
      }
    }

    return { nodes, parentEdges, spouseEdges, nodeRoles, directChildren };
  }

  function elbowPath(x1, y1, x2, y2) {
    const midY = (y1 + y2) / 2;
    return `M ${x1} ${y1} L ${x1} ${midY} L ${x2} ${midY} L ${x2} ${y2}`;
  }

  function assignRoles(closure, subject) {
    const parentsOf = new Map(), childrenOf = new Map(), spousesOf = new Map();
    const add = (m, k, v) => { if (!m.has(k)) m.set(k, new Set()); m.get(k).add(v); };
    closure.parentEdges.forEach((e) => { add(childrenOf, e.from, e.to); add(parentsOf, e.to, e.from); });
    closure.spouseEdges.forEach((e) => { add(spousesOf, e.from, e.to); add(spousesOf, e.to, e.from); });
    const walk = (start, next) => {
      const seen = new Set(), stack = [start];
      while (stack.length) (next.get(stack.pop()) || []).forEach((n) => { if (!seen.has(n)) { seen.add(n); stack.push(n); } });
      return seen;
    };
    const ancestors = walk(subject, parentsOf);
    const descendants = walk(subject, childrenOf);
    const mySpouses = spousesOf.get(subject) || new Set();
    const siblings = new Set();
    (parentsOf.get(subject) || []).forEach((p) => (childrenOf.get(p) || []).forEach((c) => { if (c !== subject) siblings.add(c); }));
    const uncles = new Set();
    ancestors.forEach((a) => (parentsOf.get(a) || []).forEach((gp) => (childrenOf.get(gp) || []).forEach((c) => { if (!ancestors.has(c) && c !== subject) uncles.add(c); })));
    siblings.forEach((s) => uncles.delete(s));
    const nephews = new Set();
    siblings.forEach((s) => walk(s, childrenOf).forEach((d) => nephews.add(d)));
    const cousins = new Set();
    uncles.forEach((u) => walk(u, childrenOf).forEach((d) => cousins.add(d)));
    const inLaws = new Set();
    [siblings, uncles, nephews, cousins, descendants, ancestors].forEach((grp) => grp.forEach((m) => (spousesOf.get(m) || []).forEach((s) => inLaws.add(s))));
    mySpouses.forEach((s) => inLaws.delete(s));
    closure.nodes.forEach((k) => {
      let r = "family";
      if (k === subject) r = "self";
      else if (ancestors.has(k)) r = "ancestor";
      else if (descendants.has(k)) r = "descendant";
      else if (mySpouses.has(k)) r = "spouse";
      else if (siblings.has(k)) r = "sibling";
      else if (uncles.has(k)) r = "uncle/aunt";
      else if (nephews.has(k)) r = "nephew/niece";
      else if (cousins.has(k)) r = "cousin";
      else if (inLaws.has(k)) r = "in-law";
      closure.nodeRoles.set(k, r);
    });
  }

  function labelFor(role) {
    const labels = {
      "self": "Self",
      "ancestor": "Ancestor",
      "descendant": "Descendant",
      "spouse": "Spouse",
      "sibling": "Sibling",
      "uncle/aunt": "Uncle/Aunt",
      "nephew/niece": "Nephew/Niece",
      "cousin": "Cousin",
      "in-law": "In-law",
      "family": "Relative"
    };
    return labels[role] || "Relative";
  }

  function renderFamilyTreeDagre(hostEl, char) {
    if (!hostEl || !char || !window.dagre) return;

    hostEl.innerHTML = "";

    // Inject styles
    if (!document.getElementById('ft-dagre-styles')) {
      const style = document.createElement('style');
      style.id = 'ft-dagre-styles';
      style.textContent = `
        .ft-controls {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
          padding: 8px 12px;
          background: var(--paper-deep);
          border: 1px solid var(--line-strong);
          border-radius: 6px;
          width: fit-content;
        }
        .ft-zoom-btn {
          width: 32px;
          height: 32px;
          border: 1px solid var(--line-strong);
          border-radius: 4px;
          background: var(--paper-light);
          color: var(--ink);
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s ease;
        }
        .ft-zoom-btn:hover {
          background: #fff8e6;
          border-color: var(--seal);
        }
        .ft-zoom-level {
          font-size: 0.8rem;
          color: var(--ink-soft);
          min-width: 45px;
          text-align: center;
          font-family: monospace;
        }
        .ft-wrapper {
          overflow: auto;
          max-height: min(82vh, 920px);
          cursor: grab;
          touch-action: pan-x pan-y;
          border: 1px solid var(--line-strong);
          border-radius: 8px;
          background: var(--paper-deep);
        }
        .ft-canvas {
          position: relative;
          transform-origin: top left;
        }
        .ft-links {
          position: absolute;
          top: 0;
          left: 0;
          pointer-events: none;
          overflow: visible;
        }
        .ft-links path {
          stroke: var(--tree-line);
          stroke-width: 2;
          fill: none;
        }
        .ft-links path[data-edge="spouse"] {
          stroke-width: 4;
          stroke: var(--tree-line);
        }
        .ft-nodes {
          position: relative;
        }
        
        /* Node card - FIXED positioning */
        .ftd-node {
          position: absolute;
          width: 124px;
          transform: translate(-50%, -50%);
          text-decoration: none;
          color: inherit;
          display: block;
        }
        .ftd-card {
          border-radius: 8px;
          border: 1px solid var(--line-strong);
          background: var(--paper-light);
          box-shadow: 0 4px 10px rgba(70,45,15,0.22);
          overflow: hidden;
          transition: border-color 0.15s, box-shadow 0.15s;
        }
        .ftd-node:hover .ftd-card {
          border-color: var(--seal);
          box-shadow: 0 6px 14px rgba(70,45,15,0.32);
        }
        .ftd-label {
          display: block;
          text-align: center;
          font-family: 'Cinzel', serif;
          font-size: 0.58rem;
          font-weight: 600;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: var(--seal-dark);
          background: var(--paper-deep);
          padding: 5px 8px;
          border-bottom: 1px solid var(--line-strong);
        }
        .ftd-portrait {
          width: 100%;
          height: 86px;
          background-color: var(--paper-deep);
          background-size: cover;
          background-position: center top;
        }
        .ftd-portrait.no-portrait {
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--paper-deep);
        }
        .ftd-portrait.no-portrait::after {
          content: "?";
          font-family: 'Cinzel', serif;
          font-size: 2rem;
          color: var(--ink-faint);
        }
        .ftd-name {
          padding: 8px;
          text-align: center;
          font-size: 0.75rem;
          line-height: 1.2;
          color: var(--ink);
          background: var(--paper-light);
        }
        .ftd-name-alt {
          display: block;
          font-size: 0.65rem;
          opacity: 0.7;
          margin-top: 2px;
        }
        .ftd-node.is-missing {
          opacity: 0.72;
        }
        .ftd-node.is-missing .ftd-card { border-style: dashed; }
        .ftd-node.is-self .ftd-card {
          border: 2px solid var(--seal);
          box-shadow: 0 0 0 3px rgba(163,35,29,.28), 0 6px 14px rgba(70,45,15,0.32);
        }
        .ftd-node.is-self .ftd-label { background: var(--seal); color: #f8e9d0; }
        .ft-wrapper.is-panning { cursor: grabbing; user-select: none; }
        .ftd-node.is-missing .ftd-card {
          cursor: default;
        }
      `;
      document.head.appendChild(style);
    }

    // Create controls
    const controls = document.createElement("div");
    controls.className = "ft-controls";
    controls.innerHTML = `
      <button class="ft-zoom-btn" data-zoom="in" title="Zoom In">+</button>
      <button class="ft-zoom-btn" data-zoom="out" title="Zoom Out">−</button>
      <button class="ft-zoom-btn" data-zoom="reset" title="Actual size">⟲</button>
      <button class="ft-zoom-btn" data-zoom="fit" title="Show the whole tree" aria-label="Show the whole tree" style="width:auto;padding:0 10px;font-size:.75rem">Fit all</button>
      <span class="ft-zoom-level">100%</span>
    `;
    hostEl.appendChild(controls);

    // Create wrapper
    const wrapper = document.createElement("div");
    wrapper.className = "ft-wrapper";
    hostEl.appendChild(wrapper);

    // Create canvas
    const canvas = document.createElement("div");
    canvas.className = "ft-canvas";

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.classList.add("ft-links");

    const nodesLayer = document.createElement("div");
    nodesLayer.className = "ft-nodes";

    canvas.appendChild(svg);
    canvas.appendChild(nodesLayer);
    wrapper.appendChild(canvas);

    const center = char.key;
    const closure = buildFamilyClosure(center, MAX_DEPTH);

    assignRoles(closure, center);

    if (closure.nodes.size <= 1) {
      hostEl.innerHTML = '<div class="ft-empty">No known family relationships for this character.</div>';
      return;
    }

    // ---- Layout -------------------------------------------------------------------------------
    // Couples are laid out as ONE unit (spouses side by side), so spouses can never overlap other cards.
    // Dagre places the units by generation; we then expand each unit into its member cards.
    const NODE_W = 124;
    const NODE_H = 160;
    const COUPLE_GAP = 22;
    const PAD = 60;

    // 1. group spouses into units (connected components of the spouse relation)
    const spouseAdj = new Map();
    closure.spouseEdges.forEach((e) => {
      if (!spouseAdj.has(e.from)) spouseAdj.set(e.from, new Set());
      if (!spouseAdj.has(e.to)) spouseAdj.set(e.to, new Set());
      spouseAdj.get(e.from).add(e.to);
      spouseAdj.get(e.to).add(e.from);
    });
    const hasParentInTree = new Set(closure.parentEdges.map((e) => e.to));
    const unitOf = new Map(); // member key -> unit
    const units = [];
    closure.nodes.forEach((k) => {
      if (unitOf.has(k)) return;
      const members = [];
      const stack = [k];
      while (stack.length) {
        const m = stack.pop();
        if (unitOf.has(m) || !closure.nodes.has(m)) continue;
        unitOf.set(m, null);
        members.push(m);
        (spouseAdj.get(m) || []).forEach((s) => stack.push(s));
      }
      // spouses on the left, the family member (has parents / is the subject) on the right
      const score = (m) => (m === center ? 2 : hasParentInTree.has(m) ? 1 : 0);
      members.sort((a, b) => score(a) - score(b));
      const unit = { id: `u${units.length}`, members, width: members.length * NODE_W + (members.length - 1) * COUPLE_GAP };
      members.forEach((m) => unitOf.set(m, unit));
      units.push(unit);
    });

    // 2. dagre on the units
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: "TB", nodesep: 28, ranksep: 90, edgesep: 12, marginx: 0, marginy: 0 });
    g.setDefaultEdgeLabel(() => ({}));
    units.forEach((u) => g.setNode(u.id, { width: u.width, height: NODE_H }));
    const unitEdges = new Set();
    const connected = new Set();
    closure.parentEdges.forEach((e) => {
      const a = unitOf.get(e.from), b = unitOf.get(e.to);
      if (!a || !b || a === b) return;
      const id = `${a.id}>${b.id}`;
      if (unitEdges.has(id)) return;
      unitEdges.add(id);
      connected.add(a.id); connected.add(b.id);
      g.setEdge(a.id, b.id, {}, id);
    });
    dagre.layout(g);

    // 3. unit positions; units with no parent/child link (e.g. a sibling listed without shared parents)
    //    are placed on the subject's row instead of floating at the top
    const unitPos = new Map();
    units.forEach((u) => { const n = g.node(u.id); unitPos.set(u.id, { x: n.x, y: n.y }); });
    const centreUnit = unitOf.get(center);
    const loose = units.filter((u) => !connected.has(u.id) && u !== centreUnit);
    if (loose.length && centreUnit) {
      const rowY = unitPos.get(centreUnit.id).y;
      let right = -Infinity;
      units.forEach((u) => { if (Math.abs(unitPos.get(u.id).y - rowY) < 1) right = Math.max(right, unitPos.get(u.id).x + u.width / 2); });
      loose.forEach((u) => {
        right += 36 + u.width / 2;
        unitPos.set(u.id, { x: right, y: rowY });
        right += u.width / 2;
      });
    }

    // 4. member card centres
    const positions = {};
    units.forEach((u) => {
      const p = unitPos.get(u.id);
      const left = p.x - u.width / 2;
      u.members.forEach((m, i) => {
        positions[m] = { x: left + NODE_W / 2 + i * (NODE_W + COUPLE_GAP), y: p.y };
      });
    });

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    Object.values(positions).forEach((p) => {
      minX = Math.min(minX, p.x - NODE_W / 2);
      minY = Math.min(minY, p.y - NODE_H / 2);
      maxX = Math.max(maxX, p.x + NODE_W / 2);
      maxY = Math.max(maxY, p.y + NODE_H / 2);
    });
    if (!isFinite(minX)) { minX = 0; minY = 0; maxX = 400; maxY = 300; }

    const W = Math.ceil(maxX - minX + PAD * 2);
    const H = Math.ceil(maxY - minY + PAD * 2);
    canvas.style.width = `${W}px`;
    canvas.style.height = `${H}px`;
    svg.setAttribute("width", String(W));
    svg.setAttribute("height", String(H));
    nodesLayer.style.width = `${W}px`;
    nodesLayer.style.height = `${H}px`;
    const cx = (p) => p.x - minX + PAD;
    const cy = (p) => p.y - minY + PAD;

    // ---- Nodes --------------------------------------------------------------------------------
    function prettyKey(key) {
      const tail = key.replace(/^.*?template_/, "");
      const skip = new Set(["historical", "generated", "ancestral", "hero", "romance", "earth", "wood", "water", "fire", "metal"]);
      return tail.split("_").filter((w) => w && !skip.has(w)).map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ") || tail;
    }

    closure.nodes.forEach((key) => {
      const pos = positions[key];
      if (!pos) return;
      const c = getCharacterByTemplate(key);
      const name = c?.display_name || prettyKey(key);
      const alt = c?.display_name_alt || "";
      const portraitUrl = getDetailsPortraitUrl(key);
      const role = closure.nodeRoles.get(key) || "family";
      const isMissing = !c;

      const el = document.createElement(c && key !== center ? "a" : "div");
      el.className = `ftd-node${isMissing ? " is-missing" : ""}${key === center ? " is-self" : ""}`;
      if (c && key !== center) el.href = `character.html?key=${encodeURIComponent(key)}`;
      el.style.left = `${cx(pos)}px`;
      el.style.top = `${cy(pos)}px`;

      el.innerHTML = `
        <div class="ftd-card">
          <span class="ftd-label">${escapeHtml(labelFor(role))}</span>
          <div class="ftd-portrait ${portraitUrl ? "" : "no-portrait"}"
               ${portraitUrl ? `style="background-image: url('${escapeHtml(portraitUrl)}')"` : ""}></div>
          <div class="ftd-name">
            ${escapeHtml(name)}
            ${alt ? `<span class="ftd-name-alt">${escapeHtml(alt)}</span>` : ""}
          </div>
        </div>
      `;
      nodesLayer.appendChild(el);
    });

    // ---- Edges --------------------------------------------------------------------------------
    function addPath(d, kind) {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      path.dataset.edge = kind;
      svg.appendChild(path);
    }

    // couples: a short bar between neighbouring cards
    units.forEach((u) => {
      for (let i = 0; i + 1 < u.members.length; i++) {
        const a = positions[u.members[i]], b = positions[u.members[i + 1]];
        const y = cy(a);
        addPath(`M ${cx(a) + NODE_W / 2} ${y} L ${cx(b) - NODE_W / 2} ${y}`, "spouse");
      }
    });

    // parent -> child: children hang from the midpoint of a couple, or from a single parent's card
    const parentsOf = new Map();
    closure.parentEdges.forEach((e) => {
      if (!positions[e.from] || !positions[e.to]) return;
      if (!parentsOf.has(e.to)) parentsOf.set(e.to, []);
      parentsOf.get(e.to).push(e.from);
    });
    parentsOf.forEach((parents, child) => {
      const byUnit = new Map();
      parents.forEach((p) => {
        const u = unitOf.get(p);
        if (!byUnit.has(u)) byUnit.set(u, []);
        byUnit.get(u).push(p);
      });
      const childPos = positions[child];
      byUnit.forEach((ps) => {
        const xs = ps.map((p) => cx(positions[p]));
        const x1 = (Math.min(...xs) + Math.max(...xs)) / 2;
        const isCouple = ps.length > 1;
        const y1 = cy(positions[ps[0]]) + (isCouple ? 0 : NODE_H / 2 - 8);
        const y2 = cy(childPos) - NODE_H / 2 + 6;
        addPath(elbowPath(x1, y1, cx(childPos), y2), "parent");
      });
    });

    // Add hint
    const hint = document.createElement("div");
    hint.className = "ft-hint";
    hint.textContent = `Showing ${closure.nodes.size} family members. Drag to pan; use the buttons or Ctrl+scroll to zoom.`;
    hostEl.insertBefore(hint, controls);

    // Zoom functionality
    let currentZoom = 1;
    const MIN_ZOOM = 0.2;
    const MAX_ZOOM = 2;
    const ZOOM_STEP = 0.15;

    function updateZoom(newZoom) {
      currentZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newZoom));
      canvas.style.transform = `scale(${currentZoom})`;
      // transform doesn't change layout size: trim the unscaled overflow so zooming out leaves no dead space
      canvas.style.marginRight = `${-W * (1 - currentZoom)}px`;
      canvas.style.marginBottom = `${-H * (1 - currentZoom)}px`;
      // modest trees need no vertical scrolling: size the panel to the scaled tree (capped to the viewport)
      wrapper.style.maxHeight = `${Math.min(Math.round(H * currentZoom) + 2, 920, Math.round(window.innerHeight * 0.82))}px`;
      controls.querySelector(".ft-zoom-level").textContent = `${Math.round(currentZoom * 100)}%`;
    }

    function centreOnSelf() {
      const cp = positions[center];
      if (!cp) return;
      const cx = ((cp.x - minX) + PAD) * currentZoom, cy = ((cp.y - minY) + PAD) * currentZoom;
      wrapper.scrollLeft = Math.max(0, cx - wrapper.clientWidth / 2);
      const wantTop = cy - wrapper.clientHeight * 0.4;
      // keep the oldest generation in view whenever the subject's row is already visible; only scroll for very tall trees
      wrapper.scrollTop = (cy + (NODE_H / 2) * currentZoom + 24 <= wrapper.clientHeight) ? 0 : Math.max(0, wantTop);
    }
    // readable start (never below 60%); the Fit button shows the whole tree whatever the size
    function fitToWidth(minZoom = 0.6) {
      const w = wrapper.clientWidth || 800;
      updateZoom(Math.max(minZoom, Math.min(1, w / W)));
    }

    controls.addEventListener("click", (e) => {
      const btn = e.target.closest(".ft-zoom-btn");
      if (!btn) return;
      const action = btn.dataset.zoom;
      if (action === "in") updateZoom(currentZoom + ZOOM_STEP);
      else if (action === "out") updateZoom(currentZoom - ZOOM_STEP);
      else if (action === "reset") { updateZoom(1); centreOnSelf(); }
      else if (action === "fit") { fitToWidth(0.2); if (W * currentZoom <= wrapper.clientWidth) wrapper.scrollLeft = 0; else centreOnSelf(); }
    });

    wrapper.addEventListener("wheel", (e) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
        updateZoom(currentZoom + delta);
      }
    }, { passive: false });

    let pan = null;
    wrapper.addEventListener("pointerdown", (e) => {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      pan = { x: e.clientX, y: e.clientY, sl: wrapper.scrollLeft, st: wrapper.scrollTop, moved: false };
    });
    window.addEventListener("pointermove", (e) => {
      if (!pan) return;
      const dx = e.clientX - pan.x, dy = e.clientY - pan.y;
      if (!pan.moved && Math.abs(dx) + Math.abs(dy) < 5) return;
      pan.moved = true;
      wrapper.classList.add("is-panning");
      wrapper.scrollLeft = pan.sl - dx;
      wrapper.scrollTop = pan.st - dy;
    });
    window.addEventListener("pointerup", () => {
      if (pan && pan.moved) wrapper.addEventListener("click", (ev) => ev.preventDefault(), { capture: true, once: true });
      wrapper.classList.remove("is-panning");
      pan = null;
    });

    // initial view: fit to the panel, centred on this character
    fitToWidth();
    centreOnSelf();
  }

  window.renderFamilyTreeDagre = renderFamilyTreeDagre;
})();
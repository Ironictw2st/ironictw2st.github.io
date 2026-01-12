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
      "family": "Family"
    };
    return labels[role] || "Family";
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
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          width: fit-content;
        }
        .ft-zoom-btn {
          width: 32px;
          height: 32px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 4px;
          background: rgba(255, 255, 255, 0.08);
          color: rgba(255, 255, 255, 0.85);
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s ease;
        }
        .ft-zoom-btn:hover {
          background: rgba(255, 255, 255, 0.15);
          border-color: rgba(255, 255, 255, 0.35);
        }
        .ft-zoom-level {
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.65);
          min-width: 45px;
          text-align: center;
          font-family: monospace;
        }
        .ft-wrapper {
          overflow: auto;
          max-height: 70vh;
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 8px;
          background: linear-gradient(180deg, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.10) 100%);
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
          stroke: rgba(255,255,255,0.35);
          stroke-width: 2;
          fill: none;
        }
        .ft-links path[data-edge="spouse"] {
          stroke-dasharray: 6 4;
          stroke: rgba(255,255,255,0.25);
        }
        .ft-nodes {
          position: relative;
        }
        
        /* Node card - FIXED positioning */
        .ftd-node {
          position: absolute;
          width: 140px;
          transform: translate(-50%, -50%);
          text-decoration: none;
          color: inherit;
          display: block;
        }
        .ftd-card {
          border-radius: 8px;
          border: 1px solid rgba(255,255,255,0.16);
          background: rgba(0,0,0,0.45);
          box-shadow: 0 12px 24px rgba(0,0,0,0.50);
          overflow: hidden;
          transition: border-color 0.15s, box-shadow 0.15s;
        }
        .ftd-node:hover .ftd-card {
          border-color: rgba(255,255,255,0.30);
          box-shadow: 0 0 20px rgba(255,255,255,0.08), 0 12px 24px rgba(0,0,0,0.55);
        }
        .ftd-label {
          display: block;
          text-align: center;
          font-family: 'Cinzel', serif;
          font-size: 0.58rem;
          font-weight: 600;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: #b48eff;
          background: rgba(0,0,0,0.6);
          padding: 5px 8px;
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .ftd-portrait {
          width: 100%;
          height: 100px;
          background-color: #0a0a0c;
          background-size: cover;
          background-position: center top;
        }
        .ftd-portrait.no-portrait {
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
        }
        .ftd-portrait.no-portrait::after {
          content: "?";
          font-family: 'Cinzel', serif;
          font-size: 2rem;
          color: rgba(255,255,255,0.4);
        }
        .ftd-name {
          padding: 8px;
          text-align: center;
          font-size: 0.75rem;
          line-height: 1.2;
          color: rgba(255,255,255,0.85);
          background: rgba(0,0,0,0.3);
        }
        .ftd-name-alt {
          display: block;
          font-size: 0.65rem;
          opacity: 0.7;
          margin-top: 2px;
        }
        .ftd-node.is-missing {
          opacity: 0.5;
        }
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
      <button class="ft-zoom-btn" data-zoom="reset" title="Reset">⟲</button>
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

    if (closure.nodes.size <= 1) {
      hostEl.innerHTML = '<div class="ft-empty">No known family relationships for this character.</div>';
      return;
    }

    // Build Dagre graph - exclude ALL spouses from dagre layout
    const g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({
      rankdir: "TB",
      nodesep: 60,
      ranksep: 110,
      edgesep: 15
    });
    g.setDefaultEdgeLabel(() => ({}));

    const NODE_W = 140;
    const NODE_H = 180;

    // Find all characters who are spouses (will be positioned manually)
    const allSpouseKeys = new Set();
    const spouseOf = new Map(); // spouseKey -> partnerKey (the one in dagre)
    
    closure.spouseEdges.forEach(e => {
      // For each spouse pair, we need to decide which one goes in Dagre
      // The one with parent edges (children) stays in Dagre, the other is a "satellite"
      const aHasChildren = closure.parentEdges.some(pe => pe.from === e.from);
      const bHasChildren = closure.parentEdges.some(pe => pe.from === e.to);
      const aHasParents = closure.parentEdges.some(pe => pe.to === e.from);
      const bHasParents = closure.parentEdges.some(pe => pe.to === e.to);
      
      // Prefer to keep the one with more connections in Dagre
      const aConnections = (aHasChildren ? 1 : 0) + (aHasParents ? 1 : 0);
      const bConnections = (bHasChildren ? 1 : 0) + (bHasParents ? 1 : 0);
      
      if (aConnections >= bConnections) {
        // b is the satellite spouse
        if (!allSpouseKeys.has(e.from)) { // Don't make someone a satellite if they're already primary
          allSpouseKeys.add(e.to);
          spouseOf.set(e.to, e.from);
        }
      } else {
        // a is the satellite spouse
        if (!allSpouseKeys.has(e.to)) {
          allSpouseKeys.add(e.from);
          spouseOf.set(e.from, e.to);
        }
      }
    });

    // Add non-spouse nodes to Dagre
    closure.nodes.forEach((k) => {
      if (!allSpouseKeys.has(k)) {
        g.setNode(k, { width: NODE_W, height: NODE_H });
      }
    });

    // Add parent edges
    closure.parentEdges.forEach((e, i) => {
      if (!allSpouseKeys.has(e.from) && !allSpouseKeys.has(e.to)) {
        g.setEdge(e.from, e.to, { type: "parent" }, `p${i}`);
      }
    });

    // Layout
    dagre.layout(g);

    // Get positions from Dagre
    const positions = {};
    g.nodes().forEach((id) => {
      const n = g.node(id);
      if (n) {
        positions[id] = { x: n.x, y: n.y };
      }
    });

    // Position spouses to the LEFT of their partner
    const SPOUSE_OFFSET_X = NODE_W + 30;
    allSpouseKeys.forEach((spouseKey) => {
      const partnerKey = spouseOf.get(spouseKey);
      const partnerPos = positions[partnerKey];
      if (partnerPos) {
        // Check if there are already spouses positioned for this partner
        let offsetMultiplier = 1;
        allSpouseKeys.forEach((otherSpouse) => {
          if (otherSpouse !== spouseKey && spouseOf.get(otherSpouse) === partnerKey) {
            if (positions[otherSpouse]) {
              offsetMultiplier++;
            }
          }
        });
        
        positions[spouseKey] = {
          x: partnerPos.x - (SPOUSE_OFFSET_X * offsetMultiplier),
          y: partnerPos.y
        };
      }
    });

    // Align direct children of center to same Y
    const centerPos = positions[center];
    if (centerPos && closure.directChildren.size > 0) {
      let childY = null;
      closure.directChildren.forEach((childKey) => {
        if (positions[childKey] && childY === null) {
          childY = positions[childKey].y;
        }
      });
      if (childY !== null) {
        closure.directChildren.forEach((childKey) => {
          if (positions[childKey]) {
            positions[childKey].y = childY;
          }
        });
      }
    }

    // Compute bounds
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    Object.values(positions).forEach((p) => {
      minX = Math.min(minX, p.x - NODE_W / 2);
      minY = Math.min(minY, p.y - NODE_H / 2);
      maxX = Math.max(maxX, p.x + NODE_W / 2);
      maxY = Math.max(maxY, p.y + NODE_H / 2);
    });

    if (!isFinite(minX)) {
      minX = 0; minY = 0; maxX = 400; maxY = 300;
    }

    const PAD = 100;
    const W = Math.ceil(maxX - minX + PAD * 2);
    const H = Math.ceil(maxY - minY + PAD * 2);

    canvas.style.width = `${W}px`;
    canvas.style.height = `${H}px`;
    svg.setAttribute("width", String(W));
    svg.setAttribute("height", String(H));
    nodesLayer.style.width = `${W}px`;
    nodesLayer.style.height = `${H}px`;

    // Render nodes
    closure.nodes.forEach((key) => {
      const pos = positions[key];
      if (!pos) return;

      const x = (pos.x - minX) + PAD;
      const y = (pos.y - minY) + PAD;

      const c = getCharacterByTemplate(key);
      const name = c?.display_name || key.replace(/^.*template_/, "").replace(/_/g, " ");
      const alt = c?.display_name_alt || "";
      const portraitUrl = getDetailsPortraitUrl(key);
      const role = closure.nodeRoles.get(key) || "family";
      const isMissing = !c;

      const el = document.createElement(c ? "a" : "div");
      el.className = `ftd-node${isMissing ? " is-missing" : ""}`;
      if (c) {
        el.href = `character.html?key=${encodeURIComponent(key)}`;
      }
      el.style.left = `${x}px`;
      el.style.top = `${y}px`;

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

    // Draw edges
    // Parent edges
    closure.parentEdges.forEach((e) => {
      const fromPos = positions[e.from];
      const toPos = positions[e.to];
      if (!fromPos || !toPos) return;

      const x1 = (fromPos.x - minX) + PAD;
      const y1 = (fromPos.y - minY) + PAD + (NODE_H / 2) - 20;
      const x2 = (toPos.x - minX) + PAD;
      const y2 = (toPos.y - minY) + PAD - (NODE_H / 2) + 10;

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", elbowPath(x1, y1, x2, y2));
      path.dataset.edge = "parent";
      svg.appendChild(path);
    });

    // Spouse edges (horizontal lines)
    closure.spouseEdges.forEach((e) => {
      const fromPos = positions[e.from];
      const toPos = positions[e.to];
      if (!fromPos || !toPos) return;

      const x1 = (fromPos.x - minX) + PAD;
      const y1 = (fromPos.y - minY) + PAD;
      const x2 = (toPos.x - minX) + PAD;
      const y2 = (toPos.y - minY) + PAD;

      // Horizontal connector at same Y level
      const avgY = (y1 + y2) / 2;
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", `M ${x1} ${avgY} L ${x2} ${avgY}`);
      path.dataset.edge = "spouse";
      svg.appendChild(path);
    });

    // Add hint
    const hint = document.createElement("div");
    hint.className = "ft-hint";
    hint.textContent = `Showing ${closure.nodes.size} family members. Use controls or Ctrl+scroll to zoom.`;
    hostEl.insertBefore(hint, controls);

    // Zoom functionality
    let currentZoom = 1;
    const MIN_ZOOM = 0.2;
    const MAX_ZOOM = 2;
    const ZOOM_STEP = 0.15;

    function updateZoom(newZoom) {
      currentZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newZoom));
      canvas.style.transform = `scale(${currentZoom})`;
      controls.querySelector(".ft-zoom-level").textContent = `${Math.round(currentZoom * 100)}%`;
    }

    controls.addEventListener("click", (e) => {
      const btn = e.target.closest(".ft-zoom-btn");
      if (!btn) return;
      const action = btn.dataset.zoom;
      if (action === "in") updateZoom(currentZoom + ZOOM_STEP);
      else if (action === "out") updateZoom(currentZoom - ZOOM_STEP);
      else if (action === "reset") updateZoom(1);
    });

    wrapper.addEventListener("wheel", (e) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
        updateZoom(currentZoom + delta);
      }
    }, { passive: false });
  }

  window.renderFamilyTreeDagre = renderFamilyTreeDagre;
})();
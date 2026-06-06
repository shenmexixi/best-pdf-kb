# Mind Map Standard Template

## Usage

All `<YEAR>-<short_title>-reading.html` files MUST use this exact mind map implementation for visual consistency. Only the `mindmapData` object content changes per paper.

## Interaction Design

- **Initial state**: Root + branch labels visible. All leaf nodes COLLAPSED (hidden).
- **Click branch**: Expands/collapses that branch's leaf nodes
- **展开全部**: Shows all leaf nodes
- **收起全部**: Hides all leaf nodes (back to initial state)
- **放大/缩小**: Scale canvas
- **重置视图**: Reset zoom and pan
- **Drag**: Pan canvas by dragging empty area

## Required HTML Structure

```html
<h2 id="s2">2. 全文交互思维导图</h2>
<p>点击蓝色分支节点可展开/收起子内容，拖拽空白区域可平移画布。</p>
<div class="mindmap-container">
  <div class="mindmap-controls">
    <button onclick="expandAll()">展开全部</button>
    <button onclick="collapseAll()">收起全部</button>
    <button onclick="resetView()">重置视图</button>
    <button onclick="zoomIn()">放大</button>
    <button onclick="zoomOut()">缩小</button>
  </div>
  <div id="mindmap-canvas"></div>
</div>
```

## Required CSS (include in `<style>`)

```css
.mindmap-container { background: var(--card-bg); border: 1px solid var(--border); border-radius: 6px; padding: 1rem; margin: 1.5rem 0; overflow: hidden; position: relative; }
.mindmap-controls { display: flex; gap: 0.5rem; margin-bottom: 0.8rem; flex-wrap: wrap; }
.mindmap-controls button { padding: 0.3rem 0.7rem; border: 1px solid var(--border); border-radius: 4px; background: var(--card-bg); cursor: pointer; font-size: 0.82rem; transition: background 0.2s; }
.mindmap-controls button:hover { background: #eaf2f8; }
#mindmap-canvas { width: 100%; min-height: 420px; position: relative; cursor: grab; }
#mindmap-canvas:active { cursor: grabbing; }
.node { position: absolute; background: var(--card-bg); border: 1.5px solid var(--border); border-radius: 6px; padding: 0.4rem 0.7rem; font-size: 0.8rem; max-width: 210px; word-wrap: break-word; cursor: pointer; transition: box-shadow 0.2s, transform 0.15s; user-select: none; line-height: 1.4; }
.node:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.15); transform: translateY(-1px); }
.node.root { background: var(--primary); color: white; font-weight: 600; border-color: var(--primary); font-size: 0.9rem; max-width: 180px; }
.node.branch { background: #eaf2f8; border-color: var(--secondary); font-weight: 500; cursor: pointer; }
.node.branch.collapsed::after { content: " ▶"; color: var(--accent); font-weight: bold; font-size: 0.7rem; }
.node.branch.expanded::after { content: " ▼"; color: var(--secondary); font-weight: bold; font-size: 0.7rem; }
.node.leaf { background: #fffdf5; border-color: #e2d8b0; font-size: 0.76rem; }
svg.connections { position: absolute; top: 0; left: 0; pointer-events: none; }
```

## Required JavaScript Template

```javascript
// === MIND MAP (standard template — initial state: collapsed) ===
const mindmapData = {
  text: "PAPER_SHORT_TITLE",
  cls: "root",
  children: [
    // 6 branches recommended: 研究问题 / 方法设计 / 实验设计 / 核心结果 / 可解释性或分析 / 讨论与后续
    {
      text: "研究问题", cls: "branch",
      children: [
        { text: "leaf text here", cls: "leaf" },
        // 3-5 leaves per branch
      ]
    },
    // ... more branches
  ]
};

let scale = 1, panX = 0, panY = 0;
let isDragging = false, dragStartX, dragStartY;
// CRITICAL: Initialize ALL branches as collapsed (true = collapsed)
let nodeStates = {};
(function initCollapsed() {
  mindmapData.children.forEach(function(_, i) { nodeStates[String(i)] = true; });
})();

function renderMindmap() {
  const canvas = document.getElementById('mindmap-canvas');
  canvas.innerHTML = '';
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.classList.add('connections');
  canvas.appendChild(svg);

  let branchY = 20;
  const branchGap = 30;
  const rootX = 40, rootY = 200;

  const rootEl = makeNode(mindmapData.text, rootX, rootY, mindmapData.cls, 'root');
  canvas.appendChild(rootEl);

  mindmapData.children.forEach(function(branch, bi) {
    const bId = String(bi);
    const bx = 270;
    const by = branchY;
    const isCollapsed = !!nodeStates[bId];
    const bEl = makeNode(branch.text, bx, by, branch.cls + (isCollapsed ? ' collapsed' : ' expanded'), bId);
    canvas.appendChild(bEl);
    drawCurve(svg, rootX + 150, rootY + 14, bx, by + 14);

    if (!isCollapsed && branch.children) {
      branch.children.forEach(function(child, ci) {
        const cx = 500;
        const cy = by + ci * branchGap;
        const cEl = makeNode(child.text, cx, cy, child.cls || 'leaf', bId + '_' + ci);
        canvas.appendChild(cEl);
        drawCurve(svg, bx + 170, by + 14, cx, cy + 12);
      });
      branchY += Math.max(80, branch.children.length * branchGap + 20);
    } else {
      branchY += 50;
    }
  });

  const totalH = Math.max(420, branchY + 40);
  canvas.style.height = totalH + 'px';
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', totalH);
  canvas.style.transform = 'scale(' + scale + ') translate(' + panX + 'px,' + panY + 'px)';
}

function makeNode(text, x, y, cls, id) {
  var d = document.createElement('div');
  d.className = 'node ' + (cls || '');
  d.style.left = x + 'px';
  d.style.top = y + 'px';
  d.textContent = text;
  d.dataset.nid = id;
  d.addEventListener('click', function(e) { e.stopPropagation(); toggleNode(id); });
  return d;
}

function drawCurve(svg, x1, y1, x2, y2) {
  var p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  var mx = (x1 + x2) / 2;
  p.setAttribute('d', 'M' + x1 + ',' + y1 + ' C' + mx + ',' + y1 + ' ' + mx + ',' + y2 + ' ' + x2 + ',' + y2);
  p.setAttribute('stroke', '#b3d9ff');
  p.setAttribute('stroke-width', '1.5');
  p.setAttribute('fill', 'none');
  svg.appendChild(p);
}

function toggleNode(id) {
  // Only toggle branch nodes (single digit IDs), not leaves
  if (id.indexOf('_') === -1 && id !== 'root') {
    nodeStates[id] = !nodeStates[id];
    renderMindmap();
  }
}
function expandAll() { nodeStates = {}; renderMindmap(); }
function collapseAll() { mindmapData.children.forEach(function(_, i) { nodeStates[String(i)] = true; }); renderMindmap(); }
function resetView() { scale = 1; panX = 0; panY = 0; renderMindmap(); }
function zoomIn() { scale = Math.min(2.5, scale + 0.2); renderMindmap(); }
function zoomOut() { scale = Math.max(0.4, scale - 0.2); renderMindmap(); }

(function() {
  var c = document.getElementById('mindmap-canvas');
  c.addEventListener('mousedown', function(e) {
    if (e.target.classList.contains('node')) return;
    isDragging = true; dragStartX = e.clientX - panX; dragStartY = e.clientY - panY;
  });
  document.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    panX = e.clientX - dragStartX; panY = e.clientY - dragStartY;
    c.style.transform = 'scale(' + scale + ') translate(' + panX + 'px,' + panY + 'px)';
  });
  document.addEventListener('mouseup', function() { isDragging = false; });
  // Mouse wheel zoom
  c.addEventListener('wheel', function(e) {
    e.preventDefault();
    if (e.deltaY < 0) { scale = Math.min(2.5, scale + 0.1); }
    else { scale = Math.max(0.4, scale - 0.1); }
    c.style.transform = 'scale(' + scale + ') translate(' + panX + 'px,' + panY + 'px)';
  });
})();

renderMindmap();
```

## What changes per paper

ONLY the `mindmapData` object content. The rendering engine, CSS, HTML structure, and controls are IDENTICAL across all papers.

## Content guidelines for mindmapData

- Root node: paper short title + year
- 6 branches recommended:
  1. 研究问题 (3-4 leaves)
  2. 方法设计 (4-5 leaves — key architectural choices)
  3. 实验设计 (3-5 leaves — datasets, evaluation modes, baselines)
  4. 核心结果 (4-5 leaves — key findings with direction)
  5. 可解释性/分析 (3-4 leaves — if applicable, otherwise merge into results)
  6. 讨论与后续 (3-5 leaves — limitations + downstream work)
- Leaf text: concise, max ~25 Chinese characters
- Do not nest deeper than 2 levels (root → branch → leaf)
- All leaf nodes use `cls: "leaf"`

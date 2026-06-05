# Mind Map Standard Template

## Usage

All comprehensive_reader.html files MUST use this exact mind map implementation for visual consistency. Only the `mindmapData` object content changes per paper.

## Required HTML Structure

```html
<h2 id="s2">2. 全文交互思维导图</h2>
<p>下面的交互式思维导图总结了全文的主要论证结构，点击分支节点可展开/收起子内容。</p>
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
.mindmap-container { background: var(--card-bg); border: 1px solid var(--border); border-radius: 6px; padding: 1rem; margin: 1.5rem 0; overflow: auto; }
.mindmap-controls { display: flex; gap: 0.5rem; margin-bottom: 0.8rem; flex-wrap: wrap; }
.mindmap-controls button { padding: 0.3rem 0.7rem; border: 1px solid var(--border); border-radius: 4px; background: var(--card-bg); cursor: pointer; font-size: 0.82rem; }
.mindmap-controls button:hover { background: #eaf2f8; }
#mindmap-canvas { width: 100%; min-height: 520px; position: relative; overflow: auto; cursor: grab; }
#mindmap-canvas:active { cursor: grabbing; }
.node { position: absolute; background: var(--card-bg); border: 1.5px solid var(--border); border-radius: 6px; padding: 0.35rem 0.65rem; font-size: 0.78rem; max-width: 200px; word-wrap: break-word; cursor: pointer; transition: box-shadow 0.2s; user-select: none; line-height: 1.4; }
.node:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
.node.root { background: var(--primary); color: white; font-weight: 600; border-color: var(--primary); font-size: 0.85rem; max-width: 160px; }
.node.branch { background: #eaf2f8; border-color: var(--secondary); font-weight: 500; }
.node.collapsed::after { content: " +"; color: var(--accent); font-weight: bold; }
svg.connections { position: absolute; top: 0; left: 0; pointer-events: none; }
```

## Required JavaScript Template

```javascript
// === MIND MAP (standard template) ===
const mindmapData = {
  text: "PAPER_SHORT_TITLE",
  cls: "root",
  children: [
    // 6 branches recommended: 研究问题 / 方法设计 / 实验设计 / 核心结果 / 可解释性或分析 / 讨论与后续
    {
      text: "研究问题", cls: "branch",
      children: [
        { text: "leaf text here", cls: "" },
        // 3-5 leaves per branch
      ]
    },
    // ... more branches
  ]
};

let scale = 1, panX = 0, panY = 0;
let isDragging = false, dragStartX, dragStartY;
let nodeStates = {};

function renderMindmap() {
  const canvas = document.getElementById('mindmap-canvas');
  canvas.innerHTML = '';
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.classList.add('connections');
  canvas.appendChild(svg);

  let branchY = 15;
  const branchGap = 28;

  const rootEl = makeNode(mindmapData.text, 40, 240, mindmapData.cls, 'root');
  canvas.appendChild(rootEl);

  mindmapData.children.forEach(function(branch, bi) {
    const bId = String(bi);
    const bx = 260;
    const by = branchY;
    const bEl = makeNode(branch.text, bx, by, branch.cls, bId);
    canvas.appendChild(bEl);
    drawCurve(svg, 185, 255, bx, by + 14);

    if (!nodeStates[bId] && branch.children) {
      branch.children.forEach(function(child, ci) {
        const cx = 480;
        const cy = by + ci * branchGap;
        const cEl = makeNode(child.text, cx, cy, child.cls, bId + '_' + ci);
        canvas.appendChild(cEl);
        drawCurve(svg, bx + 160, by + 14, cx, cy + 10);
      });
      branchY += Math.max(80, branch.children.length * branchGap + 15);
    } else {
      if (branch.children && branch.children.length > 0) bEl.classList.add('collapsed');
      branchY += 45;
    }
  });

  const totalH = Math.max(520, branchY + 30);
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
  d.addEventListener('click', function() { toggleNode(id); });
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

function toggleNode(id) { nodeStates[id] = !nodeStates[id]; renderMindmap(); }
function expandAll() { nodeStates = {}; renderMindmap(); }
function collapseAll() { mindmapData.children.forEach(function(_, i) { nodeStates[String(i)] = true; }); renderMindmap(); }
function resetView() { scale = 1; panX = 0; panY = 0; renderMindmap(); }
function zoomIn() { scale = Math.min(2, scale + 0.15); renderMindmap(); }
function zoomOut() { scale = Math.max(0.5, scale - 0.15); renderMindmap(); }

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

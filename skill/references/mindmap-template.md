# Mind Map Standard Template

## Usage

All `<YEAR>-<short_title>-reading.html` files MUST use this exact mind map implementation for visual consistency. Only the `mindmapData` object content changes per paper.

## Interaction Design

- **Initial state**: Root + Level-1 branches visible. Level-2 and deeper COLLAPSED.
- **Click any node with children**: Toggle expand/collapse of its children
- **展开全部**: Recursively expand all nodes
- **收起全部**: Collapse to initial state (only root + L1)
- **放大/缩小/重置**: Scale canvas
- **Drag**: Pan canvas by dragging empty area
- **Mouse wheel**: Zoom in/out

## Data Structure (supports 3-4 levels)

```javascript
const mindmapData = {
  text: "Paper Title (2021)",
  children: [
    {
      text: "研究问题",
      children: [
        {
          text: "核心挑战",
          children: [
            { text: "EEG信号非平稳且信噪比极低" },
            { text: "小样本导致深度模型过拟合" }
          ]
        },
        { text: "现有方法准确率仅70-80%" }
      ]
    },
    // ... more branches
  ]
};
```

## Required HTML Structure

```html
<h2 id="s2">2. 全文交互思维导图</h2>
<p>点击节点可展开/收起子内容，拖拽空白区域平移画布，滚轮缩放。</p>
<div class="mindmap-container">
  <div class="mindmap-controls">
    <button onclick="mmExpandAll()">展开全部</button>
    <button onclick="mmCollapseAll()">收起全部</button>
    <button onclick="mmResetView()">重置视图</button>
    <button onclick="mmZoomIn()">放大</button>
    <button onclick="mmZoomOut()">缩小</button>
  </div>
  <div class="mindmap-viewport">
    <div id="mindmap-canvas"></div>
  </div>
</div>
```

## Required CSS (include in `<style>`)

```css
.mindmap-container {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2f7 100%);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  margin: 1.5rem 0;
}
.mindmap-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  position: relative;
  z-index: 10;
}
.mindmap-controls button {
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 5px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.mindmap-controls button:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
.mindmap-viewport {
  overflow: hidden;
  border-radius: 6px;
  background: white;
  border: 1px solid var(--border);
  position: relative;
  height: 460px;
  z-index: 1;
}
#mindmap-canvas {
  min-height: 450px;
  position: absolute;
  top: 0;
  left: 0;
  cursor: grab;
  transform-origin: 0 0;
}
#mindmap-canvas:active { cursor: grabbing; }
.mm-node {
  position: absolute;
  border-radius: 6px;
  padding: 0.45rem 0.8rem;
  font-size: 0.78rem;
  max-width: 220px;
  min-height: 1.6em;
  word-wrap: break-word;
  overflow-wrap: break-word;
  cursor: pointer;
  user-select: none;
  line-height: 1.5;
  transition: box-shadow 0.2s, transform 0.15s;
  white-space: normal;
  display: flex;
  align-items: center;
}
.mm-node:hover {
  box-shadow: 0 3px 12px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}
/* Level 0: Root */
.mm-node.L0 {
  background: linear-gradient(135deg, #2c5282, #3b82f6);
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  max-width: 200px;
  border: none;
  box-shadow: 0 2px 8px rgba(44,82,130,0.3);
}
/* Level 1: Main branches */
.mm-node.L1 {
  background: #eef4fd;
  border: 1.5px solid #93c5fd;
  font-weight: 600;
  color: #1e40af;
  font-size: 0.82rem;
}
/* Level 2: Sub-branches */
.mm-node.L2 {
  background: #fef9e7;
  border: 1.5px solid #f6d860;
  color: #92400e;
  font-size: 0.78rem;
}
/* Level 3: Leaves */
.mm-node.L3 {
  background: #f0fdf4;
  border: 1px solid #86efac;
  color: #166534;
  font-size: 0.75rem;
  max-width: 200px;
}
/* Level 4+: Deep leaves */
.mm-node.L4 {
  background: #fdf4ff;
  border: 1px solid #e9d5ff;
  color: #6b21a8;
  font-size: 0.73rem;
}
.mm-node.has-children { cursor: pointer; }
.mm-node.has-children.collapsed::after {
  content: " \25B6";
  font-size: 0.65rem;
  opacity: 0.7;
  margin-left: 0.2rem;
}
.mm-node.has-children.expanded::after {
  content: " \25BC";
  font-size: 0.65rem;
  opacity: 0.5;
  margin-left: 0.2rem;
}
svg.mm-lines {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}
```

## Required JavaScript Template

```javascript
// === MIND MAP (multi-level, collapsed-by-default) ===
const mindmapData = {
  text: "PAPER_SHORT_TITLE",
  children: [
    // Structure: root -> L1 branches -> L2 sub-branches -> L3 leaves -> L4 (optional)
    // See content guidelines below
  ]
};

(function() {
  let scale = 1, panX = 0, panY = 0;
  let isDragging = false, startX, startY;
  const expanded = new Set(); // Track expanded node paths

  // Initial state: expand only root (level 0) children are visible but collapsed
  // Nothing in expanded set = only root's direct children shown, all collapsed

  const LEVEL_X = [30, 240, 450, 650, 820]; // X positions per level
  const V_GAP = 44; // Vertical gap between sibling nodes (enough for 2-line text)

  function render() {
    const canvas = document.getElementById('mindmap-canvas');
    canvas.innerHTML = '';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('mm-lines');
    canvas.appendChild(svg);

    const layout = computeLayout(mindmapData, '0', 0);
    drawNode(canvas, svg, layout);

    const bounds = getBounds(layout);
    canvas.style.height = (bounds.maxY + 60) + 'px';
    canvas.style.width = Math.max(900, bounds.maxX + 60) + 'px';
    svg.setAttribute('width', canvas.style.width);
    svg.setAttribute('height', canvas.style.height);
    canvas.style.transform = 'scale(' + scale + ') translate(' + panX + 'px,' + panY + 'px)';
  }

  function computeLayout(node, path, level) {
    const hasKids = node.children && node.children.length > 0;
    const isExpanded = level === 0 || expanded.has(path);
    const result = {
      text: node.text,
      path: path,
      level: level,
      x: LEVEL_X[Math.min(level, LEVEL_X.length - 1)],
      y: 0, // computed later
      hasChildren: hasKids,
      expanded: isExpanded,
      children: []
    };

    if (hasKids && isExpanded) {
      result.children = node.children.map(function(child, i) {
        return computeLayout(child, path + '.' + i, level + 1);
      });
    }
    return result;
  }

  // Assign Y positions recursively
  function assignY(node, startY) {
    if (node.children.length === 0) {
      node.y = startY;
      return startY + V_GAP;
    }
    let y = startY;
    node.children.forEach(function(child) {
      y = assignY(child, y);
    });
    // Center parent among children
    node.y = (node.children[0].y + node.children[node.children.length - 1].y) / 2;
    return y;
  }

  function getBounds(node) {
    let maxX = node.x + 200, maxY = node.y + 30;
    node.children.forEach(function(child) {
      const b = getBounds(child);
      maxX = Math.max(maxX, b.maxX);
      maxY = Math.max(maxY, b.maxY);
    });
    return { maxX: maxX, maxY: maxY };
  }

  function drawNode(canvas, svg, node) {
    const el = document.createElement('div');
    el.className = 'mm-node L' + Math.min(node.level, 4);
    if (node.hasChildren) {
      el.classList.add('has-children');
      el.classList.add(node.expanded ? 'expanded' : 'collapsed');
    }
    el.style.left = node.x + 'px';
    el.style.top = node.y + 'px';
    el.textContent = node.text;
    el.addEventListener('click', function(e) {
      e.stopPropagation();
      if (node.hasChildren) {
        if (expanded.has(node.path)) { expanded.delete(node.path); }
        else { expanded.add(node.path); }
        render();
      }
    });
    canvas.appendChild(el);

    node.children.forEach(function(child) {
      drawLine(svg, node.x + 180, node.y + 14, child.x, child.y + 14);
      drawNode(canvas, svg, child);
    });
  }

  function drawLine(svg, x1, y1, x2, y2) {
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const mx = (x1 + x2) / 2;
    p.setAttribute('d', 'M' + x1 + ',' + y1 + ' C' + mx + ',' + y1 + ' ' + mx + ',' + y2 + ' ' + x2 + ',' + y2);
    p.setAttribute('stroke', '#cbd5e1');
    p.setAttribute('stroke-width', '1.5');
    p.setAttribute('fill', 'none');
    svg.appendChild(p);
  }

  // Public API
  window.mmExpandAll = function() {
    (function addAll(node, path) {
      if (node.children) {
        expanded.add(path);
        node.children.forEach(function(c, i) { addAll(c, path + '.' + i); });
      }
    })(mindmapData, '0');
    render();
  };
  window.mmCollapseAll = function() { expanded.clear(); render(); };
  window.mmResetView = function() { scale = 1; panX = 0; panY = 0; render(); };
  window.mmZoomIn = function() { scale = Math.min(2.5, scale + 0.2); render(); };
  window.mmZoomOut = function() { scale = Math.max(0.3, scale - 0.2); render(); };

  // Pan & zoom
  var vp = document.querySelector('.mindmap-viewport');
  vp.addEventListener('mousedown', function(e) {
    if (e.target.classList.contains('mm-node')) return;
    isDragging = true; startX = e.clientX - panX; startY = e.clientY - panY;
    e.preventDefault();
  });
  document.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    panX = e.clientX - startX; panY = e.clientY - startY;
    document.getElementById('mindmap-canvas').style.transform =
      'scale(' + scale + ') translate(' + panX + 'px,' + panY + 'px)';
  });
  document.addEventListener('mouseup', function() { isDragging = false; });
  vp.addEventListener('wheel', function(e) {
    e.preventDefault();
    scale += (e.deltaY < 0 ? 0.1 : -0.1);
    scale = Math.max(0.3, Math.min(2.5, scale));
    document.getElementById('mindmap-canvas').style.transform =
      'scale(' + scale + ') translate(' + panX + 'px,' + panY + 'px)';
  });

  // Initial render
  var layout = computeLayout(mindmapData, '0', 0);
  assignY(layout, 20);
  render = function() {
    var layout = computeLayout(mindmapData, '0', 0);
    assignY(layout, 20);
    var canvas = document.getElementById('mindmap-canvas');
    canvas.innerHTML = '';
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('mm-lines');
    canvas.appendChild(svg);
    drawNode(canvas, svg, layout);
    var bounds = getBounds(layout);
    canvas.style.height = (bounds.maxY + 60) + 'px';
    canvas.style.width = Math.max(900, bounds.maxX + 60) + 'px';
    svg.setAttribute('width', canvas.style.width);
    svg.setAttribute('height', canvas.style.height);
    canvas.style.transform = 'scale(' + scale + ') translate(' + panX + 'px,' + panY + 'px)';
  };
  render();
})();
```

## What changes per paper

ONLY the `mindmapData` object content. The rendering engine, CSS, HTML structure, and controls are IDENTICAL across all papers.

## Content guidelines for mindmapData

### Required depth: 3-4 levels

| Level | Role | Count | Example |
|:---:|------|:---:|------|
| 0 | Root | 1 | "EEG-inception (2021)" |
| 1 | Main branches | 6 | "方法设计" |
| 2 | Sub-topics | 3-5 per branch | "多尺度卷积模块" |
| 3 | Specific details | 2-4 per sub-topic | "kernel 25/75/125对应0.1s/0.3s/0.5s" |
| 4 | Optional deep detail | 0-2 | (only for complex mechanisms) |

### Recommended 6 branches with sub-structure:

```
Root
├── 研究问题
│   ├── 领域背景 → [具体挑战1, 具体挑战2]
│   ├── 现有方法不足 → [方法A局限, 方法B局限]
│   └── 本文目标 → [目标1, 目标2]
├── 方法设计
│   ├── 核心架构 → [模块A功能, 模块B功能, 模块间连接]
│   ├── 关键创新点 → [创新1原理, 创新2原理]
│   └── 数据策略 → [增强方法, 预处理]
├── 实验设计
│   ├── 数据集 → [数据集A参数, 数据集B参数]
│   ├── 评估指标 → [指标1, 指标2]
│   └── 对比基线 → [基线1, 基线2]
├── 核心结果
│   ├── 主实验 → [数据集A结果, 数据集B结果]
│   ├── 消融实验 → [因素1影响, 因素2影响]
│   └── 效率分析 → [计算开销, 推理速度]
├── 可解释性/分析
│   ├── 跨条件泛化 → [条件1, 条件2]
│   └── 机理解读 → [为什么有效, 失败案例]
└── 讨论与后续
    ├── 主要贡献 → [贡献1, 贡献2]
    ├── 局限性 → [局限1, 局限2]
    └── 未来方向 → [方向1, 方向2]
```

### Text rules:
- L1 nodes: 2-4 Chinese characters (topic name)
- L2 nodes: 4-10 Chinese characters (sub-topic)
- L3 nodes: 8-20 Chinese characters (specific point with key data)
- L4 nodes: 10-25 Chinese characters (detailed mechanism or number)
- Total nodes: 50-80 for a typical paper

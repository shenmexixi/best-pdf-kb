# Human HTML Reader Rules

## Final Artifact

```text
deliverables/comprehensive_reader.html
```

One polished local HTML file. No external CDN dependencies.

## Section Hierarchy

Use logical hierarchy. Recommended 5-7 top-level sections:

1. **论文身份与阅读导向** — metadata card, one-sentence summary, reading guide
2. **全文交互思维导图** — interactive SVG mind map (MUST use standard template)
3. **背景与核心研究问题** — what problem, why hard, what's missing
4. **方法与核心技术设计** — architecture, mechanism, design rationale
5. **实验设计与主要结果** — datasets, metrics, key findings
6. **图表深度解读** — interpretability, figure deep dive (or merge into §4-5)
7. **总结、术语表与延伸阅读** — takeaways, term glossary, future directions

Keep TOC to these top-level sections only. Nest figures under relevant section.

## Writing Rules (per style preset)

### All styles must include:
- What question each section answers
- The core intuition
- The technical mechanism
- Why the authors chose this design
- Which figure/experiment supports the point
- The takeaway

### For core technical designs, explain ALL of:
- Design motivation
- Input and output
- Mechanism
- Problem solved
- Correspondence to traditional methods
- Trade-off or limitation

### Style-specific adjustments:

**academic:** Formal language, precise numbers, full equations, cite specific sections/figures, no simplification of mathematical notation, standard domain terminology.

**technical:** Deep mechanism explanation, allow analogies to familiar systems, include implementation detail (hyperparameters, code structure), prefer concrete examples over abstract descriptions.

**popular:** Lead with intuition and analogy before technical detail, minimize jargon on first mention (explain inline), use progressive disclosure (simple→complex), more "why this matters" framing.

## Narrative Coherence (MANDATORY)

- Each top-level section opens with 1-2 sentence bridge from previous section
- Within sections: setup → mechanism → evidence → implication
- When presenting figures in sequence: explain what each new figure ADDS to the argument
- Experimental results must include "so what": not just "A > B" but WHY and WHAT IT MEANS
- Discussion connects back to earlier findings with explicit references
- No orphaned conclusions — every claim needs visible reasoning chain

## Figure Block Structure

Every figure MUST have:

```html
<div class="figure-block">
  <img src="../assets/figures/figure_XX.png" alt="[Figure label]">
  <p class="caption">[Original English caption]</p>
  <p class="caption-zh">[Chinese caption]</p>
  <div class="explanation">
    [Panel-by-panel or block-by-block explanation]
    [Explain axes, colors, labels, what it proves]
    [Confidence note if crop uncertain]
  </div>
</div>
```

For multi-panel figures, explain each panel separately:
- Panel (a): ...
- Panel (b): ...

## Interactive Mind Map

MUST use the EXACT template from `references/mindmap-template.md`. Only change `mindmapData` content.

Required behavior:
- Expand/collapse individual nodes
- Expand all / Collapse all / Reset
- Zoom in / Zoom out / Reset zoom
- Drag-to-pan canvas
- Text wrapping inside node boxes
- No external CDN dependency

Recommended 6 branches:
1. 研究问题 (3-4 leaves)
2. 方法设计 (4-5 leaves)
3. 实验设计 (3-5 leaves)
4. 核心结果 (4-5 leaves)
5. 可解释性/分析 (3-4 leaves, if applicable)
6. 讨论与后续 (3-5 leaves)

## Visual Style

- CSS variables for theming: `--primary`, `--secondary`, `--accent`, `--bg`, `--card-bg`, `--text`, `--border`
- Academic restrained interface
- Full-width readable content
- Cards for: paper metadata, technical breakdowns, result highlights
- `border-radius` ≤ 8px
- No decorative/marketing backgrounds
- All text fits inside containers (no overflow)

## Component Library

Use these CSS classes:

| Class | Purpose |
|-------|---------|
| `.meta-card` | Paper identity block |
| `.toc` | Table of contents |
| `.figure-block` | Figure + captions + explanation |
| `.tech-card` | Technical mechanism explanation |
| `.result-highlight` | Key quantitative result |
| `.formula` | Math formula display |
| `table` | Data comparison tables |
| `.mindmap-container` | Mind map wrapper |

## HTML Template Structure

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Paper short title] - 论文精读</title>
  <style>
    /* CSS variables + component styles */
  </style>
</head>
<body>
  <!-- Section 1: Identity -->
  <h1>[Chinese title]</h1>
  <div class="meta-card">...</div>
  <div class="toc">...</div>

  <!-- Section 2: Mind Map -->
  <h2>全文交互思维导图</h2>
  <div class="mindmap-container">...</div>

  <!-- Sections 3-6: Content -->
  ...

  <!-- Section 7: Summary -->
  ...

  <footer>图片来源: 本地提取的论文figure资源</footer>

  <script>
    // Mind map JS (from template)
  </script>
</body>
</html>
```

## Verification Checklist (before delivery)

- [ ] No `????` or Unicode replacement characters
- [ ] All image paths exist
- [ ] JavaScript passes syntax check (balanced braces/parens)
- [ ] TOC has only top-level sections (5-7)
- [ ] Every paper figure has a corresponding `<img>` tag
- [ ] Mind map canvas supports drag and zoom
- [ ] No "beginner" labels unless user requested
- [ ] Responsive layout works at different widths

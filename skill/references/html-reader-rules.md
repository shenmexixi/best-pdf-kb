# Human HTML Reader Rules

## Final Artifact

```text
deliverables/<YEAR>-<short_title>-reading.html
```

Naming rule: `<YEAR>-<short_title>-reading.html` where `<YEAR>` is publication year and `<short_title>` is a concise lowercase kebab-case identifier.
Examples: `2021-eeg-inception-reading.html`, `2025-super-adhesive-hydrogels-reading.html`

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

## Symbol and Encoding Rules (MANDATORY)

The HTML must display all symbols correctly. Follow these rules strictly:

### Mathematical symbols — use Unicode characters directly:
| Instead of | Use | Unicode |
|-----------|-----|---------|
| `>=` | ≥ | U+2265 |
| `<=` | ≤ | U+2264 |
| `!=` | ≠ | U+2260 |
| `~=` | ≈ | U+2248 |
| `+-` | ± | U+00B1 |
| `*` (multiply) | × | U+00D7 |
| `->` | → | U+2192 |
| `<-` | ← | U+2190 |
| `inf` | ∞ | U+221E |
| `sqrt` | √ | U+221A |
| `sum` | Σ | U+03A3 |
| `delta` | Δ/δ | U+0394/U+03B4 |
| `alpha` | α | U+03B1 |
| `beta` | β | U+03B2 |
| `theta` | θ | U+03B8 |
| `sigma` | σ | U+03C3 |
| `mu` | μ | U+03BC |

### Subscripts and superscripts — use HTML tags:
```html
x<sub>i</sub>     <!-- subscript: xᵢ -->
x<sup>2</sup>     <!-- superscript: x² -->
10<sup>-3</sup>   <!-- scientific: 10⁻³ -->
```

### Formulas — wrap in `.formula` class:
```html
<div class="formula">S<sub>aug</sub>(i) = S<sub>0</sub>(i) − S<sub>n</sub>(i) + S<sub>n</sub>(k)</div>
```

### Encoding safety:
- ALL HTML files MUST be written as UTF-8 with BOM (`\xEF\xBB\xBF` at start) or with `<meta charset="UTF-8">`
- When writing files with Python, ALWAYS use `encoding="utf-8"`: `Path(f).write_text(html, encoding="utf-8")`
- NEVER mix `print()` redirection for file writing on Windows (codepage corruption risk)
- After writing, run Step 8e encoding validation to detect garbled sequences
- If garbled text is found, regenerate that section — do NOT try to fix byte-by-byte

## Narrative Coherence (MANDATORY)

- Each top-level section opens with 1-2 sentence bridge from previous section
- Within sections: setup → mechanism → evidence → implication
- When presenting figures in sequence: explain what each new figure ADDS to the argument
- Experimental results must include "so what": not just "A > B" but WHY and WHAT IT MEANS
- Discussion connects back to earlier findings with explicit references
- No orphaned conclusions — every claim needs visible reasoning chain

## Long Document Adaptive Writing Strategy

The HTML reader must maintain quality regardless of paper length. Do NOT generate the entire HTML in one pass.

### Process:
1. **Outline first**: Generate a structured outline with 7 sections, key points per section, and figure assignments
2. **Write section by section**: Each section generated independently (2000-3000 Chinese characters)
3. **Assemble**: Concatenate sections, add header/footer/TOC/mind map
4. **Verify coherence**: Check transitions between sections, fix any gaps
5. **Inject base64 images**: Post-processing script replaces all `<img src="...">` with base64 data URIs

### Depth adaptation by paper length:
| Paper length | Sections | Per-section depth | Total HTML 中文字数 |
|:---:|:---:|------|------|
| ≤15 pages | 5-6 sections | 1500-2000 字 | ~10K 字 |
| 15-30 pages | 6-7 sections | 2000-3000 字 | ~15K 字 |
| 30-60 pages | 7 sections | 2500-3500 字 | ~20K 字 |
| 60+ pages | 7 sections | 3000-4000 字 | ~25K 字 |

### Content quality verification:
After writing, count Chinese characters in the HTML (excluding tags/scripts). If below the target range, the content is insufficient — go back and expand the weakest sections. A 17-page paper should have at minimum 8,000 中文字 of explanation content.

### Key rules for long papers:
- Never sacrifice depth for brevity — if a paper has 8 experiments, cover all 8
- Group related experiments under logical subsections rather than listing all sequentially
- Use more tech-cards and result-highlights for dense content
- Mind map may have more leaves per branch (5-6 instead of 3-4)
- Terms glossary should be comprehensive (15-25 terms)

## Figure Block Structure

During writing, use relative paths for figures. Base64 injection happens as a post-processing step (see workflow.md Step 8d).

**During writing (Step 8b):**
```html
<div class="figure-block">
  <img src="../assets/figures/figure_XX.jpg" alt="[Figure label]">
  <p class="caption">[Original English caption]</p>
  <p class="caption-zh">[Chinese caption]</p>
  <div class="explanation">
    [Panel-by-panel or block-by-block explanation]
    [Explain axes, colors, labels, what it proves]
    [Confidence note if crop uncertain]
  </div>
</div>
```

**After post-processing (Step 8d), the final HTML will have:**
```html
<img src="data:image/jpeg;base64,/9j/4AAQ..." alt="[Figure label]">
```

This two-phase approach ensures:
- Agent dedicates 100% of context to content quality during writing
- No base64 noise competes with the writing task
- Final HTML is still fully self-contained and portable

**How to package:**
```bash
python <skill-dir>/scripts/embed_html_images.py \
  deliverables/<YEAR>-<short_title>-reading.html \
  deliverables/<YEAR>-<short_title>-reading.html
```

Use the bundled script; do not rewrite the embedding logic. It validates all image references before writing, supports in-place packaging, and preserves the exact source image bytes.

**CRITICAL RULES:**
- NEVER use `<img src="../assets/figures/...">` or any file path in the final HTML
- EVERY `<img>` tag must use a `data:` URI
- The `assets/figures/` directory still stores the original crops for KB use, but the HTML must not reference them
- This ensures the HTML can be opened anywhere — emailed, uploaded, moved to another machine — without broken images

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

## Component Library (MANDATORY visual variety)

The HTML must use colored blocks and visual differentiation to break up prose and highlight key information. A good reader uses at minimum: 4+ tech-cards, 3+ result-highlights, and colored explanation blocks.

### Required CSS:

```css
:root {
  --primary: #2c5282;
  --secondary: #4a90d9;
  --accent: #e53e3e;
  --bg: #f7fafc;
  --card-bg: #ffffff;
  --text: #1a202c;
  --text-muted: #4a5568;
  --border: #e2e8f0;
}

.meta-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1.2rem; margin-bottom: 1.5rem; }
.toc { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.5rem; margin: 1.5rem 0; }
.figure-block { background: var(--card-bg); border: 1px solid var(--border); border-radius: 6px; padding: 1rem; margin: 1.5rem 0; }
.figure-block .explanation { background: #f8f9fa; border-left: 3px solid var(--secondary); padding: 0.8rem 1rem; margin-top: 0.8rem; font-size: 0.9rem; line-height: 1.7; }
.tech-card { background: #f0f7ff; border: 1px solid #bee3f8; border-radius: 6px; padding: 1rem; margin: 1rem 0; }
.tech-card h4 { color: var(--primary); margin-top: 0; margin-bottom: 0.5rem; }
.result-highlight { background: #fef9e7; border-left: 4px solid #f6ad55; padding: 0.8rem 1rem; margin: 1rem 0; border-radius: 0 6px 6px 0; }
.summary-box { background: #f0fff4; border: 1px solid #c6f6d5; border-radius: 6px; padding: 1rem; margin: 1rem 0; }
.formula { background: #f5f5f5; border: 1px solid var(--border); border-radius: 4px; padding: 0.6rem 1rem; margin: 0.8rem 0; font-family: monospace; text-align: center; }
```

### Component usage rules:

| Class | Color | When to use | Minimum count |
|-------|-------|-------------|:---:|
| `.meta-card` | White | Paper identity (title, authors, DOI, summary) | 1 |
| `.tech-card` | Light blue `#f0f7ff` | Each core technical mechanism/design choice | 4+ |
| `.result-highlight` | Light yellow `#fef9e7` | Key quantitative results (accuracy, speedup, etc.) | 3+ |
| `.summary-box` | Light green `#f0fff4` | Section takeaways, key conclusions | 2+ |
| `.figure-block .explanation` | Grey `#f8f9fa` + blue left border | Figure panel explanations | per figure |
| `.formula` | Grey `#f5f5f5` | Mathematical formulas or key equations | as needed |
| `.toc` | White | Table of contents | 1 |

### Example usage patterns:

**Tech-card** — one per major design choice:
```html
<div class="tech-card">
  <h4>多尺度并行卷积设计动机</h4>
  <p><strong>问题:</strong> EEG信号非平稳，单一时间窗口无法捕获全部频率特征。</p>
  <p><strong>方案:</strong> 并行使用25/75/125卷积核，对应250Hz下0.1s/0.3s/0.5s时间窗口。</p>
  <p><strong>效果:</strong> 同时提取theta/alpha/beta节律特征。</p>
</div>
```

**Result-highlight** — one per key finding:
```html
<div class="result-highlight">
  <p><strong>核心发现:</strong> 四分类准确率达88.39%，跨被试标准差仅7.1（较HS-CNN降低58%），单样本推理0.0215秒。</p>
</div>
```

**Summary-box** — section-end takeaway:
```html
<div class="summary-box">
  <p><strong>本节要点:</strong> EEG-inception通过物理采样率绑定的多尺度卷积核 + 残差模块，实现了端到端特征提取，无需人工预处理。</p>
</div>
```

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

  <footer>图片已内嵌为base64，本文件完全自包含，可独立打开。</footer>

  <script>
    // Mind map JS (from template)
  </script>
</body>
</html>
```

## Verification Checklist (before delivery)

### After Step 8c (content verification):
- [ ] Chinese character count meets target (≥8000 for 15-page paper, see depth table)
- [ ] No `????` or Unicode replacement characters
- [ ] Every paper figure has a corresponding `<img>` tag
- [ ] JavaScript passes syntax check (balanced braces/parens)
- [ ] TOC has only top-level sections (5-7)
- [ ] Mind map canvas supports drag and zoom
- [ ] No "beginner" labels unless user requested
- [ ] Responsive layout works at different widths

### After Step 8d (base64 injection):
- [ ] All `<img>` tags now use `data:` URIs (no external file paths remaining)
- [ ] HTML file is fully self-contained (opens correctly when moved to any location)
- [ ] File size reasonable (typically 1-5 MB depending on figure count)
- [ ] No "beginner" labels unless user requested
- [ ] Responsive layout works at different widths
- [ ] HTML file is fully self-contained (opens correctly when moved to any location)

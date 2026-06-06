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

**How to embed (Python):**
```python
import base64
from pathlib import Path

def embed_image(image_path: str) -> str:
    data = Path(image_path).read_bytes()
    b64 = base64.b64encode(data).decode()
    suffix = Path(image_path).suffix.lower()
    mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
    return f"data:{mime};base64,{b64}"
```

**How to embed (Bash):**
```bash
# Read image, convert to base64, output data URI
echo "data:image/png;base64,$(base64 -w0 assets/figures/figure_01.png)"
```

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

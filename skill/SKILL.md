---
name: best-pdf-kb
description: >
  Use when Codex needs to turn an academic PDF into a complete paper knowledge
  base and polished Chinese interactive HTML reader, or package an existing paper
  reader as a portable single-file HTML with embedded images.
---

# Best PDF Knowledge Base Builder

## Purpose

Turn one academic PDF into two coordinated outputs:

1. **Machine-readable KB** — structured metadata, text chunks with provenance, figure assets with VLM analysis, terminology, searchable SQLite index, and a dual-layer knowledge graph.
2. **Human-facing HTML reader** — a single polished Chinese interactive reader with logical section hierarchy, inline figure explanations, and an interactive mind-map canvas.

## Prerequisites

- **MinerU** (`magic-pdf`) installed: `pip install magic-pdf`
- **Python tools** included in this project under `tools/`:
  - `tools/pdf_figure_extractor/` — figure extraction + VLM analysis
  - `tools/pdf_text_summarizer/` — text summarization pipeline
  - `tools/pdf_knowledge_base/` — orchestrator
  - Usage: `sys.path.insert(0, "<project_root>")` then `from tools.pdf_knowledge_base import build_knowledge_base`
- **Python dependencies**: `pip install -r requirements.txt`
- **API access** via environment variables:
  - `PDF_KB_API_KEY` — API key for VLM/LLM calls
  - `PDF_KB_BASE_URL` — API endpoint (OpenAI-compatible)
  - `PDF_KB_MODEL` — model name (e.g., `gemini-2.5-flash`, `claude-sonnet-4-6`)

## Load References

Read these files as needed during execution:

- `references/workflow.md` — end-to-end 10-step process
- `references/machine-package.md` — file tree and schema definitions
- `references/html-reader-rules.md` — HTML writing rules, section hierarchy, figure blocks
- `references/mindmap-template.md` — EXACT mind map JS/CSS template (use verbatim)
- `references/review-agents.md` — dual-reviewer protocol (Domain Expert + Science Editor)
- `references/style-presets.md` — tone/depth customization options

Use this bundled tool instead of rewriting image-embedding code:

- `scripts/embed_html_images.py` — convert every local `<img>` reference into a base64 data URI and produce a portable HTML file

## Style Presets

Ask user which style to use (default: `academic`):

| Preset | Tone | Depth | Target |
|--------|------|-------|--------|
| `academic` | 正式、引用准确、不简化数学 | 深度完整 | 研究人员 |
| `technical` | 深度讲解、允许类比 | 机制为主 | 工程师 |
| `popular` | 先直觉再细节、大量类比 | 渐进式 | 跨学科/学生 |

## Workspace Contract

All work must live under a single paper folder:

```text
<workspace>/
  input/
  output/
  kb/
  assets/figures/
  assets/page_previews/
  deliverables/
  notes/
  README.md
```

Final user-facing artifact: `deliverables/<YEAR>-<short_title>-reading.html`

Naming rule: `<YEAR>` is the paper's publication year, `<short_title>` is a concise lowercase kebab-case paper identifier (e.g., `eeg-inception`, `super-adhesive-hydrogels`). Examples:
- `2021-eeg-inception-reading.html`
- `2025-super-adhesive-hydrogels-reading.html`

## Core Workflow (Summary)

1. Prepare workspace and copy PDF
2. Smoke test PDF (pages, text quality, figures)
3. Parse with MinerU → markdown + raw figures
4. Build text chunks (chunk_id, page, section, linked_figures, summary_zh)
5. Extract figures (MinerU + VLM analysis + panel splitting + 300DPI fallback)
6. Build KB files (chunks/figures/tables/terms/profile/index.sqlite)
7. Build knowledge graph (source layer + semantic layer)
8. Generate HTML reader (fixed template, multi-section, interactive mind map)
9. Technical verification
10. Dual-reviewer quality check → auto-fix → re-verify
11. Final response

See `references/workflow.md` for full step-by-step detail.

## Non-Negotiable Rules

- Never fabricate data, figure captions, or numeric claims
- Every chunk/node/edge must have provenance (page_id, chunk_id)
- **HTML must be self-contained** — during writing (Step 8b), use relative image paths; after assembly, run `scripts/embed_html_images.py` in Step 8d so every final `<img>` uses a base64 data URI.
- **Content depth**: Chinese character count must meet the target in the depth adaptation table (≥8000 for a 15-page paper). If below target, expand weakest sections.
- Mind map uses the EXACT template from `references/mindmap-template.md`
- HTML has 5-7 top-level sections, not flat headings
- Figures nested under relevant section, not a standalone gallery
- No mojibake (????) or Unicode replacement characters
- Review must produce structured issues with ID/severity/location/fix/source

## Quick Decision Tree

```
User says "read this PDF" or "build KB from PDF"
  → Is MinerU output available?
    → Yes: reuse it (skip Step 3)
    → No: run MinerU parsing
  → Does user specify style?
    → Yes: use that preset
    → No: default to "academic"
  → Does user want lightweight (KB only)?
    → Yes: skip Steps 8-10
    → No: full pipeline including HTML + review
```

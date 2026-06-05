---
name: best-pdf-kb
description: >
  Build a complete paper knowledge base + polished Chinese interactive HTML reader
  from an academic PDF. Combines MinerU parsing, VLM figure analysis, knowledge
  graph construction, and dual-reviewer quality check. Outputs machine-readable KB
  (chunks, figures, tables, terms, graph, SQLite) and one deliverable HTML reader
  with interactive mind map. Supports style presets (academic/technical/popular).
  Use when the user asks to read/analyze/explain a PDF paper, convert a paper
  into a knowledge base, extract all figures/tables, or produce a single deliverable
  HTML reader.
---

When invoked, first read `SKILL.md` from the skill directory (same directory as this file, or the installed skill location).
Treat that file as the governing workflow.

If the skill references supporting files (e.g., `references/workflow.md`), read them from the `references/` subdirectory relative to the skill location.

Available references:
- `references/workflow.md` — end-to-end 11-step process
- `references/machine-package.md` — file tree and schema definitions
- `references/html-reader-rules.md` — HTML writing rules
- `references/mindmap-template.md` — EXACT mind map implementation template
- `references/review-agents.md` — dual-reviewer protocol
- `references/style-presets.md` — tone/depth customization

## Configuration

The following environment variables configure the skill:
- `PDF_KB_API_KEY` — API key for VLM/LLM calls
- `PDF_KB_BASE_URL` — API endpoint (OpenAI-compatible)
- `PDF_KB_MODEL` — model name
- `PDF_KB_TOOLS_PATH` — (optional) path to Python tools directory for accelerated pipeline

## Usage

Create a workspace directory per paper. The skill will populate it with the standard structure defined in `references/machine-package.md`.

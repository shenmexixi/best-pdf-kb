# PDF-to-Knowledge-Base Workflow

## Step 1: Prepare Workspace

Create the paper folder structure:

```text
<workspace>/
  input/          ← original PDF
  output/         ← intermediate results, smoke test, reviews
  kb/             ← machine-readable knowledge base
  assets/
    figures/      ← high-quality figure crops
    page_previews/← rendered pages (optional)
  deliverables/   ← comprehensive_reader.html
  notes/          ← manual notes
  README.md
```

Copy or symlink the PDF to `input/`.

## Step 2: Smoke Test

Determine:
- Page count
- Selectable text vs scanned
- Figure count and complexity (multi-panel?)
- Caption extractability
- DOI/arXiv metadata availability

Save findings to `output/smoke_test.md`.

## Step 3: Parse with MinerU

Run MinerU (`magic-pdf`) to produce:
- Structured markdown with section headings
- Extracted images in a raw figures directory
- Layout analysis metadata

If MinerU output already exists (from prior runs), reuse it.

Fallback: If MinerU fails or is unavailable, use pymupdf for text extraction and 300 DPI page rendering for figures.

## Step 4: Build Text Chunks

From MinerU markdown, split into section-aware chunks:

```python
# Use tools/pdf_text_summarizer/section_splitter.py
sections = split_sections(markdown_path)
```

For each chunk, produce:
- `chunk_id`: stable ID (format: `p{page}_s{section}_c{seq}`)
- `page_start` / `page_end`: source page numbers
- `section`: section title
- `text`: original text (English)
- `summary_zh`: Chinese summary/rewrite
- `keywords`: 3-6 key terms
- `linked_figures`: figure IDs referenced in this chunk
- `linked_tables`: table IDs referenced
- `source_confidence`: high/medium/low

Then generate multi-level overall summary:
- `one_liner`: one sentence
- `abstract_summary`: 3-5 sentences
- `detailed_summary`: 3-4 paragraphs with bracketed subheadings
- `key_contributions`: list of 3-5 items
- `methodology`: methodology paragraph
- `main_findings`: list of 4-6 quantitative findings

Write `kb/chunks.jsonl` and store summary in `kb/paper_profile.json`.

## Step 5: Extract and Analyze Figures

### 5.1 Extraction (in priority order)

1. **MinerU bbox**: Use figure positions from MinerU layout analysis
2. **Caption-based crop**: Find captions in page text → locate figure region above → crop at PDF coordinates
3. **300 DPI render + manual region**: When methods 1-2 fail, render page at 300 DPI and crop the figure region
4. **Full-page render (last resort)**: Only when figure spans >60% of page. Mark `crop_confidence: "low"`

### 5.2 VLM Analysis

For each figure, call the VLM API:
```python
# Use tools/pdf_figure_extractor/figure_analyzer.py
analyzed = await analyze_figures(figures, sub_figures_map, vlm_backend)
```

Produce per-figure:
- `description`: what the figure shows
- `key_findings`: what conclusions it supports
- `data_summary`: quantitative info visible
- `tags`: searchable keywords
- `category`: architecture / result / diagram / method / table
- `importance`: high / medium / low

### 5.3 Panel Splitting

For multi-panel figures (a, b, c...):
```python
# Use tools/pdf_figure_extractor/panel_splitter.py
is_multi, sub_panels = await detect_and_split_panels(figure, vlm_backend)
```

Each sub-panel gets its own analysis.

### 5.4 Output

- `assets/figures/figure_XX.png` — one file per figure
- `assets/figures/figure_crops_manifest.json` — manifest with bbox, confidence, notes
- `assets/figures/figure_contact_sheet.png` — QA overview
- `kb/figures.jsonl` — machine-readable figure records
- `kb/tables.jsonl` — table records

## Step 6: Build KB Files

Create remaining knowledge base files:

- `kb/paper_profile.json` — metadata (see machine-package.md for schema)
- `kb/terms.json` — recurring technical terms with translations
- `kb/index.sqlite` — searchable SQLite FTS index (tables: chunks, figures, tables, terms)
- `kb/README.md` — KB usage guide

## Step 7: Build Knowledge Graph

Follow the dual-layer approach:

### 7.1 Source Graph (deterministic, no LLM needed)
Create nodes for: Paper, Sections, Chunks, Figures, Tables, Terms
Create edges: HAS_SECTION, HAS_CHUNK, MENTIONS_FIGURE, MENTIONS_TABLE, HAS_TERM, HAS_ASSET

### 7.2 Semantic Graph (schema-constrained, with provenance)
Extract: Concepts, Methods, ModelComponents, Datasets, Tasks, Metrics, Results, Claims, Limitations
Create edges: USES_COMPONENT, PART_OF, SOLVES, EVALUATED_ON, MEASURED_BY, OUTPERFORMS, SUPPORTS_CLAIM, HAS_LIMITATION, EXPLAINS, COMPARES_WITH

Every edge MUST have:
- evidence_text or evidence summary
- provenance (chunk_ids, figure_ids, pages)
- confidence level

### 7.3 Export
- `kb/graph/schema.json` — allowed types
- `kb/graph/nodes.jsonl` — canonical nodes
- `kb/graph/edges.jsonl` — canonical edges
- `kb/graph/graph.sqlite` — queryable
- `kb/graph/graph.graphml` — visualization
- `kb/graph/graph.ttl` — RDF export
- `kb/graph/extraction_report.md` — method and limitations

## Step 8: Generate HTML Reader

Follow `references/html-reader-rules.md` for the complete spec. Key points:

1. Use KB outputs as source data (chunks, figures, terms, graph)
2. Structure as 5-7 logical top-level sections
3. Embed interactive mind map using the EXACT template from `references/mindmap-template.md`
4. Every figure gets a figure-block (image + original caption + Chinese caption + explanation)
5. Apply the style preset (academic/technical/popular) to tone and depth
6. Include TOC, meta-card, tech-cards, result-highlights as appropriate
7. **Embed all images as base64 data URIs** — read each figure from `assets/figures/`, encode as base64, use `<img src="data:image/png;base64,...">`. The HTML must be fully self-contained (no external file references). This ensures it can be opened anywhere without broken images.

Write to `deliverables/comprehensive_reader.html`.

## Step 9: Technical Verification

Check:
- [ ] HTML file exists and is valid
- [ ] All `<img>` tags use base64 data URIs (no external file paths)
- [ ] At least 1 `<img>` per paper figure
- [ ] All JSON/JSONL files parse
- [ ] SQLite databases open
- [ ] Graph nodes/edges validate (no orphan references)
- [ ] JavaScript syntax valid (balanced braces)
- [ ] No `????` or Unicode replacement characters
- [ ] 5-7 top-level headings in HTML
- [ ] TOC links work

## Step 10: Dual-Reviewer Quality Check

Follow `references/review-agents.md`.

1. **Domain Expert** reviews: accuracy, depth, figure interpretation, result interpretation, missing content, terminology
2. **Science Editor** reviews: narrative, transitions, figure presentation, progressive disclosure, visual hierarchy, mind map

Both produce structured issue lists. Auto-fix all critical + major issues, then re-verify (Step 9).

## Step 11: Final Response

Report:
- Path to `deliverables/comprehensive_reader.html`
- Path to `kb/`
- Path to `kb/graph/`
- Path to `assets/figures/figure_contact_sheet.png`
- Any low-confidence crops or extraction caveats
- Verification summary
- Review verdict

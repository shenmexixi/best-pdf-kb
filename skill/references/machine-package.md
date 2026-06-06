# Machine-Readable Package Rules

## Required File Tree

```text
<paper folder>/
  input/
    original PDF
  output/
    smoke_test.md
    review_domain_expert.md
    review_science_editor.md
    full_text.txt (optional)
  kb/
    chunks.jsonl
    figures.jsonl
    tables.jsonl
    terms.json
    paper_profile.json
    index.sqlite
    summary.md
    mindmap.md
    graph/
      schema.json
      nodes.jsonl
      edges.jsonl
      graph.sqlite
      graph.graphml
      graph.ttl
      extraction_report.md
    README.md
  assets/
    figures/
      figure_01.png
      figure_02.png
      ...
      figure_crops_manifest.json
      figure_contact_sheet.png
    page_previews/
      (optional rendered pages)
  deliverables/
    <YEAR>-<short_title>-reading.html
  notes/
    (manual notes)
  README.md
```

## `kb/paper_profile.json`

```json
{
  "paper_id": "folder-safe-id",
  "title": "",
  "authors": [],
  "year": null,
  "journal_or_source": "",
  "doi": null,
  "arxiv": null,
  "pmid": null,
  "affiliations": [],
  "code_url": null,
  "keywords": [],
  "one_sentence_summary_zh": "",
  "summary": {
    "one_liner": "",
    "abstract_summary": "",
    "detailed_summary": "",
    "key_contributions": [],
    "methodology": "",
    "main_findings": []
  },
  "pdf_path": "input/source.pdf",
  "page_count": null,
  "extraction_summary": {
    "text_method": "MinerU | pymupdf",
    "figure_method": "MinerU + VLM + 300DPI fallback",
    "table_method": "MinerU | text-based",
    "limitations": []
  }
}
```

## `kb/chunks.jsonl`

One JSON object per line:

```json
{
  "chunk_id": "p001_s01_c001",
  "paper_id": "",
  "page_start": 1,
  "page_end": 1,
  "section": "Introduction",
  "text": "original text",
  "summary_zh": "中文摘要改写",
  "keywords": ["term1", "term2"],
  "linked_figures": ["figure_01"],
  "linked_tables": ["table_01"],
  "source_confidence": "high"
}
```

## `kb/figures.jsonl`

```json
{
  "figure_id": "figure_01",
  "label": "Figure 1",
  "page": 2,
  "asset_path": "assets/figures/figure_01.png",
  "caption_original": "",
  "caption_zh": "",
  "content_explanation_zh": "",
  "category": "architecture",
  "importance": "high",
  "tags": [],
  "related_chunks": ["p002_s03_c001"],
  "crop_confidence": "high",
  "sub_panels": [
    {
      "panel_id": "figure_01a",
      "label": "(a)",
      "asset_path": "assets/figures/figure_01a.png",
      "description_zh": ""
    }
  ],
  "notes": ""
}
```

## `kb/tables.jsonl`

```json
{
  "table_id": "table_01",
  "label": "Table 1",
  "page": 3,
  "asset_path": null,
  "caption_original": "",
  "caption_zh": "",
  "content_explanation_zh": "",
  "data_markdown": "| Col1 | Col2 |\n|---|---|\n| ... |",
  "related_chunks": [],
  "extraction_confidence": "medium"
}
```

## `kb/terms.json`

```json
{
  "terms": [
    {
      "term": "English term",
      "translation_zh": "中文翻译",
      "definition_zh": "中文定义",
      "first_seen_chunk": "p001_s01_c001",
      "aliases": []
    }
  ]
}
```

## `kb/index.sqlite`

Required tables:
- `chunks(chunk_id, page_start, page_end, section, text, summary_zh, keywords_json)`
- `figures(figure_id, label, page, asset_path, caption_original, caption_zh, content_explanation_zh, category, importance)`
- `tables(table_id, label, page, caption_original, caption_zh, data_markdown)`
- `terms(term, translation_zh, definition_zh, first_seen_chunk)`

Enable FTS5 on `chunks(text, summary_zh)` and `terms(term, translation_zh, definition_zh)`.

## `kb/summary.md`

Multi-level human-readable summary:

```markdown
# [One-liner title]

## Summary
[3-5 sentence abstract-level summary]

## Key Contributions
- [contribution 1]
- [contribution 2]
...

## Main Findings
- [finding 1 with numbers]
- [finding 2 with numbers]
...

## Methodology
[methodology paragraph]

## Detailed Summary
[3-4 paragraphs with 【bracketed subheadings】]
```

## `assets/figures/figure_crops_manifest.json`

```json
{
  "figures": [
    {
      "figure_id": "figure_01",
      "label": "Figure 1",
      "page": 2,
      "asset_path": "assets/figures/figure_01.png",
      "width": 2080,
      "height": 1020,
      "crop_method": "bbox | caption_based | render_crop | full_page",
      "crop_confidence": "high",
      "notes": ""
    }
  ]
}
```

## Knowledge Graph (see workflow.md Step 7)

Required in `kb/graph/`:
- `schema.json`: allowed node and edge types
- `nodes.jsonl`: all nodes with provenance
- `edges.jsonl`: all edges with provenance
- `graph.sqlite`: queryable local store
- `graph.graphml`: portable visualization format
- `graph.ttl`: RDF export
- `extraction_report.md`: method and limitations

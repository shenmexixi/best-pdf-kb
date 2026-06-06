# Best PDF Knowledge Base Builder

A Claude Code skill that transforms academic PDFs into structured knowledge bases + polished interactive Chinese HTML readers. Self-contained — all Python tools included.

## What It Does

Given a PDF paper, produces:
- **Machine-readable KB**: text chunks with provenance, figure analysis, terminology, knowledge graph, SQLite index
- **Human-facing HTML**: self-contained (base64 images), interactive mind map, inline figure explanations, academic styling, dual-reviewer quality check

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/shenmexixi/best-pdf-kb.git
cd best-pdf-kb
pip install -r requirements.txt
```

### 2. Register as Claude Code agent

```bash
cp agent-definition.md ~/.claude/agents/best-pdf-kb.md
# Edit paths in the file to match your local clone location
```

Or as a skill:
```bash
cp -r skill ~/.claude/skills/best-pdf-kb
```

### 3. Configure API access

```bash
export PDF_KB_API_KEY="your-api-key"
export PDF_KB_BASE_URL="https://your-api-endpoint/v1"
export PDF_KB_MODEL="gemini-2.5-flash"  # or any compatible model
```

### 4. Use it

In Claude Code, say:
```
Read this PDF and build a knowledge base: /path/to/paper.pdf
```

Or with a style preset:
```
Process this paper in popular style: /path/to/paper.pdf
```

## Output Structure

```
workspace/
├── input/              # Original PDF
├── kb/
│   ├── chunks.jsonl    # Text chunks with page/section provenance
│   ├── figures.jsonl   # Figure records with VLM analysis
│   ├── tables.jsonl    # Table records
│   ├── terms.json      # Technical terminology
│   ├── paper_profile.json
│   ├── index.sqlite    # Full-text search index
│   ├── summary.md      # Multi-level summary
│   ├── mindmap.md      # Mind map data
│   └── graph/          # Knowledge graph (JSONL + SQLite + GraphML + RDF)
├── assets/figures/     # High-quality figure crops
└── deliverables/
    └── 2021-eeg-inception-reading.html  # Self-contained HTML (base64 images)
```

## Key Features

- **Self-contained HTML**: All images base64-embedded, works anywhere without external files
- **Long document adaptive**: Sectional generation ensures depth for 10-page and 60-page papers alike
- **Style presets**: academic / technical / popular — controls tone, depth, and presentation
- **Python tools included**: `tools/` directory has the full pipeline (no external deps needed)

## Style Presets

| Preset | Target Audience | Tone |
|--------|----------------|------|
| `academic` (default) | Researchers | Formal, precise, full depth |
| `technical` | Engineers | Mechanism-focused, implementation detail |
| `popular` | Cross-disciplinary | Intuitive, progressive, analogy-rich |

## How It Works

1. Parse PDF with MinerU (fallback: pymupdf + 300 DPI rendering)
2. Split text into section-aware chunks with provenance (adaptive chunking for long sections)
3. Extract figures with VLM analysis + panel splitting
4. Build structured KB (chunks, figures, tables, terms, SQLite)
5. Construct dual-layer knowledge graph (source + semantic)
6. Generate HTML reader section-by-section (outline → write → assemble → verify)
7. Embed all images as base64 for portability
8. Run dual-reviewer quality check (Domain Expert + Science Editor)
9. Auto-fix issues and verify

## Quality

Evaluated on a 110-point rubric across 5 dimensions:
- Text extraction & understanding (25 pts)
- Figure extraction & explanation (30 pts)
- Knowledge base structure (20 pts)
- HTML presentation quality (25 pts)
- Review & revision quality (10 pts)

**Score: 104/110 (94.5%)** — tested on JNE and Nature papers.

## Project Structure

```
best-pdf-kb/
├── skill/              # Skill definition + references (for Claude Code)
├── tools/              # Python pipeline (figure extraction, summarization, KB builder)
├── agent-definition.md # Claude Code agent registration template
├── requirements.txt    # Python dependencies
├── docs/               # Installation guide + troubleshooting
├── README.md
└── LICENSE (MIT)
```

## Requirements

- Claude Code (or compatible AI coding assistant)
- Python 3.10+
- MinerU (`magic-pdf`) for PDF parsing
- An OpenAI-compatible API endpoint for VLM/LLM calls
- ~10-25 minutes per paper (depending on length and figure count)

## License

MIT

# Best PDF Knowledge Base Builder

A Claude Code skill that transforms academic PDFs into structured knowledge bases + polished interactive Chinese HTML readers.

## What It Does

Given a PDF paper, produces:
- **Machine-readable KB**: text chunks with provenance, figure analysis, terminology, knowledge graph, SQLite index
- **Human-facing HTML**: interactive mind map, inline figure explanations, academic styling, dual-reviewer quality check

## Quick Start

### 1. Install the skill

Copy the skill directory to your Claude Code skills folder:

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/best-pdf-kb.git

# Copy to Claude Code skills directory
cp -r best-pdf-kb/skill ~/.claude/skills/best-pdf-kb
```

Or register as an agent:
```bash
cp best-pdf-kb/agent-definition.md ~/.claude/agents/best-pdf-kb.md
```

Then edit the paths in `~/.claude/agents/best-pdf-kb.md` to match your local setup.

### 2. Install dependencies

- **MinerU** (`magic-pdf`): Follow [MinerU installation guide](https://github.com/opendatalab/MinerU)
- **Python packages**: `pymupdf`, `networkx`, `rdflib` (for graph exports)
- **API access**: Any OpenAI-compatible API endpoint (Gemini, Claude, etc.)

### 3. Configure environment variables

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
    └── comprehensive_reader.html  # Interactive HTML reader
```

## Style Presets

| Preset | Target Audience | Tone |
|--------|----------------|------|
| `academic` (default) | Researchers | Formal, precise, full depth |
| `technical` | Engineers | Mechanism-focused, implementation detail |
| `popular` | Cross-disciplinary | Intuitive, progressive, analogy-rich |

## How It Works

1. Parse PDF with MinerU (fallback: pymupdf + 300 DPI rendering)
2. Split text into section-aware chunks with provenance
3. Extract figures with VLM analysis + panel splitting
4. Build structured KB (chunks, figures, tables, terms, SQLite)
5. Construct dual-layer knowledge graph (source + semantic)
6. Generate interactive HTML reader with fixed mind map template
7. Run dual-reviewer quality check (Domain Expert + Science Editor)
8. Auto-fix issues and verify

## Quality

Evaluated on a 110-point rubric across 5 dimensions:
- Text extraction & understanding (25 pts)
- Figure extraction & explanation (30 pts)
- Knowledge base structure (20 pts)
- HTML presentation quality (25 pts)
- Review & revision quality (10 pts)

**Score: 104/110 (94.5%)** — tested on JNE and Nature papers.

## Requirements

- Claude Code (or compatible AI coding assistant)
- Python 3.10+
- MinerU (`magic-pdf`) for PDF parsing
- An OpenAI-compatible API endpoint for VLM/LLM calls
- ~10-25 minutes per paper (depending on length and figure count)

## License

MIT

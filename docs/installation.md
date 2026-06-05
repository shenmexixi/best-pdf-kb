# Installation Guide

## Prerequisites

### 1. MinerU (PDF Parser)

MinerU is used for high-quality PDF-to-markdown conversion with layout analysis.

```bash
pip install magic-pdf
# or follow: https://github.com/opendatalab/MinerU
```

Verify installation:
```bash
magic-pdf --version
```

### 2. Python Dependencies

```bash
pip install pymupdf networkx rdflib
```

### 3. API Access

You need an OpenAI-compatible API endpoint for VLM (vision-language model) and LLM calls. Options:

| Provider | Model | Cost |
|----------|-------|------|
| Google Gemini | gemini-2.5-flash | Low |
| Anthropic Claude | claude-sonnet-4-6 | Medium |
| OpenAI | gpt-4o | Medium |
| Local (Ollama) | llava, qwen2-vl | Free |

Set environment variables:

```bash
# Linux/Mac
export PDF_KB_API_KEY="your-key"
export PDF_KB_BASE_URL="https://your-endpoint/v1"
export PDF_KB_MODEL="gemini-2.5-flash"

# Windows PowerShell
$env:PDF_KB_API_KEY = "your-key"
$env:PDF_KB_BASE_URL = "https://your-endpoint/v1"
$env:PDF_KB_MODEL = "gemini-2.5-flash"
```

## Installation Methods

### Method A: As Claude Code Agent (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/best-pdf-kb.git
```

2. Copy the agent definition to your Claude Code agents directory:
```bash
# Edit agent-definition.md to set correct paths first
cp best-pdf-kb/agent-definition.md ~/.claude/agents/best-pdf-kb.md
```

3. Edit `~/.claude/agents/best-pdf-kb.md`:
   - Update the skill directory path to where you cloned the repo
   - Set `PDF_KB_TOOLS_PATH` if you have the Python tools installed

4. Restart Claude Code. The `best-pdf-kb` agent type will be available.

### Method B: As Claude Code Skill

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/best-pdf-kb.git
```

2. Copy the skill directory:
```bash
cp -r best-pdf-kb/skill ~/.claude/skills/best-pdf-kb
```

3. The skill will be available in Claude Code sessions.

### Method C: Manual (Any AI Assistant)

The skill is defined as markdown specification files. You can use them with any AI assistant that supports long context:

1. Read `skill/SKILL.md` as the system prompt / instructions
2. Read relevant reference files as needed during execution
3. Follow the 11-step workflow in `skill/references/workflow.md`

## Optional: Python Tools (Accelerated Pipeline)

If you have the MinerU Python tools installed, the skill can use them for faster figure extraction and text summarization:

```bash
export PDF_KB_TOOLS_PATH="/path/to/tools/parent/directory"
```

The tools directory should contain:
- `tools/pdf_figure_extractor/`
- `tools/pdf_text_summarizer/`
- `tools/pdf_knowledge_base/`

Without these tools, the skill operates in "agent-only" mode — slower but fully functional using Claude's built-in capabilities.

## Verification

After installation, test with a short PDF:

```
Process this paper: /path/to/any-paper.pdf
```

Expected: workspace directory with `kb/`, `assets/`, `deliverables/comprehensive_reader.html`.

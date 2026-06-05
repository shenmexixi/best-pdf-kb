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

## Troubleshooting

### MinerU fails with "unsupported CPU" on Windows

**Symptom**: `magic-pdf` crashes on import with CPU architecture errors.

**Cause**: `py-cpuinfo` cannot detect CPU architecture on some Windows systems (especially AMD Ryzen), returning an empty string.

**Fix**: Patch `cpuinfo/cpuinfo.py` to add a Windows fallback:

```python
# In cpuinfo.py, find the Windows architecture detection section
# Add fallback when arch_string_raw is empty:
import platform
if not arch_string_raw:
    machine = platform.machine().upper()
    if machine in ('AMD64', 'X86_64'):
        arch_string_raw = 'X86_64'
    elif machine == 'ARM64':
        arch_string_raw = 'ARM_8'
```

### Windows long path errors

**Symptom**: FileNotFoundError or OSError with paths exceeding 260 characters.

**Cause**: PDF filenames + MinerU output subdirectories exceed Windows MAX_PATH.

**Fix** (choose one):
1. Enable long paths system-wide: `reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f`
2. Use short filenames for PDFs before processing
3. Create directory junctions to shorten output paths: `mklink /J short_name "long path"`

### MinerU output already exists

If MinerU has already been run on a PDF (e.g., from a prior `pdf-kb` run), the skill will detect and reuse existing output. Set the `_mineru_output_dir` parameter or ensure the raw output is in the expected location (`output/mineru/` in the workspace).

---

## Verification

After installation, test with a short PDF:

```
Process this paper: /path/to/any-paper.pdf
```

Expected: workspace directory with `kb/`, `assets/`, `deliverables/comprehensive_reader.html`.

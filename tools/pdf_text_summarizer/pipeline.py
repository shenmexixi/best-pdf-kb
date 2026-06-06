import glob, json, time
from pathlib import Path
from typing import Optional
from tools.pdf_text_summarizer.config import SummarizerConfig, load_config
from tools.pdf_text_summarizer.models import PaperSummary
from tools.pdf_text_summarizer.section_splitter import split_sections
from tools.pdf_text_summarizer.section_summarizer import summarize_sections
from tools.pdf_text_summarizer.overall_summarizer import generate_overall_summary
from tools.pdf_text_summarizer.mindmap_generator import generate_mindmap
from tools.pdf_text_summarizer.llm import get_llm_backend

async def summarize_pdf(
    pdf_path: str,
    output_dir: str,
    config: Optional[SummarizerConfig | dict] = None,
    _mineru_output_dir: Optional[str] = None,
    _markdown_path: Optional[str] = None,
) -> dict:
    start_time = time.time()
    if isinstance(config, dict):
        cfg = load_config(config_dict=config)
    elif config is None:
        cfg = SummarizerConfig()
    else:
        cfg = config

    md_path = _markdown_path
    if not md_path:
        md_path = _find_markdown(_mineru_output_dir or "")
    if not md_path:
        raise FileNotFoundError("No markdown file found. Run MinerU first or provide _markdown_path.")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    sections = split_sections(md_path)
    llm_backend = get_llm_backend(cfg.llm)
    section_summaries = await summarize_sections(
        sections, llm_backend, min_length=cfg.min_section_length, max_concurrent=cfg.max_concurrent
    )
    paper_summary = await generate_overall_summary(section_summaries, llm_backend)

    mindmap_text = None
    if cfg.generate_mindmap:
        mindmap_text = await generate_mindmap(paper_summary, llm_backend)
        (out_path / "mindmap.md").write_text(mindmap_text, encoding="utf-8")

    elapsed = time.time() - start_time
    output = {
        "paper_info": {
            "source_pdf": pdf_path,
            "total_sections": _count_sections(sections),
            "sections_summarized": len(section_summaries),
            "processing_time_seconds": round(elapsed, 2),
            "llm_backend": cfg.llm.model,
        },
        "summary": {
            "one_liner": paper_summary.one_liner,
            "abstract_summary": paper_summary.abstract_summary,
            "detailed_summary": paper_summary.detailed_summary,
            "key_contributions": paper_summary.key_contributions,
            "methodology": paper_summary.methodology,
            "main_findings": paper_summary.main_findings,
        },
        "sections": [
            {"title": s.title, "level": s.level, "summary": s.summary, "key_points": s.key_points}
            for s in section_summaries
        ],
    }
    if mindmap_text:
        output["mindmap"] = mindmap_text

    (out_path / "summary.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output


def _find_markdown(output_dir: str) -> str | None:
    if not output_dir:
        return None
    patterns = [f"{output_dir}/**/*.md"]
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        md_files = [m for m in matches if "layout" not in m and "mindmap" not in m]
        if md_files:
            return md_files[0]
    return None


def _count_sections(sections: list) -> int:
    count = len(sections)
    for s in sections:
        if s.children:
            count += _count_sections(s.children)
    return count

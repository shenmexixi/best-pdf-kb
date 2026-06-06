import json, shutil, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from tools.pdf_knowledge_base.config import KnowledgeBaseConfig, load_config
from tools.pdf_knowledge_base.index_builder import build_figure_index
import re

async def build_knowledge_base(
    pdf_path: str, output_dir: str, config: Optional[KnowledgeBaseConfig | dict] = None,
    _figure_results: Optional[dict] = None, _summary_results: Optional[dict] = None,
    _mineru_output_dir: Optional[str] = None,
) -> dict:
    start_time = time.time()
    if isinstance(config, dict):
        cfg = load_config(config_dict=config)
    elif config is None:
        cfg = KnowledgeBaseConfig()
    else:
        cfg = config

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)

    figure_results = _figure_results
    if figure_results is None and cfg.vlm.get("api_key"):
        figure_results = await _run_figure_extraction(pdf_path, str(out / "_tmp_figures"), cfg, _mineru_output_dir)

    summary_results = _summary_results
    if summary_results is None and cfg.llm.get("api_key"):
        summary_results = await _run_summarization(pdf_path, str(out / "_tmp_summary"), cfg, _mineru_output_dir)

    summary_data = summary_results.get("summary", {}) if summary_results else {}
    sections_data = summary_results.get("sections", []) if summary_results else []
    mindmap_text = summary_results.get("mindmap") if summary_results else None
    figures_list = figure_results.get("figures", []) if figure_results else []
    fig_info = figure_results.get("paper_info", {}) if figure_results else {}

    _write_summary_md(out / "summary.md", summary_data)

    if mindmap_text:
        (out / "mindmap.md").write_text(mindmap_text, encoding="utf-8")

    fig_index = build_figure_index(figures_list)
    (out / "figures" / "index.json").write_text(json.dumps(fig_index, ensure_ascii=False, indent=2), encoding="utf-8")

    for fig in figures_list:
        (out / "figures" / f"{fig['id']}.json").write_text(json.dumps(fig, ensure_ascii=False, indent=2), encoding="utf-8")
        # Copy actual image file to figures/ directory
        fig_file = fig.get("file", "")
        if fig_file:
            # Try multiple source locations
            possible_sources = [
                Path(fig_file),  # absolute or relative path from metadata
                out / fig_file,  # relative to output dir
                out / "_tmp_figures" / fig_file,  # from figure extraction temp dir
            ]
            dest_name = Path(fig_file).name
            dest = out / "figures" / dest_name
            if not dest.exists():
                for src in possible_sources:
                    if src.exists() and src.is_file():
                        shutil.copy2(src, dest)
                        break
            # Update figure's file path to be relative to output dir
            fig["file"] = f"figures/{dest_name}"

    if cfg.output_sections and sections_data:
        sections_dir = out / "sections"
        sections_dir.mkdir(exist_ok=True)
        for i, section in enumerate(sections_data):
            safe_title = re.sub(r'[<>:"/\\|?*\t\n\r]', '_', section["title"].lower().replace(" ", "_"))[:30]
            (sections_dir / f"{i+1:02d}_{safe_title}.json").write_text(json.dumps(section, ensure_ascii=False, indent=2), encoding="utf-8")

    # Step: Generate HTML article with expert review
    html_path = None
    if cfg.vlm.get("api_key") or cfg.llm.get("api_key"):
        from tools.pdf_knowledge_base.html_generator import generate_html
        from tools.pdf_knowledge_base.expert_review import expert_review, infer_domain
        from tools.pdf_text_summarizer.llm import get_llm_backend as get_text_llm
        from tools.pdf_text_summarizer.config import LLMConfig as TextLLMConfig

        llm_config = TextLLMConfig(
            api_key=cfg.llm.get("api_key", cfg.vlm.get("api_key", "")),
            base_url=cfg.llm.get("base_url", cfg.vlm.get("base_url")),
            model=cfg.llm.get("model", cfg.vlm.get("model", "gemini-2.5-flash")),
            max_tokens=cfg.llm.get("max_tokens", 8000),
        )
        text_llm = get_text_llm(llm_config)

        html_output = str(out / "article.html")
        try:
            html_content = await generate_html(summary_data, figures_list, text_llm, html_output)
            html_path = "article.html"

            # Expert review
            domain = infer_domain(summary_data)
            review_result = await expert_review(html_content, domain, text_llm)

            # Write revised HTML (use it only if it's not truncated)
            revised_html = review_result["revised_html"]
            if len(revised_html) >= len(html_content) * 0.5:
                # Revision is reasonable length, use it
                revised_path = str(out / "article_final.html")
                Path(revised_path).write_text(revised_html, encoding="utf-8")
                html_path = "article_final.html"
            else:
                # Revision was truncated, keep original article.html
                html_path = "article.html"

            # Write review report
            review_report = {
                "domain": domain,
                "domain_review": review_result["domain_review"],
                "editor_review": review_result["editor_review"],
            }
            (out / "review_report.json").write_text(
                json.dumps(review_report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception:
            pass  # HTML generation is optional, don't break the pipeline

    elapsed = time.time() - start_time
    kb_data = {
        "version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "paper": {
            "source_pdf": pdf_path,
            "title": summary_data.get("one_liner", Path(pdf_path).stem),
            "one_liner": summary_data.get("one_liner", ""),
        },
        "summary": {"file": "summary.md", **summary_data},
        "mindmap": {"file": "mindmap.md"} if mindmap_text else None,
        "figures": {
            "index_file": "figures/index.json",
            "total_detected": fig_info.get("total_figures_detected", len(figures_list)),
            "total_analyzed": fig_info.get("figures_analyzed", len(figures_list)),
            "categories": list(fig_index["index"]["by_category"].keys()),
        },
        "sections": {
            "total": summary_results.get("paper_info", {}).get("total_sections", 0) if summary_results else 0,
            "summarized": len(sections_data),
            "directory": "sections/",
        },
        "processing": {"total_time_seconds": round(elapsed, 2)},
    }
    if html_path:
        kb_data["article"] = {"file": html_path, "review_report": "review_report.json"}
    (out / "knowledge_base.json").write_text(json.dumps(kb_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return kb_data

async def _run_figure_extraction(pdf_path, output_dir, cfg, mineru_dir):
    from tools.pdf_figure_extractor import extract_figures
    return await extract_figures(pdf_path, output_dir, config={"vlm": cfg.vlm, **cfg.figures}, _mineru_output_dir=mineru_dir)

async def _run_summarization(pdf_path, output_dir, cfg, mineru_dir):
    from tools.pdf_text_summarizer import summarize_pdf
    return await summarize_pdf(pdf_path, output_dir, config={"llm": cfg.llm, **cfg.summary}, _mineru_output_dir=mineru_dir)

def _write_summary_md(path: Path, summary: dict) -> None:
    lines = [f"# {summary.get('one_liner', 'Paper Summary')}\n"]
    if summary.get("abstract_summary"):
        lines.append("## Summary\n")
        lines.append(f"{summary['abstract_summary']}\n")
    if summary.get("key_contributions"):
        lines.append("## Key Contributions\n")
        for c in summary["key_contributions"]:
            lines.append(f"- {c}")
        lines.append("")
    if summary.get("main_findings"):
        lines.append("## Main Findings\n")
        for f in summary["main_findings"]:
            lines.append(f"- {f}")
        lines.append("")
    if summary.get("methodology"):
        lines.append("## Methodology\n")
        lines.append(f"{summary['methodology']}\n")
    if summary.get("detailed_summary"):
        lines.append("## Detailed Summary\n")
        lines.append(f"{summary['detailed_summary']}\n")
    path.write_text("\n".join(lines), encoding="utf-8")

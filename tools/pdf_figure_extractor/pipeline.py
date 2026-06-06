import asyncio
import json
import shutil
import time
from pathlib import Path
from typing import Optional

from tools.pdf_figure_extractor.config import PipelineConfig, load_config
from tools.pdf_figure_extractor.models import (
    ClassifiedFigure,
    Importance,
    AnalyzedFigure,
    FigureAnalysis,
)
from tools.pdf_figure_extractor.mineru_parser import parse_pdf
from tools.pdf_figure_extractor.caption_classifier import classify_figures
from tools.pdf_figure_extractor.panel_splitter import detect_and_split_panels
from tools.pdf_figure_extractor.figure_analyzer import analyze_figures as _analyze_figures
from tools.pdf_figure_extractor.vlm import get_backend


async def extract_figures(
    pdf_path: str,
    output_dir: str,
    config: Optional[PipelineConfig | dict] = None,
    _mineru_output_dir: Optional[str] = None,
) -> dict:
    """PDF 图片智能提取主接口。"""
    start_time = time.time()

    if isinstance(config, dict):
        cfg = load_config(config_dict=config)
    elif config is None:
        cfg = PipelineConfig()
    else:
        cfg = config

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    figures_dir = out_path / "figures"
    figures_dir.mkdir(exist_ok=True)

    # Step 1: Parse MinerU output
    mineru_dir = _mineru_output_dir or str(out_path / "raw")
    raw_figures = parse_pdf(pdf_path, mineru_dir, force_reparse=False)

    # Step 2: Classify
    classified = classify_figures(raw_figures, use_llm_fallback=False)

    # Step 3: Filter by importance
    if cfg.importance_filter:
        to_process = [f for f in classified if f.importance in (Importance.HIGH, Importance.MEDIUM)]
    else:
        to_process = classified

    # Step 4: Panel splitting
    sub_figures_map = {}
    if cfg.split_panels and cfg.vlm.api_key:
        vlm_backend = get_backend(cfg.vlm)
        for fig in to_process:
            try:
                is_multi, subs = await detect_and_split_panels(
                    figure=fig,
                    vlm_backend=vlm_backend,
                    grid_size=cfg.panel_split.grid_size,
                    output_dir=str(figures_dir),
                )
                if is_multi:
                    sub_figures_map[fig.raw.id] = subs
            except Exception:
                pass

    # Step 5: Deep analysis
    analyzed: list[AnalyzedFigure] = []
    if cfg.deep_analysis and cfg.vlm.api_key:
        vlm_backend = get_backend(cfg.vlm)
        # Load paper text for context-aware analysis
        paper_text = _load_paper_text(mineru_dir)
        analyzed = await _analyze_figures(
            figures=to_process,
            sub_figures_map=sub_figures_map,
            vlm_backend=vlm_backend,
            max_concurrent=cfg.max_concurrent,
            paper_text=paper_text,
        )
    else:
        for fig in to_process:
            subs = sub_figures_map.get(fig.raw.id, [])
            analyzed.append(AnalyzedFigure(
                id=fig.raw.id,
                file_path=fig.raw.file_path,
                page=fig.raw.page,
                caption=fig.raw.caption,
                category=fig.category,
                importance=fig.importance,
                tags=fig.tags,
                analysis=None,
                sub_figures=[],
                is_multi_panel=len(subs) > 0,
            ))

    # Step 6: Copy figures and build metadata
    figures_output = []
    for fig in analyzed:
        src = Path(fig.file_path)
        if src.exists():
            dest_name = f"{fig.id}_{fig.category.value}{src.suffix}"
            dest = figures_dir / dest_name
            shutil.copy2(src, dest)
            relative_path = f"figures/{dest_name}"
        else:
            relative_path = fig.file_path

        fig_dict = {
            "id": fig.id,
            "file": relative_path,
            "page": fig.page,
            "caption": fig.caption,
            "category": fig.category.value,
            "importance": fig.importance.value,
            "tags": fig.tags,
            "analysis": _analysis_to_dict(fig.analysis),
            "sub_figures": [
                {
                    "id": sf.id,
                    "label": sf.label,
                    "file": f"figures/{Path(sf.file_path).name}" if Path(sf.file_path).exists() else sf.file_path,
                    "analysis": _analysis_to_dict(sf.analysis),
                }
                for sf in fig.sub_figures
            ],
            "is_multi_panel": fig.is_multi_panel,
        }
        figures_output.append(fig_dict)

    index = _build_index(figures_output)

    elapsed = time.time() - start_time
    metadata = {
        "paper_info": {
            "source_pdf": pdf_path,
            "total_figures_detected": len(raw_figures),
            "figures_analyzed": len(analyzed),
            "vlm_backend_used": cfg.vlm.backend if cfg.deep_analysis else None,
            "processing_time_seconds": round(elapsed, 2),
        },
        "figures": figures_output,
        "index": index,
    }

    metadata_path = out_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return metadata


def _analysis_to_dict(analysis: Optional[FigureAnalysis]) -> Optional[dict]:
    if analysis is None:
        return None
    return {
        "description": analysis.description,
        "key_findings": analysis.key_findings,
        "data_summary": analysis.data_summary,
        "tags": analysis.tags,
    }


def _build_index(figures: list[dict]) -> dict:
    by_category: dict[str, list[str]] = {}
    by_importance: dict[str, list[str]] = {}
    by_tag: dict[str, list[str]] = {}

    for fig in figures:
        fig_id = fig["id"]
        by_category.setdefault(fig["category"], []).append(fig_id)
        by_importance.setdefault(fig["importance"], []).append(fig_id)
        for tag in fig.get("tags", []):
            by_tag.setdefault(tag, []).append(fig_id)
        for sf in fig.get("sub_figures", []):
            if sf.get("analysis") and sf["analysis"].get("tags"):
                for tag in sf["analysis"]["tags"]:
                    by_tag.setdefault(tag, []).append(sf["id"])

    return {"by_category": by_category, "by_importance": by_importance, "by_tag": by_tag}


def _load_paper_text(mineru_dir: str) -> str:
    """Load the paper's markdown text from MinerU output for context extraction."""
    import glob as _glob
    patterns = [f"{mineru_dir}/**/*.md"]
    for pattern in patterns:
        matches = _glob.glob(pattern, recursive=True)
        md_files = [m for m in matches if "layout" not in m and "mindmap" not in m]
        if md_files:
            with open(md_files[0], encoding="utf-8") as f:
                return f.read()
    return ""

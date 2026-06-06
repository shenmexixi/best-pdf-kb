import json
import glob
import subprocess
from pathlib import Path
from tools.pdf_figure_extractor.models import RawFigure


def parse_pdf(
    pdf_path: str,
    output_dir: str,
    force_reparse: bool = False,
) -> list[RawFigure]:
    """调用 MinerU 解析 PDF，返回所有检测到的图片。

    如果 output_dir 中已有解析结果且 force_reparse=False，直接读取。
    """
    content_list_path = _find_content_list(output_dir)

    if content_list_path and not force_reparse:
        return parse_content_list(content_list_path)

    _run_mineru(pdf_path, output_dir)

    content_list_path = _find_content_list(output_dir)
    if not content_list_path:
        raise RuntimeError(f"MinerU did not produce content_list.json in {output_dir}")
    return parse_content_list(content_list_path)


def parse_content_list(content_list_path: str) -> list[RawFigure]:
    """解析 MinerU 的 content_list.json，提取图片块。"""
    content_list_dir = Path(content_list_path).parent

    with open(content_list_path, encoding="utf-8") as f:
        data = json.load(f)

    blocks = data if isinstance(data, list) else data.get("content_list", [])
    figures = []
    fig_counter = {}

    for block in blocks:
        block_type = block.get("type", "")
        if block_type not in ("image", "chart", "table"):
            continue

        page = block.get("page_idx", 0)
        key = f"p{page}"
        fig_counter[key] = fig_counter.get(key, 0)
        fig_id = f"fig_{key}_{fig_counter[key]}"
        fig_counter[key] += 1

        raw_caption = block.get("img_caption", "") or ""
        if isinstance(raw_caption, list):
            raw_caption = " ".join(str(s) for s in raw_caption).strip()

        raw_path = block.get("img_path", "")
        # Resolve relative paths against the directory containing content_list.json
        if raw_path and not Path(raw_path).is_absolute():
            resolved = content_list_dir / raw_path
            if resolved.exists():
                raw_path = str(resolved)

        figures.append(RawFigure(
            id=fig_id,
            file_path=raw_path,
            caption=raw_caption,
            page=page,
            fig_type=block_type,
        ))

    return figures


def _find_content_list(output_dir: str) -> str | None:
    patterns = [
        f"{output_dir}/**/*content_list.json",
        f"{output_dir}/**/content_list.json",
    ]
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    return None


def _run_mineru(pdf_path: str, output_dir: str) -> None:
    cmd = ["magic-pdf", "-p", pdf_path, "-o", output_dir, "-m", "auto"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"MinerU failed: {result.stderr}")

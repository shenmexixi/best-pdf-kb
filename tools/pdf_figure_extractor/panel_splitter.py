import json
import re
from pathlib import Path
from PIL import Image
from tools.pdf_figure_extractor.models import ClassifiedFigure, SubFigure
from tools.pdf_figure_extractor.vlm.base import VLMBackend
from tools.pdf_figure_extractor.figure_cropper import add_coordinate_grid, crop_region


PANEL_DETECTION_PROMPT = """这是一张科研论文中的图片，已叠加坐标网格（列: A-{max_col}，行: 1-{grid_size}）。

请判断：
1. 这张图是否包含多个独立子图（如 (a), (b), (c) 面板）？
2. 如果是，请标注每个子图的坐标范围。

输出严格 JSON 格式（不要输出其他内容）：
{{"is_multi_panel": true/false, "panels": [{{"label": "(a)", "top_left": "A1", "bottom_right": "E5", "description_hint": "简要描述"}}]}}

如果不是复合图，输出: {{"is_multi_panel": false, "panels": []}}
"""


async def detect_and_split_panels(
    figure: ClassifiedFigure,
    vlm_backend: VLMBackend,
    grid_size: int = 10,
    output_dir: str = ".",
) -> tuple[bool, list[SubFigure]]:
    """检测图片是否为复合图，如果是则拆分为子图。"""
    gridded_path = add_coordinate_grid(figure.raw.file_path, grid_size=grid_size)

    max_col = chr(ord("A") + grid_size - 1)
    prompt = PANEL_DETECTION_PROMPT.format(max_col=max_col, grid_size=grid_size)
    response = await vlm_backend.analyze_image(gridded_path, prompt)

    is_multi, panels = _parse_panel_response(response)

    if not is_multi or not panels:
        _cleanup_grid(gridded_path)
        return False, []

    # Crop sub-figures
    sub_figures = []
    img = Image.open(figure.raw.file_path)
    w, h = img.size
    cell_w = w / grid_size
    cell_h = h / grid_size

    for panel in panels:
        label = panel.get("label", "")
        top_left = panel.get("top_left", "A1")
        bottom_right = panel.get("bottom_right", f"{max_col}{grid_size}")

        safe_label = re.sub(r"[^\w]", "", label)
        sub_id = f"{figure.raw.id}_{safe_label}"
        sub_filename = f"{sub_id}.png"
        sub_path = str(Path(output_dir) / sub_filename)

        crop_region(
            image_path=figure.raw.file_path,
            top_left=top_left,
            bottom_right=bottom_right,
            grid_size=grid_size,
            output_path=sub_path,
        )

        tl_col = ord(top_left[0].upper()) - ord("A")
        tl_row = int(top_left[1:]) - 1
        br_col = ord(bottom_right[0].upper()) - ord("A")
        br_row = int(bottom_right[1:]) - 1

        bbox = (
            tl_col * cell_w / w,
            tl_row * cell_h / h,
            (br_col + 1) * cell_w / w,
            (br_row + 1) * cell_h / h,
        )

        sub_figures.append(SubFigure(
            id=sub_id,
            label=label,
            file_path=sub_path,
            bbox_in_parent=bbox,
        ))

    _cleanup_grid(gridded_path)
    return True, sub_figures


def _parse_panel_response(response: str) -> tuple[bool, list[dict]]:
    """解析 VLM 返回的 panel 检测结果。"""
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    try:
        data = json.loads(text)
        is_multi = data.get("is_multi_panel", False)
        panels = data.get("panels", [])
        return is_multi, panels
    except (json.JSONDecodeError, KeyError):
        return False, []


def _cleanup_grid(gridded_path: str) -> None:
    p = Path(gridded_path)
    if p.exists() and "_grid" in p.name:
        p.unlink()

from pathlib import Path
from PIL import Image, ImageDraw


def add_coordinate_grid(
    image_path: str,
    grid_size: int = 10,
    output_path: str | None = None,
) -> str:
    """在图片上叠加坐标网格。

    列标记: A, B, C, ... (左到右)
    行标记: 1, 2, 3, ... (上到下)
    """
    img = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size
    cell_w = w / grid_size
    cell_h = h / grid_size

    grid_color = (128, 128, 128, 80)
    label_color = (255, 0, 0, 200)

    for i in range(grid_size + 1):
        x = int(i * cell_w)
        draw.line([(x, 0), (x, h)], fill=grid_color, width=1)
        if i < grid_size:
            label = chr(ord("A") + i)
            draw.text((x + 2, 2), label, fill=label_color)

    for j in range(grid_size + 1):
        y = int(j * cell_h)
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)
        if j < grid_size:
            label = str(j + 1)
            draw.text((2, y + 2), label, fill=label_color)

    result = Image.alpha_composite(img, overlay).convert("RGB")

    if output_path is None:
        p = Path(image_path)
        output_path = str(p.parent / f"{p.stem}_grid{p.suffix}")

    result.save(output_path)
    return output_path


def grid_coord_to_pixel(
    coord: str,
    image_width: int,
    image_height: int,
    grid_size: int = 10,
) -> tuple[int, int]:
    """将网格坐标 (如 'E5') 转换为像素坐标 (左上角)。"""
    col_letter = coord[0].upper()
    row_number = int(coord[1:])

    col_idx = ord(col_letter) - ord("A")
    row_idx = row_number - 1

    cell_w = image_width / grid_size
    cell_h = image_height / grid_size

    x = int(col_idx * cell_w)
    y = int(row_idx * cell_h)
    return x, y


def crop_region(
    image_path: str,
    top_left: str,
    bottom_right: str,
    grid_size: int = 10,
    output_path: str | None = None,
) -> str:
    """按网格坐标裁剪图片区域。包含 bottom_right 所在的整个网格单元。"""
    img = Image.open(image_path)
    w, h = img.size
    cell_w = w / grid_size
    cell_h = h / grid_size

    x1, y1 = grid_coord_to_pixel(top_left, w, h, grid_size)

    br_col = ord(bottom_right[0].upper()) - ord("A")
    br_row = int(bottom_right[1:]) - 1
    x2 = int((br_col + 1) * cell_w)
    y2 = int((br_row + 1) * cell_h)

    x2 = min(x2, w)
    y2 = min(y2, h)

    cropped = img.crop((x1, y1, x2, y2))

    if output_path is None:
        p = Path(image_path)
        output_path = str(p.parent / f"{p.stem}_crop{p.suffix}")

    cropped.save(output_path)
    return output_path

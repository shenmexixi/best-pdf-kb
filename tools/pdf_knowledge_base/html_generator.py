import json
import re
from pathlib import Path
from typing import Optional
from tools.pdf_text_summarizer.llm.base import LLMBackend

HTML_GENERATION_PROMPT = """你是一位科研论文解读专家。请基于以下论文摘要和图片分析结果，生成一篇图文并茂的中文解读文章（HTML格式）。

论文概要：{one_liner}

详细总结：
{detailed_summary}

关键贡献：
{contributions}

方法论：{methodology}

主要发现：
{findings}

论文图片信息（你必须使用下面提供的真实文件名，不要编造文件名）：
{figures_info}

请生成一篇结构清晰、逻辑流畅的中文解读 HTML。要求：
1. 使用 <h1> 作为文章标题，<h2> 作为各部分标题
2. 按研究逻辑组织（背景→问题→方法→结果→意义），而非简单罗列
3. 【重要】插入图片时，必须使用上面"论文图片信息"中给出的真实文件名，格式为 <img src="figures/真实文件名" alt="caption">。禁止使用 placeholder 或编造的文件名。
4. 每张图片前后要有对图片内容的讲解文字
5. 尽量将所有图片都用上，按内容逻辑插入合适位置
6. 使用简洁专业的中文，面向有一定学术背景的读者
7. 不要使用 markdown，直接输出 HTML 标签
8. 加入适当的 CSS 样式使排版美观

输出完整的 HTML（从 <!DOCTYPE html> 开始），不要输出其他内容。
"""


async def generate_html(
    summary_data: dict,
    figures_data: list[dict],
    llm_backend: LLMBackend,
    output_path: str,
) -> str:
    """Generate a Chinese HTML article with embedded figures."""
    # Format figures info for the prompt
    figures_info = _format_figures_for_prompt(figures_data)
    contributions = "\n".join(f"- {c}" for c in summary_data.get("key_contributions", []))
    findings = "\n".join(f"- {f}" for f in summary_data.get("main_findings", []))

    prompt = HTML_GENERATION_PROMPT.format(
        one_liner=summary_data.get("one_liner", ""),
        detailed_summary=summary_data.get("detailed_summary", ""),
        contributions=contributions or "无",
        methodology=summary_data.get("methodology", ""),
        findings=findings or "无",
        figures_info=figures_info,
    )

    response = await llm_backend.complete(prompt)
    html_content = _clean_html_response(response)

    # Post-process: ensure figures are embedded in the HTML
    html_content = _ensure_figures_embedded(html_content, figures_data)

    # Write to file
    Path(output_path).write_text(html_content, encoding="utf-8")
    return html_content


def _format_figures_for_prompt(figures: list[dict]) -> str:
    if not figures:
        return "（无图片信息）"
    parts = []
    for fig in figures:
        file_path = fig.get("file", "")
        filename = Path(file_path).name if file_path else ""
        caption = fig.get("caption", "")
        analysis = fig.get("analysis", {})
        desc = analysis.get("description", "") if analysis else ""
        parts.append(f"- 文件: {filename}\n  Caption: {caption}\n  描述: {desc[:200]}")
    return "\n".join(parts)


def _clean_html_response(response: str) -> str:
    text = response.strip()
    # Remove code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    # Ensure it starts with DOCTYPE or html tag
    if not text.lower().startswith("<!doctype") and not text.lower().startswith("<html"):
        text = f'<!DOCTYPE html>\n<html lang="zh-CN">\n<head><meta charset="utf-8"><title>论文解读</title></head>\n<body>\n{text}\n</body>\n</html>'
    return text


def _ensure_figures_embedded(html: str, figures: list[dict]) -> str:
    """If the LLM failed to include figure images, append them as a gallery section."""
    if not figures:
        return html

    # Check how many figures are already referenced
    existing_refs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    figure_filenames = set()
    for fig in figures:
        file_path = fig.get("file", "")
        if file_path:
            figure_filenames.add(Path(file_path).name)

    referenced = set(Path(ref).name for ref in existing_refs) & figure_filenames
    missing = figure_filenames - referenced

    if not missing:
        return html  # All figures are already referenced

    # Build a figure gallery section for missing figures
    gallery_html = '\n<h2>论文图表</h2>\n<div class="figure-gallery">\n'
    for fig in figures:
        file_path = fig.get("file", "")
        filename = Path(file_path).name if file_path else ""
        if filename not in missing:
            continue
        caption = fig.get("caption", "")
        analysis = fig.get("analysis", {})
        desc = analysis.get("description", "") if analysis else ""
        gallery_html += f'''<div class="figure">
<img src="figures/{filename}" alt="{caption}" style="max-width:100%;height:auto;">
<p class="figure-caption"><strong>{caption}</strong></p>
{f'<p class="figure-desc">{desc[:300]}</p>' if desc else ''}
</div>
'''
    gallery_html += '</div>\n'

    # Insert before </body> if present, otherwise append
    if '</body>' in html:
        html = html.replace('</body>', gallery_html + '</body>')
    else:
        html += gallery_html

    return html

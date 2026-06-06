import asyncio
import json
import re
from tools.pdf_figure_extractor.models import (
    ClassifiedFigure,
    SubFigure,
    FigureAnalysis,
    AnalyzedFigure,
    AnalyzedSubFigure,
)
from tools.pdf_figure_extractor.vlm.base import VLMBackend


ANALYSIS_PROMPT = """你是一位科研文献图片分析专家。请对这张科研论文中的图片进行深度解读。

图片 Caption: {caption}
图片分类: {category}
{sub_context}
{text_context}

基于图片视觉内容、Caption 信息以及论文正文中的相关讨论，请撰写一段全面深入的中文解读。

请用中文输出严格 JSON 格式（不要输出其他内容）：
{{
  "description": "综合视觉识别和正文讨论的详细图片解读，200-500字。要说明：图中展示了什么、关键视觉元素、数据或结构的含义、以及该图在论文论证中的作用",
  "key_findings": ["从图中结合正文可得出的关键发现1", "关键发现2", "关键发现3"],
  "data_summary": "如果是图表，结合正文描述具体数据趋势和关键数值；否则设为 null",
  "tags": ["中文标签1", "中文标签2", "中文标签3", "中文标签4", "中文标签5"]
}}
"""


def extract_figure_context(markdown_text: str, caption: str) -> str:
    """从论文正文中提取与该图相关的讨论段落。

    搜索策略：
    1. 查找 "Figure N" / "Fig. N" 的引用
    2. 提取引用前后各 2-3 句话作为上下文
    """
    if not caption or not markdown_text:
        return ""

    # Extract figure number from caption
    fig_match = re.search(r"(?:figure|fig\.?)\s*(\d+)", caption, re.IGNORECASE)
    if not fig_match:
        return ""

    fig_num = fig_match.group(1)

    # Search for references to this figure in the text
    patterns = [
        rf"(?:figure|fig\.?)\s*{fig_num}\b",
    ]

    contexts = []
    sentences = re.split(r"(?<=[.。!?])\s+", markdown_text)

    for i, sentence in enumerate(sentences):
        for pattern in patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                # Get surrounding sentences (2 before, 2 after)
                start = max(0, i - 2)
                end = min(len(sentences), i + 3)
                context = " ".join(sentences[start:end])
                if context not in contexts and len(context) > 30:
                    contexts.append(context)
                break

    if not contexts:
        return ""

    # Limit to top 3 most relevant contexts, max 1000 chars total
    combined = "\n".join(contexts[:3])
    return combined[:1000]


async def analyze_figures(
    figures: list[ClassifiedFigure],
    sub_figures_map: dict[str, list[SubFigure]],
    vlm_backend: VLMBackend,
    max_concurrent: int = 3,
    paper_text: str = "",
) -> list[AnalyzedFigure]:
    """对所有重要图片进行 VLM 深度分析。

    Args:
        paper_text: 论文正文（markdown），用于提取每张图的上下文讨论。
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [
        _analyze_single(fig, sub_figures_map.get(fig.raw.id, []), vlm_backend, semaphore, paper_text)
        for fig in figures
    ]
    return await asyncio.gather(*tasks)


async def _analyze_single(
    fig: ClassifiedFigure,
    sub_figs: list[SubFigure],
    vlm_backend: VLMBackend,
    semaphore: asyncio.Semaphore,
    paper_text: str = "",
) -> AnalyzedFigure:
    async with semaphore:
        sub_context = f"该图包含 {len(sub_figs)} 个子图。" if sub_figs else ""

        # Extract relevant text context for this figure
        text_context = ""
        if paper_text and fig.raw.caption:
            context = extract_figure_context(paper_text, fig.raw.caption)
            if context:
                text_context = f"论文正文中对该图的讨论：\n{context}"

        prompt = ANALYSIS_PROMPT.format(
            caption=fig.raw.caption,
            category=fig.category.value,
            sub_context=sub_context,
            text_context=text_context,
        )
        try:
            response = await vlm_backend.analyze_image(fig.raw.file_path, prompt)
            analysis = _parse_analysis_response(response)
        except Exception:
            analysis = None

        analyzed_subs = []
        for sub in sub_figs:
            sub_prompt = ANALYSIS_PROMPT.format(
                caption=f"{fig.raw.caption} - 子图 {sub.label}",
                category=fig.category.value,
                sub_context=f"这是复合图中的子图 {sub.label}。",
                text_context=text_context,
            )
            try:
                sub_response = await vlm_backend.analyze_image(sub.file_path, sub_prompt)
                sub_analysis = _parse_analysis_response(sub_response)
            except Exception:
                sub_analysis = None

            analyzed_subs.append(AnalyzedSubFigure(
                id=sub.id,
                label=sub.label,
                file_path=sub.file_path,
                analysis=sub_analysis,
            ))

        all_tags = list(fig.tags)
        if analysis and analysis.tags:
            for tag in analysis.tags:
                if tag not in all_tags:
                    all_tags.append(tag)

        return AnalyzedFigure(
            id=fig.raw.id,
            file_path=fig.raw.file_path,
            page=fig.raw.page,
            caption=fig.raw.caption,
            category=fig.category,
            importance=fig.importance,
            tags=all_tags,
            analysis=analysis,
            sub_figures=analyzed_subs,
            is_multi_panel=len(sub_figs) > 0,
        )


def _parse_analysis_response(response: str) -> FigureAnalysis:
    text = response.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    try:
        data = json.loads(text)
        return FigureAnalysis(
            description=data.get("description", ""),
            key_findings=data.get("key_findings", []),
            data_summary=data.get("data_summary"),
            tags=data.get("tags", []),
        )
    except (json.JSONDecodeError, KeyError):
        return FigureAnalysis(
            description=text,
            key_findings=[],
            data_summary=None,
            tags=[],
        )

import re
from tools.pdf_figure_extractor.models import RawFigure, ClassifiedFigure, FigureCategory, Importance

CATEGORY_KEYWORDS: dict[FigureCategory, list[str]] = {
    FigureCategory.OVERVIEW: [
        "overview", "framework", "architecture", "pipeline",
        "workflow", "schematic", "system", "proposed",
    ],
    FigureCategory.EXPERIMENT: [
        "comparison", "ablation", "benchmark", "performance",
        "accuracy", "evaluation", "versus", "vs.", "vs ",
    ],
    FigureCategory.RESULT: [
        "result", "visualization", "distribution", "spectrum",
        "plot", "map", "surface", "density", "contour",
        "rendering",
    ],
    FigureCategory.METHOD: [
        "illustration", "diagram", "mechanism", "process",
        "procedure", "step", "algorithm",
    ],
    FigureCategory.SUPPLEMENTARY: [
        "supplementary", "appendix", "additional", "supporting",
    ],
}

HIGH_IMPORTANCE_SIGNALS = [
    r"figure\s*1[^0-9]", "overview", "main result", "proposed",
    "our method", "our approach",
]
LOW_IMPORTANCE_SIGNALS = [
    "supplementary", "appendix", "supporting information",
    r"figure\s*s\d",
]

_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "for", "to", "and", "is",
    "are", "was", "were", "with", "from", "by", "at", "as", "or",
    "figure", "fig", "table", "that", "this", "its", "their",
}


def classify_figures(
    figures: list[RawFigure],
    use_llm_fallback: bool = True,
    llm_config: dict | None = None,
) -> list[ClassifiedFigure]:
    """对所有图片进行分类和重要性判断。"""
    results = []
    for fig in figures:
        category, importance = _classify_by_rules(fig.caption)
        tags = _extract_tags(fig.caption)
        results.append(ClassifiedFigure(
            raw=fig,
            category=category,
            importance=importance,
            tags=tags,
        ))
    return results


def _classify_by_rules(caption: str) -> tuple[FigureCategory, Importance]:
    """基于关键词规则分类。"""
    caption_lower = caption.lower()

    category = FigureCategory.UNKNOWN
    best_score = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in caption_lower)
        if score > best_score:
            best_score = score
            category = cat

    importance = Importance.MEDIUM

    for signal in HIGH_IMPORTANCE_SIGNALS:
        if re.search(signal, caption_lower):
            importance = Importance.HIGH
            break

    if importance != Importance.HIGH:
        for signal in LOW_IMPORTANCE_SIGNALS:
            if re.search(signal, caption_lower):
                importance = Importance.LOW
                break

    return category, importance


def _extract_tags(caption: str) -> list[str]:
    """从 caption 中提取有意义的关键词作为标签。"""
    text = re.sub(r"^(figure|fig\.?)\s*\d+\s*[:.]?\s*", "", caption, flags=re.IGNORECASE)
    words = re.findall(r"[a-zA-Z][\w-]*[a-zA-Z]|[a-zA-Z]", text.lower())
    tags = [w for w in words if w not in _STOPWORDS and len(w) > 2]
    seen = set()
    unique_tags = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)
    return unique_tags[:10]

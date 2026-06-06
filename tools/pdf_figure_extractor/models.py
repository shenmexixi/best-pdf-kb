# tools/pdf_figure_extractor/models.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FigureCategory(str, Enum):
    OVERVIEW = "overview"
    EXPERIMENT = "experiment"
    RESULT = "result"
    METHOD = "method"
    SUPPLEMENTARY = "supplementary"
    UNKNOWN = "unknown"


class Importance(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RawFigure:
    """MinerU 解析出的原始图片信息。"""
    id: str
    file_path: str
    caption: str
    page: int
    fig_type: str  # "image" | "chart" | "table"


@dataclass
class ClassifiedFigure:
    """经过 caption 分类后的图片。"""
    raw: RawFigure
    category: FigureCategory
    importance: Importance
    tags: list[str] = field(default_factory=list)


@dataclass
class SubFigure:
    """从复合图中拆分出的子图。"""
    id: str
    label: str
    file_path: str
    bbox_in_parent: tuple[float, float, float, float]


@dataclass
class FigureAnalysis:
    """VLM 深度分析结果。"""
    description: str
    key_findings: list[str]
    data_summary: Optional[str]
    tags: list[str]


@dataclass
class AnalyzedFigure:
    """最终分析完成的图片。"""
    id: str
    file_path: str
    page: int
    caption: str
    category: FigureCategory
    importance: Importance
    tags: list[str]
    analysis: Optional[FigureAnalysis]
    sub_figures: list["AnalyzedSubFigure"] = field(default_factory=list)
    is_multi_panel: bool = False


@dataclass
class AnalyzedSubFigure:
    """分析完成的子图。"""
    id: str
    label: str
    file_path: str
    analysis: Optional[FigureAnalysis]

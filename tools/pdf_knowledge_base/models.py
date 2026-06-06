from dataclasses import dataclass
from typing import Optional

@dataclass
class KnowledgeBase:
    source_pdf: str
    title: str
    output_dir: str
    summary: Optional[dict]
    figures: Optional[dict]
    mindmap: Optional[str]
    processing_time: float

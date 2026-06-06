from dataclasses import dataclass, field
from typing import Optional
import os
import yaml

@dataclass
class KnowledgeBaseConfig:
    vlm: dict = field(default_factory=dict)
    llm: dict = field(default_factory=dict)
    figures: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)
    output_sections: bool = True

def load_config(config_path: Optional[str] = None, config_dict: Optional[dict] = None) -> KnowledgeBaseConfig:
    raw = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    if config_dict:
        raw.update(config_dict)
    return KnowledgeBaseConfig(
        vlm=raw.get("vlm", {}),
        llm=raw.get("llm", {}),
        figures=raw.get("figures", {}),
        summary=raw.get("summary", {}),
        output_sections=raw.get("output_sections", True),
    )

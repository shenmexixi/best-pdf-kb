from dataclasses import dataclass, field
from typing import Optional
import os
import yaml


@dataclass
class VLMConfig:
    backend: str = "claude"
    api_key: str = ""
    model: str = ""
    max_tokens: int = 2000
    base_url: Optional[str] = None


@dataclass
class ClassificationConfig:
    use_llm_fallback: bool = True
    llm_model: str = "claude-haiku-4-5-20251001"


@dataclass
class PanelSplitConfig:
    grid_size: int = 10
    min_panel_area: float = 0.1


@dataclass
class OutputConfig:
    image_format: str = "png"
    image_quality: int = 95
    naming_template: str = "{fig_id}_{category}"


@dataclass
class PipelineConfig:
    vlm: VLMConfig = field(default_factory=VLMConfig)
    classification: ClassificationConfig = field(default_factory=ClassificationConfig)
    panel_split: PanelSplitConfig = field(default_factory=PanelSplitConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    importance_filter: bool = True
    split_panels: bool = False
    deep_analysis: bool = True
    max_concurrent: int = 3


ENV_KEY_MAP = {
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
}


def load_config(
    config_path: Optional[str] = None,
    config_dict: Optional[dict] = None,
) -> PipelineConfig:
    """Load config from a YAML file or dict, with env vars as API key fallback."""
    raw = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    if config_dict:
        _deep_merge(raw, config_dict)

    config = PipelineConfig()

    vlm_raw = raw.get("vlm", {})
    if vlm_raw:
        config.vlm.backend = vlm_raw.get("backend", config.vlm.backend)
        config.vlm.api_key = vlm_raw.get("api_key", config.vlm.api_key)
        config.vlm.model = vlm_raw.get("model", config.vlm.model)
        config.vlm.max_tokens = vlm_raw.get("max_tokens", config.vlm.max_tokens)
        config.vlm.base_url = vlm_raw.get("base_url", config.vlm.base_url)

    if not config.vlm.api_key:
        env_key = ENV_KEY_MAP.get(config.vlm.backend, "")
        config.vlm.api_key = os.environ.get(env_key, "")

    cls_raw = raw.get("classification", {})
    if cls_raw:
        config.classification.use_llm_fallback = cls_raw.get("use_llm_fallback", config.classification.use_llm_fallback)
        config.classification.llm_model = cls_raw.get("llm_model", config.classification.llm_model)

    ps_raw = raw.get("panel_split", {})
    if ps_raw:
        config.panel_split.grid_size = ps_raw.get("grid_size", config.panel_split.grid_size)
        config.panel_split.min_panel_area = ps_raw.get("min_panel_area", config.panel_split.min_panel_area)

    out_raw = raw.get("output", {})
    if out_raw:
        config.output.image_format = out_raw.get("image_format", config.output.image_format)
        config.output.image_quality = out_raw.get("image_quality", config.output.image_quality)
        config.output.naming_template = out_raw.get("naming_template", config.output.naming_template)

    config.importance_filter = raw.get("importance_filter", config.importance_filter)
    config.split_panels = raw.get("split_panels", config.split_panels)
    config.deep_analysis = raw.get("deep_analysis", config.deep_analysis)
    config.max_concurrent = raw.get("max_concurrent", config.max_concurrent)

    return config


def _deep_merge(base: dict, override: dict) -> None:
    for key, val in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val

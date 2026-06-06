from dataclasses import dataclass, field
from typing import Optional
import os, yaml

@dataclass
class LLMConfig:
    api_key: str = ""
    base_url: Optional[str] = None
    model: str = "gemini-2.5-flash"
    max_tokens: int = 4000

@dataclass
class SummarizerConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    summary_levels: list[str] = field(default_factory=lambda: ["one_liner", "abstract", "detailed"])
    generate_mindmap: bool = True
    max_concurrent: int = 3
    min_section_length: int = 100
    language: str = "en"

def load_config(config_path: Optional[str] = None, config_dict: Optional[dict] = None) -> SummarizerConfig:
    raw = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    if config_dict:
        _deep_merge(raw, config_dict)

    config = SummarizerConfig()
    llm_raw = raw.get("llm", {})
    if llm_raw:
        config.llm.api_key = llm_raw.get("api_key", config.llm.api_key)
        config.llm.base_url = llm_raw.get("base_url", config.llm.base_url)
        config.llm.model = llm_raw.get("model", config.llm.model)
        config.llm.max_tokens = llm_raw.get("max_tokens", config.llm.max_tokens)

    if not config.llm.api_key:
        config.llm.api_key = os.environ.get("OPENAI_API_KEY", "")
        if not config.llm.api_key:
            config.llm.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not config.llm.api_key:
            config.llm.api_key = os.environ.get("DASHSCOPE_API_KEY", "")

    config.summary_levels = raw.get("summary_levels", config.summary_levels)
    config.generate_mindmap = raw.get("generate_mindmap", config.generate_mindmap)
    config.max_concurrent = raw.get("max_concurrent", config.max_concurrent)
    config.min_section_length = raw.get("min_section_length", config.min_section_length)
    config.language = raw.get("language", config.language)
    return config

def _deep_merge(base: dict, override: dict) -> None:
    for key, val in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val

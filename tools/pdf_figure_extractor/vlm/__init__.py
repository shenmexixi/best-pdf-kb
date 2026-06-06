from tools.pdf_figure_extractor.vlm.base import VLMBackend
from tools.pdf_figure_extractor.config import VLMConfig


def get_backend(config: VLMConfig) -> VLMBackend:
    """Factory: create VLM backend from config."""
    if config.backend == "claude":
        from tools.pdf_figure_extractor.vlm.claude import ClaudeBackend
        return ClaudeBackend(config)
    elif config.backend == "openai":
        from tools.pdf_figure_extractor.vlm.openai import OpenAIBackend
        return OpenAIBackend(config)
    elif config.backend == "qwen":
        from tools.pdf_figure_extractor.vlm.qwen import QwenBackend
        return QwenBackend(config)
    else:
        raise ValueError(f"Unknown VLM backend: {config.backend}")

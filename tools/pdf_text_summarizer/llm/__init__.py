from tools.pdf_text_summarizer.llm.base import LLMBackend
from tools.pdf_text_summarizer.llm.openai_compat import OpenAICompatBackend
from tools.pdf_text_summarizer.config import LLMConfig

def get_llm_backend(config: LLMConfig) -> LLMBackend:
    return OpenAICompatBackend(config)

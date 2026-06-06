from tools.pdf_text_summarizer.llm.base import LLMBackend
from tools.pdf_text_summarizer.config import LLMConfig

class OpenAICompatBackend(LLMBackend):
    def __init__(self, config: LLMConfig):
        self._model = config.model
        self._max_tokens = config.max_tokens
        import openai
        kwargs = {"api_key": config.api_key}
        if config.base_url:
            kwargs["base_url"] = config.base_url
        self._client = openai.AsyncOpenAI(**kwargs)

    @property
    def name(self) -> str:
        return f"openai-compat ({self._model})"

    async def complete(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await self._client.chat.completions.create(
            model=self._model, max_tokens=self._max_tokens, messages=messages,
        )
        return response.choices[0].message.content

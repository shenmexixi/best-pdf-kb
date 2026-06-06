import base64
from pathlib import Path
from tools.pdf_figure_extractor.vlm.base import VLMBackend
from tools.pdf_figure_extractor.config import VLMConfig


class ClaudeBackend(VLMBackend):
    def __init__(self, config: VLMConfig):
        self._config = config
        self._model = config.model or "claude-sonnet-4-20250514"
        import anthropic
        self._client = anthropic.AsyncAnthropic(api_key=config.api_key)

    @property
    def name(self) -> str:
        return "claude"

    @property
    def supports_batch(self) -> bool:
        return True

    async def analyze_image(self, image_path: str, prompt: str) -> str:
        image_data = self._encode_image(image_path)
        media_type = self._get_media_type(image_path)
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=self._config.max_tokens,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return response.content[0].text

    async def analyze_images_batch(self, image_paths: list[str], prompt: str) -> str:
        content = []
        for path in image_paths:
            image_data = self._encode_image(path)
            media_type = self._get_media_type(path)
            content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}})
        content.append({"type": "text", "text": prompt})

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=self._config.max_tokens,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _get_media_type(self, image_path: str) -> str:
        suffix = Path(image_path).suffix.lower().lstrip(".")
        return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}.get(suffix, "image/png")

import base64
from pathlib import Path
from tools.pdf_figure_extractor.vlm.base import VLMBackend
from tools.pdf_figure_extractor.config import VLMConfig


class QwenBackend(VLMBackend):
    def __init__(self, config: VLMConfig):
        self._config = config
        self._model = config.model or "qwen-vl-max"
        import openai
        self._client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    @property
    def name(self) -> str:
        return "qwen"

    @property
    def supports_batch(self) -> bool:
        return True

    async def analyze_image(self, image_path: str, prompt: str) -> str:
        image_data = self._encode_image(image_path)
        media_type = self._get_media_type(image_path)
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._config.max_tokens,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_data}"}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return response.choices[0].message.content

    async def analyze_images_batch(self, image_paths: list[str], prompt: str) -> str:
        content = []
        for path in image_paths:
            image_data = self._encode_image(path)
            media_type = self._get_media_type(path)
            content.append({"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_data}"}})
        content.append({"type": "text", "text": prompt})
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._config.max_tokens,
            messages=[{"role": "user", "content": content}],
        )
        return response.choices[0].message.content

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _get_media_type(self, image_path: str) -> str:
        suffix = Path(image_path).suffix.lower().lstrip(".")
        return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(suffix, "image/png")

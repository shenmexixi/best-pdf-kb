from abc import ABC, abstractmethod


class VLMBackend(ABC):
    @abstractmethod
    async def analyze_image(self, image_path: str, prompt: str) -> str:
        """单张图片分析，返回 VLM 原始文本输出。"""

    @abstractmethod
    async def analyze_images_batch(self, image_paths: list[str], prompt: str) -> str:
        """多张图片分析（用于批量或对比）。"""

    @property
    @abstractmethod
    def supports_batch(self) -> bool:
        """是否支持多图输入。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """后端名称标识。"""

from abc import ABC, abstractmethod

class LLMBackend(ABC):
    @abstractmethod
    async def complete(self, prompt: str, system: str = "") -> str:
        """Send text prompt, return LLM response."""

    @property
    @abstractmethod
    def name(self) -> str: ...

from abc import ABC, abstractmethod


class CaptchaSolverPort(ABC):
    @abstractmethod
    async def solve(self, image_bytes: bytes) -> str:
        ...

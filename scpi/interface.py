from abc import ABC, abstractmethod


class Interface(ABC):
    @abstractmethod
    async def send_data(self, command: str) -> None:
        pass

    @abstractmethod
    async def recv_data(self) -> str:
        pass

    @abstractmethod
    async def recv_data_field(self, separators: str) -> str:
        pass

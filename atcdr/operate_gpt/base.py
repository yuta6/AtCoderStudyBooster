from abc import ABC, abstractmethod

class BaseChatGPTClient(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None:
        pass

    @abstractmethod
    def read_message(self) -> str:
        pass

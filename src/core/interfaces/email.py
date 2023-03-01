from abc import ABC, abstractmethod

from src.core.schemas.email import EmailSchema


class EmailClient(ABC):
    @abstractmethod
    def send(self, email: EmailSchema) -> None:
        raise NotImplementedError


class EmailService(ABC):
    def __init__(self, client: EmailClient) -> None:
        self.client = client

    @abstractmethod
    def send_email(self, email: EmailSchema) -> None:
        raise NotImplementedError

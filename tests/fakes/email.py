from src.core.interfaces.email import EmailClient, EmailService
from src.core.schemas.email import EmailSchema


class FakeEmailClient(EmailClient):
    def __init__(self) -> None:
        self.inbox: list = []

    def send(self, email: EmailSchema, body: str) -> None:
        self.inbox.append((email, body))


class FakeEmailService(EmailService):
    def __init__(self) -> None:
        self.client = FakeEmailClient()

    def send_email(self, email: EmailSchema) -> None:
        self.client.send(email, "fake body")

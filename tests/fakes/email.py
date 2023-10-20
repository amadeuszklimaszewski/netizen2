from src.core.interfaces.email import EmailClient, EmailSender, EmailService
from src.core.schemas.email import EmailSchema


class FakeEmailClient(EmailClient):
    def __init__(self) -> None:
        self.inbox: list = []

    def send(self, schema: EmailSchema, body: str) -> None:
        self.inbox.append((schema, body))


class FakeEmailService(EmailService):
    def __init__(self) -> None:
        self.client = FakeEmailClient()

    def send_email(self, schema: EmailSchema) -> None:
        self.client.send(schema, "fake body")


class FakeEmailSender(EmailSender):
    def send(self, schema: EmailSchema):
        service = FakeEmailService()
        service.send_email(schema)

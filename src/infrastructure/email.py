import logging
import smtplib
from email.message import EmailMessage
from typing import Any

from jinja2 import Template

from src.core.interfaces.email import EmailClient as IEmailClient
from src.core.interfaces.email import EmailService as IEmailService
from src.core.schemas.email import EmailSchema
from src.settings import settings


class ConsoleEmailClient(IEmailClient):
    def send(self, schema: EmailSchema, body: str) -> None:
        logging.info(schema, body)


class MailHogEmailClient(IEmailClient):
    def __init__(self) -> None:
        self.server = settings.MAIL_SERVER
        self.port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD

    def send(self, schema: EmailSchema, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = schema.from_email
        msg["To"] = ", ".join(schema.recipients)
        msg["Subject"] = schema.subject
        msg.add_alternative(body, subtype="html")

        self._send_message(msg)

    def _send_message(self, message: EmailMessage):
        with smtplib.SMTP(self.server, self.port) as smtp_server:
            smtp_server.login(self.username, self.password)
            smtp_server.send_message(message)


class EmailService(IEmailService):
    def __init__(self, client: IEmailClient) -> None:
        self.client = client

    def send_email(self, schema: EmailSchema) -> None:
        template: Template = self._get_html_template(schema.template_name)
        body = self._render_template(template, schema.context)

        self.client.send(schema, body)

    @classmethod
    def _get_html_template(cls, template_name) -> Template:
        with open(settings.TEMPLATE_FOLDER / template_name, "r") as template_file:
            template = Template(template_file.read())
        return template

    @classmethod
    def _render_template(cls, template: Template, context: dict[str, Any]) -> str:
        return template.render(**context)

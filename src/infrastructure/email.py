import logging
from typing import Any

from jinja2 import Template

from src.core.interfaces.email import EmailClient as IEmailClient
from src.core.interfaces.email import EmailService as IEmailService
from src.core.schemas.email import EmailSchema
from src.settings import settings


class ConsoleEmailClient(IEmailClient):
    def send(self, email: EmailSchema, body: str) -> None:
        logging.info(email, body)


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

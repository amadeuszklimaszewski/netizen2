from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    MAIL_FROM: str = "default@example.com"
    MAIL_FROM_NAME: str = "netizen team"

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str

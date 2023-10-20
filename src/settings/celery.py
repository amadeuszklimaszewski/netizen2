from pydantic_settings import BaseSettings


class CelerySettings(BaseSettings):
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    CELERY_ACCEPT_CONTENT: list[str] = [
        "application/json",
        "application/x-python-serialize",
        "pickle",
    ]

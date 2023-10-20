from pathlib import Path

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    ENVIRONMENT: str = "development"

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS_COUNT: int = 1
    RELOAD: bool = False

    BASE_DIR: Path = Path(__file__).parents[1]
    TEMPLATE_FOLDER: Path = BASE_DIR / "templates"

    MINIMUM_YEAR_OF_BIRTH: int = 1900
    MINIMUM_AGE: int = 18

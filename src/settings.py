from pydantic import BaseSettings


class AppSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS_COUNT: int = 1
    RELOAD: bool = False


class DatabaseSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DATABASE: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int

    TESTING: bool = False

    @property
    def postgres_url(self) -> str:
        database_name = "test" if self.TESTING else self.POSTGRES_DATABASE
        driver = "postgresql+asyncpg"
        return (
            f"{driver}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{database_name}"
        )


class Settings(AppSettings, DatabaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore

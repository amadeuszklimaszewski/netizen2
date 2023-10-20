from pydantic_settings import BaseSettings


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

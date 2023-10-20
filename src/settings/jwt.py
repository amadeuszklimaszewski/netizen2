from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    JWT_SECRET_KEY: str
    HASHING_ALGORITHM: str = "HS256"
    JWT_EXPIRE_TIME: int = 24 * 60 * 60

from datetime import datetime, timedelta

from passlib.context import CryptContext

from src.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_jwt_expire_time(expire_in_seconds: int = settings.JWT_EXPIRE_TIME) -> datetime:
    return datetime.utcnow() + timedelta(seconds=expire_in_seconds)

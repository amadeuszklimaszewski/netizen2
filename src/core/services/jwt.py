from jose import JWTError, jwt

from src.core.exceptions import InvalidCredentialsError
from src.core.schemas.jwt import JWTPayload
from src.settings import settings

_JWT_ALGORITHM = settings.HASHING_ALGORITHM
_SECRET_KEY = settings.JWT_SECRET_KEY


def encode_jwt(payload: JWTPayload, algorithm: str = _JWT_ALGORITHM) -> str:
    """
    Encode JWT payload with secret key and algorithm.

    :param payload: JWT payload
    :param algorithm: JWT algorithm
    :return: JWT token
    """
    to_encode = payload.dict()
    to_encode["sub"] = str(to_encode["sub"])

    return jwt.encode(to_encode, _SECRET_KEY, algorithm=algorithm)


def decode_jwt(
    token: str,
    algorithms: str | list[str] = _JWT_ALGORITHM,
    key: str = _SECRET_KEY,
) -> JWTPayload:
    """
    Decode JWT token with key and algorithm.

    :param token: JWT token
    :param algorithms: JWT algorithms
    :param key: JWT secret key
    :return: JWT payload

    :raises InvalidCredentialsError: if token is invalid
    """
    try:
        payload = jwt.decode(token, key, algorithms=algorithms)
        if not payload:
            raise InvalidCredentialsError
    except JWTError:
        raise InvalidCredentialsError

    return JWTPayload(**payload)

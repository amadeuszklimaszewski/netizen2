from uuid import uuid4

import pytest
from jose import jwt

from src.core.exceptions import InvalidCredentialsError
from src.core.schemas.jwt import JWTPayload
from src.core.services.jwt import decode_jwt, encode_jwt
from src.settings import settings


def test_encode_jwt():
    payload = JWTPayload(sub=uuid4())

    token = encode_jwt(payload)

    assert token is not None


def test_decode_jwt():
    sub = uuid4()
    payload = JWTPayload(sub=sub)

    token = encode_jwt(payload)
    payload = decode_jwt(token)

    assert payload.sub == sub


def test_decode_jwt_empty_token():
    token = jwt.encode(
        {},
        settings.JWT_SECRET_KEY,
        algorithm=settings.HASHING_ALGORITHM,
    )
    with pytest.raises(InvalidCredentialsError):
        decode_jwt(token)


def test_decode_jwt_invalid_token():
    with pytest.raises(InvalidCredentialsError):
        decode_jwt("invalid_token")

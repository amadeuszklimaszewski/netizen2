from pydantic import BaseModel


class AccessToken(BaseModel):
    token: str
    type: str


class UserCredentials(BaseModel):
    email: str
    password: str

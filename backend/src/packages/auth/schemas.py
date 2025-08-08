from pydantic import BaseModel


class LoginInfo(BaseModel):
    email: str
    password: str


class CreateInfo(BaseModel):
    email: str
    password: str

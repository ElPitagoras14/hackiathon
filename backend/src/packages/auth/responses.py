from pydantic import BaseModel

from ...utils.responses import SuccessResponse


class Tokens(BaseModel):
    access: str
    refresh: str


class TokenOut(SuccessResponse):
    payload: Tokens | None

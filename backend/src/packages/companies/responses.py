from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from utils.responses import SuccessResponse


class Company(BaseModel):
    id: int
    user_id: UUID
    name: str
    ruc: str
    ig_url: str
    industry: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class CompanyList(BaseModel):
    items: list[Company]
    total: int


class CompanyListOut(SuccessResponse):
    payload: CompanyList | None


class Task(BaseModel):
    id: str | None


class TaskOut(SuccessResponse):
    payload: Task | None


class CreditRequest(BaseModel):
    id: int
    company_id: int
    amount: float
    reason: str
    status: str
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class CreditRequestList(BaseModel):
    items: list[CreditRequest]
    total: int


class CreditRequestOut(SuccessResponse):
    payload: CreditRequestList | None

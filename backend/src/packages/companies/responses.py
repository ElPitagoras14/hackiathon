from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ...utils.responses import SuccessResponse


class FinancialInfo(BaseModel):
    id: UUID
    company_id: int
    account_status: str | None
    status: str
    average_cash_flow: float | None
    debt_ratio: float | None
    income_variability: float | None
    platform_reviews: float | None
    social_media_activity: float | None
    suppliers_reviews: float | None
    customer_reviews: float | None
    payment_compliance: float | None
    on_time_delivery: float | None
    income_simulation: float | None
    reputation_simulation: float | None
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Company(BaseModel):
    id: int
    user_id: UUID
    name: str
    ruc: str
    ig_url: str
    industry: str
    financial_info: FinancialInfo | None

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
    reason: str | None
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

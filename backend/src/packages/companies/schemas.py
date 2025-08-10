from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CompanyInfo(BaseModel):
    name: str
    ruc: str
    ig_url: str
    industry: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class CreditRequestInfo(BaseModel):
    company_id: int
    amount: float

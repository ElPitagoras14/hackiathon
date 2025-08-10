from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    companies = relationship("Company", back_populates="user")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255))
    ruc = Column(String(50), nullable=False)
    ig_url = Column(String(255), nullable=False)

    user = relationship("User", back_populates="companies")
    financial_info = relationship(
        "FinancialInfo", back_populates="company", cascade="all, delete-orphan"
    )
    credit_requests = relationship(
        "CreditRequest", back_populates="company", cascade="all, delete-orphan"
    )


class FinancialInfo(Base):
    __tablename__ = "financial_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    account_status = Column(String(100))
    status = Column(String(100), default="PENDING")
    average_cash_flow = Column(Float)
    debt_ratio = Column(Float)
    income_variability = Column(Float)
    platform_reviews = Column(Float)
    social_media_activity = Column(Float)
    suppliers_reviews = Column(Float)
    customer_reviews = Column(Float)
    payment_compliance = Column(Float)
    on_time_delivery = Column(Float)
    income_simulation = Column(Float)
    reputation_simulation = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="financial_info")


class CreditRequest(Base):
    __tablename__ = "credit_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Float, nullable=False)
    reason = Column(Text)
    status = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="credit_requests")

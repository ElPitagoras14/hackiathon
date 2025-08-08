from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))

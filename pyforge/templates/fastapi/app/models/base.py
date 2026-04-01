"""
Base SQLModel classes with common fields (id, created_at, updated_at).
"""
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    """Adds created_at and updated_at to any model."""

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)


class BaseModel(TimestampMixin, table=False):
    """Abstract base — inherit from this for all your DB models."""

    id: int | None = Field(default=None, primary_key=True)

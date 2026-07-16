from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import Base


class SessionModel(Base):
    """Database model for chat sessions."""

    __tablename__ = "sessions"
    from datetime import datetime, UTC

    default=lambda: datetime.now(UTC)
    id: Mapped[str] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
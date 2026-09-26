from datetime import datetime
from typing import ClassVar
from uuid import UUID

from db.base import Base
from sqlalchemy import DateTime, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column


class ChallengeProgress(Base):
    __tablename__ = "challenge_progress"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "people"}

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "people.users.id",
            ondelete="CASCADE",
            name="fk_challenge_progress_user_id",
        ),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    challenge_step: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

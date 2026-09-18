from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy import (
                        BigInteger,
                        DateTime,
                        ForeignKey,
                        Identity,
                        String,
                        Text,
                        text
                        )
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID

from db.base import Base
class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {"schema": "people"}

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "people.users.id",
            ondelete="CASCADE",
            name="fk_sessions_user_id",            
        ),
        nullable=False
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
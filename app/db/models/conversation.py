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
class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = {"schema": "conversations"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "people.users.id",
            ondelete="CASCADE",
            name="fk_conversations_user_id"
        ),
        nullable=False,
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
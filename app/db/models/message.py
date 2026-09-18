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

from .base import Base

#TO DO: put the classes in different files. And put them in a folder models instead.





class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "conversations"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "conversations.conversations.id",
            ondelete="CASCADE",
            name="fk_messages_conversation_id"
        ),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
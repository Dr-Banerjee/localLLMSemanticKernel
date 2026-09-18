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
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "people"}

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid7
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
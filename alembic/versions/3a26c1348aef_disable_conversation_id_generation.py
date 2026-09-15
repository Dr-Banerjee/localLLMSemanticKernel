"""disable conversation id generation

Revision ID: 3a26c1348aef
Revises: a3cc22546569
Create Date: 2026-09-13 23:10:46.472761

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3a26c1348aef'
down_revision: Union[str, Sequence[str], None] = 'a3cc22546569'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "conversations",
        "id",
        schema="conversations",
        server_default=None,
    )

    op.execute(
        "DROP SEQUENCE IF EXISTS "
        "conversations.conversations_id_seq"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "CREATE SEQUENCE conversations.conversations_id_seq "
        "AS bigint"
    )

    op.execute(
        "ALTER SEQUENCE conversations.conversations_id_seq "
        "OWNED BY conversations.conversations.id"
    )

    op.alter_column(
        "conversations",
        "id",
        schema="conversations",
        server_default=op.inline_literal(
            "nextval('conversations.conversations_id_seq'::regclass)"
        ),
    )

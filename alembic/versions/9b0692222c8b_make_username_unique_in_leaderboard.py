"""Make username unique in leaderboard

Revision ID: 9b0692222c8b
Revises: c80cbbd407e0
Create Date: 2025-07-30 00:11:18.906817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b0692222c8b'
down_revision: Union[str, Sequence[str], None] = 'c80cbbd407e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_leaderboard_username", "leaderboard", ["username"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass

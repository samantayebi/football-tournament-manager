"""add champion_team_id to tournaments

Revision ID: add_champion_team_id
Revises: 973090c6169a
Create Date: 2026-02-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_champion_team_id"
down_revision: Union[str, Sequence[str], None] = "973090c6169a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tournaments",
        sa.Column("champion_team_id", sa.String(length=36), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tournaments", "champion_team_id")

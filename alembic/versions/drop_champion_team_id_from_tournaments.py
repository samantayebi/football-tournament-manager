"""drop champion_team_id from tournaments

Revision ID: drop_champion_team_id
Revises: add_champion_team_id
Create Date: 2026-02-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "drop_champion_team_id"
down_revision: Union[str, Sequence[str], None] = "add_champion_team_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("tournaments", "champion_team_id")


def downgrade() -> None:
    op.add_column(
        "tournaments",
        sa.Column("champion_team_id", sa.String(length=36), nullable=True),
    )

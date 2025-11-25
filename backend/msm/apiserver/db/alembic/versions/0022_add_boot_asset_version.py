"""add boot asset version column

Revision ID: 0022
Revises: 0021
Create Date: 2025-02-19 00:00:00.000000+00:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0022"
down_revision: str | None = "0021"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("boot_asset", sa.Column("version", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("boot_asset", "version")

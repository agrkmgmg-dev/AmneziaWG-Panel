"""Add optional AmneziaWG preshared key to peers."""

from alembic import op
import sqlalchemy as sa

revision = "4c8d1e2f3a5b"
down_revision = "3b7c9d1a2e4f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("peers", sa.Column("preshared_key", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("peers", "preshared_key")

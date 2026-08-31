"""Add one-device binding fields to peers."""

from alembic import op
import sqlalchemy as sa


revision = "3b7c9d1a2e4f"
down_revision = "01fb4405a466"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("peers", sa.Column("device_public_key", sa.String(255), nullable=True))
    op.add_column("peers", sa.Column("device_bound_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_peers_device_public_key", "peers", ["device_public_key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_peers_device_public_key", table_name="peers")
    op.drop_column("peers", "device_bound_at")
    op.drop_column("peers", "device_public_key")

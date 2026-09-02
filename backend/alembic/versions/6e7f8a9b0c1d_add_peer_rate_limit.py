"""add per-peer rate limit

Revision ID: 6e7f8a9b0c1d
Revises: 5d9f1a2b3c4e
"""
from alembic import op
import sqlalchemy as sa

revision = "6e7f8a9b0c1d"
down_revision = "5d9f1a2b3c4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "peers",
        sa.Column("rate_limit_mbps", sa.Integer(), nullable=False, server_default="15"),
    )
    op.add_column(
        "peers",
        sa.Column("last_upload_bytes", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "peers",
        sa.Column("last_download_bytes", sa.BigInteger(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("peers", "last_download_bytes")
    op.drop_column("peers", "last_upload_bytes")
    op.drop_column("peers", "rate_limit_mbps")

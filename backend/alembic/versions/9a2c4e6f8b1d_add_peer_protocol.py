"""Add the VPN protocol discriminator to peers.

Revision ID: 9a2c4e6f8b1d
Revises: 6e7f8a9b0c1d
"""

from alembic import op
import sqlalchemy as sa


revision = "9a2c4e6f8b1d"
down_revision = "6e7f8a9b0c1d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing peers are AmneziaWG peers, so the server default also provides
    # a safe value for every existing row during the SQLite migration.
    op.add_column(
        "peers",
        sa.Column(
            "protocol",
            sa.String(length=20),
            nullable=False,
            server_default="amneziawg",
        ),
    )
    op.create_index("ix_peers_protocol", "peers", ["protocol"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_peers_protocol", table_name="peers")
    op.drop_column("peers", "protocol")

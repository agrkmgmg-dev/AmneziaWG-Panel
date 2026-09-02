"""Store AmneziaWG I1 client parameter."""
from alembic import op
import sqlalchemy as sa

revision = "5d9f1a2b3c4e"
down_revision = "4c8d1e2f3a5b"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("peers", sa.Column("amnezia_i1", sa.String(512), nullable=True))

def downgrade() -> None:
    op.drop_column("peers", "amnezia_i1")

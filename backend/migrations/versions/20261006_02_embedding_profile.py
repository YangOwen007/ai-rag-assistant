"""Record embedding compatibility without silently rewriting existing documents."""
from alembic import op
import sqlalchemy as sa

revision = "20261006_02"
down_revision = "20260727_01"
branch_labels = None
depends_on = None


def upgrade():
    # Existing process-random vectors are marked legacy so the API can request reindexing.
    op.add_column("documents", sa.Column("embedding_profile", sa.String(200), nullable=False, server_default="legacy"))


def downgrade():
    op.drop_column("documents", "embedding_profile")

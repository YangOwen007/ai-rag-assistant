"""Align the foreign-key nullability with the ORM document ownership rule."""
from alembic import op
import sqlalchemy as sa

revision = "20261006_03"
down_revision = "20261006_02"
branch_labels = None
depends_on = None


def upgrade():
    # SQLite needs a table rebuild for this constraint; Alembic handles both dialects.
    with op.batch_alter_table("chunks") as batch:
        batch.alter_column("document_id", existing_type=sa.String(36), nullable=False)


def downgrade():
    with op.batch_alter_table("chunks") as batch:
        batch.alter_column("document_id", existing_type=sa.String(36), nullable=True)

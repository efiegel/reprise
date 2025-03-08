"""citation table

Revision ID: 572c84b8233b
Revises: 3fd9ec1e9280
Create Date: 2025-03-02 19:25:08.989809

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "572c84b8233b"
down_revision: Union[str, None] = "3fd9ec1e9280"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "citation",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.add_column(
        "motif", sa.Column("citation_uuid", sa.String(length=36), nullable=True)
    )
    op.create_foreign_key(
        "motif_citation_uuid_fk", "motif", "citation", ["citation_uuid"], ["uuid"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("motif_citation_uuid_fk", "motif", type_="foreignkey")
    op.drop_column("motif", "citation_uuid")
    op.drop_table("citation")
    # ### end Alembic commands ###

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
    op.create_table(
        "citation",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )

    # enable foreign key constraints (not default in sqlite)
    op.execute("PRAGMA foreign_keys = ON;")

    # sqlite doesn't support adding an fk to an existing table: recreate and copy data
    op.create_table(
        "motif_with_citation",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citation_uuid", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.ForeignKeyConstraint(
            ["citation_uuid"],
            ["citation.uuid"],
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )

    op.execute(
        """INSERT INTO motif_with_citation (uuid, content, citation_uuid, created_at)
        SELECT uuid, content, NULL, created_at FROM motif;"""
    )
    op.rename_table("motif", "motif_old")
    op.rename_table("motif_with_citation", "motif")
    op.drop_table("motif_old")


def downgrade() -> None:
    op.create_table(
        "motif_without_citation",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )

    op.execute(
        """INSERT INTO motif_without_citation (uuid, content, created_at)
        SELECT uuid, content, created_at FROM motif;"""
    )
    op.rename_table("motif", "motif_with_citation")
    op.rename_table("motif_without_citation", "motif")
    op.drop_table("motif_with_citation")

    op.drop_table("citation")

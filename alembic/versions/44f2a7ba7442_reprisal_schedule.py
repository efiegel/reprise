"""reprisal_schedule

Revision ID: 44f2a7ba7442
Revises: 5e641ae4295c
Create Date: 2025-04-05 16:17:55.774742

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44f2a7ba7442"
down_revision: Union[str, None] = "5e641ae4295c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "reprisal_schedule",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("reprisal_set_uuid", sa.String(length=36), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("reprisal_schedule")
    # ### end Alembic commands ###

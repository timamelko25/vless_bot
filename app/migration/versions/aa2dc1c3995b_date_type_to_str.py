"""date type to str

Revision ID: aa2dc1c3995b
Revises: 1cdffee0920f
Create Date: 2025-03-08 02:29:08.352731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'aa2dc1c3995b'
down_revision: Union[str, None] = '1cdffee0920f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('keys', 'expires_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('keys', 'expires_at',
               existing_type=sa.String(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    # ### end Alembic commands ###

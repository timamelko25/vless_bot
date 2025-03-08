"""2 new entity and correct types

Revision ID: 1cdffee0920f
Revises: 10d0b7220112
Create Date: 2025-03-08 00:03:32.907307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cdffee0920f'
down_revision: Union[str, None] = '10d0b7220112'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('promocodes',
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('bonus', sa.Float(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('history_payments',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('payment_id', sa.String(), nullable=False),
    sa.Column('sum', sa.Float(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('keys', sa.Column('email', sa.String(), nullable=False))
    op.alter_column('keys', 'id_panel',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    op.add_column('servers', sa.Column('name_in_bot', sa.String(), nullable=False))
    op.add_column('servers', sa.Column('description', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'servers', ['name_in_bot'])
    op.add_column('users', sa.Column('refer_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('count_refer', sa.Integer(), nullable=False))
    op.alter_column('users', 'telegram_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('users', 'balance',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'balance',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('users', 'telegram_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.drop_column('users', 'count_refer')
    op.drop_column('users', 'refer_id')
    op.drop_constraint(None, 'servers', type_='unique')
    op.drop_column('servers', 'description')
    op.drop_column('servers', 'name_in_bot')
    op.alter_column('keys', 'id_panel',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.drop_column('keys', 'email')
    op.drop_table('history_payments')
    op.drop_table('promocodes')
    # ### end Alembic commands ###

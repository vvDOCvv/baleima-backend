"""created AutoTradeModel

Revision ID: 014192fe27e3
Revises: 0f4cdeae1d5a
Create Date: 2024-02-15 12:16:28.110894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '014192fe27e3'
down_revision: Union[str, None] = '0f4cdeae1d5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trade_settings',
    sa.Column('auto_trade', sa.Boolean(), nullable=False),
    sa.Column('bif_is_active', sa.Boolean(), nullable=False),
    sa.Column('trade_quantity', sa.Integer(), nullable=False),
    sa.Column('trade_percent', sa.Float(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=False),
    sa.Column('percent_1', sa.Float(), nullable=False),
    sa.Column('percent_2', sa.Float(), nullable=False),
    sa.Column('percent_3', sa.Float(), nullable=False),
    sa.Column('price_1', sa.Float(), nullable=True),
    sa.Column('price_2', sa.Float(), nullable=True),
    sa.Column('price_3', sa.Float(), nullable=True),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trade_settings_id'), 'trade_settings', ['id'], unique=True)
    op.alter_column('user', 'last_paid',
               existing_type=sa.BOOLEAN(),
               type_=sa.String(),
               existing_nullable=True)
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'auto_trade')
    op.drop_column('user', 'symbol_to_trade')
    op.drop_column('user', 'trade_quantity')
    op.drop_column('user', 'trade_percent')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('trade_percent', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('trade_quantity', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('symbol_to_trade', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('auto_trade', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.alter_column('user', 'last_paid',
               existing_type=sa.String(),
               type_=sa.BOOLEAN(),
               existing_nullable=True)
    op.drop_index(op.f('ix_trade_settings_id'), table_name='trade_settings')
    op.drop_table('trade_settings')
    # ### end Alembic commands ###

"""empty message

Revision ID: f23eaec8dd1c
Revises: 
Create Date: 2022-11-07 13:35:18.652077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f23eaec8dd1c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.LargeBinary(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wallets',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, cycle=False), nullable=False),
    sa.Column('funds', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transfers',
    sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, cycle=False), nullable=False),
    sa.Column('from_wallet_id', sa.Integer(), nullable=False),
    sa.Column('to_wallet_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=True),
    sa.Column('datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['from_wallet_id'], ['wallets.id'], ),
    sa.ForeignKeyConstraint(['to_wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transfers')
    op.drop_table('wallets')
    op.drop_table('users')
    # ### end Alembic commands ###
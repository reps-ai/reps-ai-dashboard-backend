"""Add external_call_id to CallLog model

Revision ID: 03ee265cc61d
Revises: 834c466287a3
Create Date: 2025-03-30 13:48:34.282924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03ee265cc61d'
down_revision = '834c466287a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('call_logs', 'campaign_id',
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('call_logs', 'campaign_id',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###

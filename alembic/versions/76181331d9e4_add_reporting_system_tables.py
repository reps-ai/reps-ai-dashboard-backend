"""add_reporting_system_tables

Revision ID: 76181331d9e4
Revises: 6a5d1d486ac8
Create Date: 2025-04-26 20:13:07.384225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76181331d9e4'
down_revision = '6a5d1d486ac8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create report_templates table
    op.create_table('report_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_type', sa.String(length=50), nullable=False),
        sa.Column('template_content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create report_subscriptions table
    op.create_table('report_subscriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('branch_id', sa.UUID(), nullable=False),
        sa.Column('gym_id', sa.UUID(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('template_id', sa.UUID(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('delivery_method', sa.String(length=50), nullable=False, server_default=sa.text("'email'")),
        sa.Column('recipients', sa.JSON(), nullable=False),
        sa.Column('delivery_time', sa.String(length=50), nullable=True),
        sa.Column('delivery_days', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create report_deliveries table
    op.create_table('report_deliveries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('branch_id', sa.UUID(), nullable=False),
        sa.Column('gym_id', sa.UUID(), nullable=False),
        sa.Column('template_id', sa.UUID(), nullable=True),
        sa.Column('recipients', sa.JSON(), nullable=False),
        sa.Column('report_data', sa.JSON(), nullable=True),
        sa.Column('report_period_start', sa.DateTime(), nullable=False),
        sa.Column('report_period_end', sa.DateTime(), nullable=False),
        sa.Column('delivery_status', sa.String(length=50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('delivery_time', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_report_subscriptions_branch_id'), 'report_subscriptions', ['branch_id'], unique=False)
    op.create_index(op.f('ix_report_subscriptions_gym_id'), 'report_subscriptions', ['gym_id'], unique=False)
    op.create_index(op.f('ix_report_subscriptions_report_type'), 'report_subscriptions', ['report_type'], unique=False)
    op.create_index(op.f('ix_report_deliveries_branch_id'), 'report_deliveries', ['branch_id'], unique=False)
    op.create_index(op.f('ix_report_deliveries_delivery_status'), 'report_deliveries', ['delivery_status'], unique=False)
    op.create_index(op.f('ix_report_deliveries_gym_id'), 'report_deliveries', ['gym_id'], unique=False)
    op.create_index(op.f('ix_report_deliveries_report_type'), 'report_deliveries', ['report_type'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('report_deliveries')
    op.drop_table('report_subscriptions')
    op.drop_table('report_templates')

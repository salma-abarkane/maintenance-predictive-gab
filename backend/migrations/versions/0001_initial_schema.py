"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-06-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = '0001_initial_schema'
down_revision = None
branch_labels = None
deepdown = None


def upgrade() -> None:
    op.create_table(
        'cities',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('population', sa.Integer, nullable=False),
        sa.Column('male', sa.Integer, nullable=False),
        sa.Column('female', sa.Integer, nullable=False),
        sa.Column('pct_under15', sa.Float, nullable=False),
        sa.Column('pct_15_59', sa.Float, nullable=False),
        sa.Column('pct_over60', sa.Float, nullable=False)
    )
    op.create_table(
        'agencies',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('city', sa.String, sa.ForeignKey('cities.name'), nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False)
    )
    op.create_table(
        'atms',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('serial', sa.String, nullable=False, unique=True),
        sa.Column('agency_id', sa.Integer, sa.ForeignKey('agencies.id'), nullable=False),
        sa.Column('location', sa.String, nullable=False),
        sa.Column('year_installed', sa.Integer, nullable=False)
    )
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('atm_id', sa.Integer, sa.ForeignKey('atms.id'), nullable=False),
        sa.Column('agency_id', sa.Integer, sa.ForeignKey('agencies.id'), nullable=False),
        sa.Column('city', sa.String, nullable=False),
        sa.Column('category', sa.String, nullable=False),
        sa.Column('severity', sa.String, nullable=False),
        sa.Column('reported_at', sa.DateTime, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('incidents')
    op.drop_table('atms')
    op.drop_table('agencies')
    op.drop_table('cities')

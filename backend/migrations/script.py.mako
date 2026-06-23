"""A generic revision script.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${creation_date}
"""

from alembic import op
import sqlalchemy as sa

revision = '${up_revision}'
down_revision = ${down_revision | repr}
branch_labels = ${branch_labels | repr}
deepdown = ${deepdown | repr}


def upgrade() -> None:
${upgrades if upgrades else '    pass'}


def downgrade() -> None:
${downgrades if downgrades else '    pass'}

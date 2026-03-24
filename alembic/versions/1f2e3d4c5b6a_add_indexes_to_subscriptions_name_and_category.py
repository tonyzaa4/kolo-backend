"""Add indexes to subscriptions.name and subscriptions.category

Revision ID: 1f2e3d4c5b6a
Revises: 6101060e78bd
Create Date: 2026-03-24 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f2e3d4c5b6a'
down_revision: Union[str, Sequence[str], None] = '6101060e78bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_subscriptions_name'), 'subscriptions', ['name'], unique=False)
    op.create_index(op.f('ix_subscriptions_category'), 'subscriptions', ['category'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_subscriptions_category'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_name'), table_name='subscriptions')

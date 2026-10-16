"""add tenant ownership

Revision ID: 318df9280f85
Revises: 5e7fddec696d
Create Date: 2026-10-16 12:48:25.521859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '318df9280f85'
down_revision: Union[str, Sequence[str], None] = '5e7fddec696d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

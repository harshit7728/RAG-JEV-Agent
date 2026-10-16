"""add full text search

Revision ID: 5e7fddec696d
Revises: 5bf5c6642e3e
Create Date: 2026-10-16 11:56:58.436888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e7fddec696d'
down_revision: Union[str, Sequence[str], None] = '5bf5c6642e3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

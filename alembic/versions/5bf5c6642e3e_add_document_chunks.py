"""add document chunks

Revision ID: 5bf5c6642e3e
Revises: 49949dffe9d2
Create Date: 2026-10-15 16:37:59.136024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bf5c6642e3e'
down_revision: Union[str, Sequence[str], None] = '49949dffe9d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

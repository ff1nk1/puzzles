"""merge_heads

Revision ID: c2fc12dfe565
Revises: 7633aa257b1f, 84aad292c8fb
Create Date: 2026-06-28 19:42:52.708109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2fc12dfe565'
down_revision: Union[str, Sequence[str], None] = ('7633aa257b1f', '84aad292c8fb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""comments

Revision ID: 6a8303b72475
Revises: 311247e40726
Create Date: 2024-03-03 10:18:07.802195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a8303b72475'
down_revision: Union[str, None] = '311247e40726'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

"""fix_image_url_nullable

Revision ID: fix_image_url_nullable
Revises: 79680385a11a
Create Date: 2025-12-19 09:49:56.557662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_image_url_nullable'
down_revision: Union[str, Sequence[str], None] = '79680385a11a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Явно указываем схему и тип
    op.execute("""
        ALTER TABLE products 
        ALTER COLUMN image_url DROP NOT NULL
    """)

def downgrade():
    op.execute("""
        ALTER TABLE products 
        ALTER COLUMN image_url SET NOT NULL
    """)
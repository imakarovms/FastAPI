"""make image_url nullable

Revision ID: 79680385a11a
Revises: 338373e1c8c6
Create Date: 2025-12-19 09:22:19.888082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79680385a11a'
down_revision: Union[str, Sequence[str], None] = '338373e1c8c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Изменяем столбец image_url, разрешая NULL значения
    op.alter_column('products', 'image_url',
               existing_type=sa.String(length=100),
               nullable=True)

def downgrade():
    # Восстанавливаем NOT NULL constraint при откате
    op.alter_column('products', 'image_url',
               existing_type=sa.String(length=100),
               nullable=False)
"""Update Region model with hierarchy

Revision ID: ab12cd34ef56
Revises: 60d78f000fc5
Create Date: 2026-01-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'ab12cd34ef56'
down_revision: Union[str, Sequence[str], None] = '60d78f000fc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns
    op.add_column('region', sa.Column('sido', sa.String(length=20), server_default='', nullable=False))
    op.add_column('region', sa.Column('sigugun', sa.String(length=20), server_default='', nullable=False))
    op.add_column('region', sa.Column('dong', sa.String(length=20), server_default='', nullable=False))
    
    # 2. Drop unique constraint/index on name
    op.drop_index('ix_region_name', table_name='region')
    
    # 3. Drop name column
    op.drop_column('region', 'name')
    
    # 4. Remove server_default (optional, but cleaner)
    # in mysql modifying column to remove default
    # op.alter_column('region', 'sido', server_default=None) # Alembic might imply this if not specified? 
    # To be safe, just leaving them is fine or alter them.
    
    # 5. Add new composite unique constraint
    op.create_unique_constraint('uix_region_sido_sigugun_dong', 'region', ['sido', 'sigugun', 'dong'])


def downgrade() -> None:
    op.drop_constraint('uix_region_sido_sigugun_dong', 'region', type_='unique')
    op.add_column('region', sa.Column('name', sa.String(length=20), nullable=False))
    op.create_index('ix_region_name', 'region', ['name'], unique=True)
    op.drop_column('region', 'dong')
    op.drop_column('region', 'sigugun')
    op.drop_column('region', 'sido')

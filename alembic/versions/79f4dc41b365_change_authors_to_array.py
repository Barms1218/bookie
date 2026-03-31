"""change authors to array

Revision ID: 79f4dc41b365
Revises: f776d036ccb8
Create Date: 2026-03-30 21:46:04.798708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '79f4dc41b365'
down_revision: Union[str, Sequence[str], None] = 'f776d036ccb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE books 
        ALTER COLUMN authors TYPE VARCHAR[]
        USING translate(authors::text, '[]', '{}')::VARCHAR[]
    """)

def downgrade() -> None:
    op.execute("""
        ALTER TABLE books
        ALTER COLUMN authors TYPE JSONB
        USING to_jsonb(authors)
    """)

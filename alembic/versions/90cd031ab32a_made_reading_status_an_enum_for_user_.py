"""Made reading status an enum for user books

Revision ID: 90cd031ab32a
Revises: f7b928970bf8
Create Date: 2026-04-05 20:09:22.029327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import ENUM
reading_status_enum = ENUM('want_to_read', 'reading', 'finished', 're_reading', 'did_not_finish', name='reading_status')

# revision identifiers, used by Alembic.
revision: str = '90cd031ab32a'
down_revision: Union[str, Sequence[str], None] = 'f7b928970bf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE TYPE reading_status AS ENUM ('want_to_read', 'reading', 'finished', 're_reading', 'did_not_finish')")
    op.add_column('user_books', sa.Column('reading_status', sa.Enum('want_to_read', 'reading', 'finished', 're_reading', 'did_not_finish', name='reading_status'), nullable=False))

def downgrade():
    op.drop_column('user_books', 'reading_status')
    op.execute("DROP TYPE reading_status")

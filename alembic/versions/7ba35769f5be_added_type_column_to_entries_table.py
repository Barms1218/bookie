"""Added type column to entries table

Revision ID: 7ba35769f5be
Revises: a42a49847558
Create Date: 2026-04-04 22:41:19.979306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

entry_type_enum = ENUM('note', 'quote', 'journal', name='entrytype')

# revision identifiers, used by Alembic.
revision: str = '7ba35769f5be'
down_revision: Union[str, Sequence[str], None] = 'a42a49847558'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE TYPE entrytype AS ENUM ('note', 'quote', 'journal')")
    op.add_column('entries', sa.Column('type', sa.Enum('note', 'quote', 'journal', name='entrytype'), nullable=False))

def downgrade():
    op.drop_column('entries', 'type')
    op.execute("DROP TYPE entrytype")

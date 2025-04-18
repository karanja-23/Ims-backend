"""changes date acquired column to datatype date

Revision ID: 3d070dcbe180
Revises: 776a3000b032
Create Date: 2025-04-01 19:41:56.011313

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3d070dcbe180'
down_revision = '776a3000b032'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventory_items', schema=None) as batch_op:
        batch_op.alter_column('date_acquired',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Date(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventory_items', schema=None) as batch_op:
        batch_op.alter_column('date_acquired',
               existing_type=sa.Date(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    # ### end Alembic commands ###

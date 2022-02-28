"""empty message

Revision ID: 53600bbd3d59
Revises: 7f79bf88f845
Create Date: 2022-02-28 10:07:19.485226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53600bbd3d59'
down_revision = '7f79bf88f845'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('folder_name', sa.String(length=120), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.drop_column('folder_name')

    # ### end Alembic commands ###

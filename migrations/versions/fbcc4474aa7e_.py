"""empty message

Revision ID: fbcc4474aa7e
Revises: 683a2f6b174c
Create Date: 2022-02-17 14:23:24.947034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbcc4474aa7e'
down_revision = '683a2f6b174c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('views', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.drop_column('views')

    # ### end Alembic commands ###
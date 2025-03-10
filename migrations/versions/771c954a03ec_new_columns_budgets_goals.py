"""new columns budgets/goals

Revision ID: 771c954a03ec
Revises: b5847e2bc8b4
Create Date: 2025-02-24 19:37:34.880107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '771c954a03ec'
down_revision = 'b5847e2bc8b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('spent', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('spent_percentage', sa.Float(), nullable=True))

    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('progress', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('goals', schema=None) as batch_op:
        batch_op.drop_column('progress')

    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.drop_column('spent_percentage')
        batch_op.drop_column('spent')

    # ### end Alembic commands ###

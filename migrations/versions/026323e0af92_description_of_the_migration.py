"""Description of the migration

Revision ID: 026323e0af92
Revises: 7f52d4515013
Create Date: 2024-03-13 22:07:13.821880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '026323e0af92'
down_revision = '7f52d4515013'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.TEXT(length=80),
               type_=sa.String(length=80),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.TEXT(length=120),
               type_=sa.String(length=120),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.TEXT(length=80),
               type_=sa.String(length=80),
               existing_nullable=False)
        batch_op.alter_column('exercise_percentage',
               existing_type=sa.FLOAT(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('exercise_percentage',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('password',
               existing_type=sa.String(length=80),
               type_=sa.TEXT(length=80),
               existing_nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.String(length=120),
               type_=sa.TEXT(length=120),
               existing_nullable=False)
        batch_op.alter_column('name',
               existing_type=sa.String(length=80),
               type_=sa.TEXT(length=80),
               existing_nullable=False)

    # ### end Alembic commands ###

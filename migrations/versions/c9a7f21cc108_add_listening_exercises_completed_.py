"""Add listening_exercises_completed column to User table

Revision ID: c9a7f21cc108
Revises: 
Create Date: 2024-03-09 21:34:22.554610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9a7f21cc108'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('listening_exercises_completed', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('listening_quizzes_completed', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('listening_audio_completed', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('interactive_lessons_completed', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('speaking_practice_completed', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('speaking_practice_completed')
        batch_op.drop_column('interactive_lessons_completed')
        batch_op.drop_column('listening_audio_completed')
        batch_op.drop_column('listening_quizzes_completed')
        batch_op.drop_column('listening_exercises_completed')

    # ### end Alembic commands ###
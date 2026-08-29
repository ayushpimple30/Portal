"""Add lesson delivery metadata and timed quiz attempt fields.

Revision ID: 20260828_phase3
Revises: 
"""
from alembic import op
import sqlalchemy as sa
revision = '20260828_phase3'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('lessons') as batch:
        batch.add_column(sa.Column('slug', sa.String(length=200), nullable=True))
        batch.add_column(sa.Column('knowledge_question', sa.String(length=500), nullable=True))
        batch.add_column(sa.Column('knowledge_answer', sa.String(length=500), nullable=True))
        batch.add_column(sa.Column('knowledge_explanation', sa.Text(), nullable=True))
        batch.add_column(sa.Column('video_url', sa.String(length=500), nullable=True))
        batch.add_column(sa.Column('estimated_minutes', sa.Integer(), server_default='8', nullable=False))
        batch.add_column(sa.Column('published', sa.Boolean(), server_default=sa.true(), nullable=False))
    op.create_index('ix_lessons_slug', 'lessons', ['slug'], unique=True)
    op.add_column('quiz_attempts', sa.Column('started_at', sa.DateTime(), nullable=True))
    op.add_column('quiz_attempts', sa.Column('duration_seconds', sa.Integer(), server_default='0', nullable=False))

def downgrade():
    op.drop_column('quiz_attempts', 'duration_seconds'); op.drop_column('quiz_attempts', 'started_at')
    op.drop_index('ix_lessons_slug', table_name='lessons')
    with op.batch_alter_table('lessons') as batch:
        for column in ('published','estimated_minutes','video_url','knowledge_explanation','knowledge_answer','knowledge_question','slug'): batch.drop_column(column)

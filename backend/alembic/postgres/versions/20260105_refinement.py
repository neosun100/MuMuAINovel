"""添加章节优化相关表和字段

Revision ID: 20260105_refinement
Revises: 20260103_foreshadow
Create Date: 2026-01-05
"""
from alembic import op
import sqlalchemy as sa

revision = '20260105_refinement'
down_revision = '20260103_foreshadow'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 创建章节优化记录表
    op.create_table(
        'chapter_refinements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('chapter_id', sa.String(36), sa.ForeignKey('chapters.id', ondelete='CASCADE')),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE')),
        sa.Column('chapter_number', sa.Integer),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('original_content', sa.Text),
        sa.Column('original_word_count', sa.Integer),
        sa.Column('segment1_original', sa.Text),
        sa.Column('segment1_refined', sa.Text),
        sa.Column('segment1_word_count', sa.Integer),
        sa.Column('segment2_original', sa.Text),
        sa.Column('segment2_refined', sa.Text),
        sa.Column('segment2_word_count', sa.Integer),
        sa.Column('segment3_original', sa.Text),
        sa.Column('segment3_refined', sa.Text),
        sa.Column('segment3_word_count', sa.Integer),
        sa.Column('refined_content', sa.Text),
        sa.Column('refined_word_count', sa.Integer),
        sa.Column('model_used', sa.String(100)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('current_segment', sa.Integer, default=0),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_chapter_refinements_chapter_id', 'chapter_refinements', ['chapter_id'])
    op.create_index('ix_chapter_refinements_project_id', 'chapter_refinements', ['project_id'])
    op.create_index('ix_chapter_refinements_status', 'chapter_refinements', ['status'])
    
    # 2. 给chapters表添加优化相关字段
    op.add_column('chapters', sa.Column('is_refined', sa.Boolean, default=False))
    op.add_column('chapters', sa.Column('refined_at', sa.DateTime, nullable=True))
    op.add_column('chapters', sa.Column('refinement_id', sa.String(36), nullable=True))
    op.add_column('chapters', sa.Column('refinement_model', sa.String(100), nullable=True))
    op.create_index('ix_chapters_is_refined', 'chapters', ['is_refined'])


def downgrade():
    # 删除chapters表的优化字段
    op.drop_index('ix_chapters_is_refined', 'chapters')
    op.drop_column('chapters', 'refinement_model')
    op.drop_column('chapters', 'refinement_id')
    op.drop_column('chapters', 'refined_at')
    op.drop_column('chapters', 'is_refined')
    
    # 删除优化记录表
    op.drop_index('ix_chapter_refinements_status', 'chapter_refinements')
    op.drop_index('ix_chapter_refinements_project_id', 'chapter_refinements')
    op.drop_index('ix_chapter_refinements_chapter_id', 'chapter_refinements')
    op.drop_table('chapter_refinements')

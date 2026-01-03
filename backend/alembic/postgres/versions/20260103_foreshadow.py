"""添加伏笔管理表

Revision ID: 20260103_foreshadow
Revises: 
Create Date: 2026-01-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260103_foreshadow'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'foreshadows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('foreshadow_type', sa.String(50), default='plot'),
        sa.Column('status', sa.String(20), default='planted', index=True),
        sa.Column('importance', sa.Integer, default=5),
        sa.Column('planted_chapter_id', sa.String(36), sa.ForeignKey('chapters.id', ondelete='SET NULL')),
        sa.Column('planted_chapter_number', sa.Integer),
        sa.Column('planted_content', sa.Text),
        sa.Column('planted_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('resolved_chapter_id', sa.String(36), sa.ForeignKey('chapters.id', ondelete='SET NULL')),
        sa.Column('resolved_chapter_number', sa.Integer),
        sa.Column('resolved_content', sa.Text),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('related_characters', sa.JSON, default=[]),
        sa.Column('related_foreshadows', sa.JSON, default=[]),
        sa.Column('tags', sa.JSON, default=[]),
        sa.Column('remind_before_chapters', sa.Integer, default=5),
        sa.Column('auto_remind', sa.Integer, default=1),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # 创建索引
    op.create_index('ix_foreshadows_project_status', 'foreshadows', ['project_id', 'status'])
    op.create_index('ix_foreshadows_resolved_chapter', 'foreshadows', ['resolved_chapter_number'])


def downgrade() -> None:
    op.drop_index('ix_foreshadows_resolved_chapter')
    op.drop_index('ix_foreshadows_project_status')
    op.drop_table('foreshadows')

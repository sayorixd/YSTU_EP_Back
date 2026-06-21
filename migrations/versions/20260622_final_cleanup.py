"""Final cleanup of has_* fields and cascade fixes

Revision ID: 20260622_final_cleanup
Revises: ba33b6a80f88
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa

revision = '20260622_final_cleanup'
down_revision = 'ba33b6a80f88' # <-- ВАШ ТЕКУЩИЙ HEAD
branch_labels = None
depends_on = None

def upgrade():
    # 1. Удаляем мусорные колонки has_* из БД
    op.drop_column('discipline_blocks', 'has_course_project')
    op.drop_column('discipline_blocks', 'has_course_work')
    op.drop_column('discipline_blocks', 'has_rz')
    op.drop_column('discipline_blocks', 'has_rgr')
    op.drop_column('discipline_blocks', 'has_referat')

    # 2. Чиним каскадное удаление для направлений (решает проблему удаления направления)
    op.drop_constraint('direction_map_cors_direction_id_fkey', 'direction_map_cors', type_='foreignkey')
    op.create_foreign_key(
        'direction_map_cors_direction_id_fkey',
        'direction_map_cors', 'directions',
        ['direction_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    op.drop_constraint('direction_map_cors_direction_id_fkey', 'direction_map_cors', type_='foreignkey')
    op.create_foreign_key(
        'direction_map_cors_direction_id_fkey',
        'direction_map_cors', 'directions',
        ['direction_id'], ['id']
    )

    op.add_column('discipline_blocks', sa.Column('has_referat', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('discipline_blocks', sa.Column('has_rgr', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('discipline_blocks', sa.Column('has_rz', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('discipline_blocks', sa.Column('has_course_work', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('discipline_blocks', sa.Column('has_course_project', sa.Boolean(), nullable=False, server_default=sa.false()))
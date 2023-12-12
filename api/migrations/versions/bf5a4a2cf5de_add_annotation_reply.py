"""add-annotation-reply

Revision ID: bf5a4a2cf5de
Revises: fca025d3b60f
Create Date: 2023-12-11 08:50:51.301231

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bf5a4a2cf5de'
down_revision = 'fca025d3b60f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_annotation_hit_histories',
    sa.Column('id', postgresql.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('app_id', postgresql.UUID(), nullable=False),
    sa.Column('annotation_id', postgresql.UUID(), nullable=False),
    sa.Column('source', sa.Text(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('account_id', postgresql.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP(0)'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='app_annotation_hit_histories_pkey')
    )
    with op.batch_alter_table('app_annotation_hit_histories', schema=None) as batch_op:
        batch_op.create_index('app_annotation_hit_histories_account_idx', ['account_id'], unique=False)
        batch_op.create_index('app_annotation_hit_histories_annotation_idx', ['annotation_id'], unique=False)
        batch_op.create_index('app_annotation_hit_histories_app_idx', ['app_id'], unique=False)

    with op.batch_alter_table('app_model_configs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('annotation_reply', sa.Text(), nullable=True))

    with op.batch_alter_table('dataset_collection_bindings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.String(length=40), server_default=sa.text("'dataset'::character varying"), nullable=False))

    with op.batch_alter_table('message_annotations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('question', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('hit_count', sa.Integer(), nullable=False))
        batch_op.alter_column('conversation_id',
               existing_type=postgresql.UUID(),
               nullable=True)
        batch_op.alter_column('message_id',
               existing_type=postgresql.UUID(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message_annotations', schema=None) as batch_op:
        batch_op.alter_column('message_id',
               existing_type=postgresql.UUID(),
               nullable=False)
        batch_op.alter_column('conversation_id',
               existing_type=postgresql.UUID(),
               nullable=False)
        batch_op.drop_column('hit_count')
        batch_op.drop_column('question')

    with op.batch_alter_table('dataset_collection_bindings', schema=None) as batch_op:
        batch_op.drop_column('type')

    with op.batch_alter_table('app_model_configs', schema=None) as batch_op:
        batch_op.drop_column('annotation_reply')

    with op.batch_alter_table('app_annotation_hit_histories', schema=None) as batch_op:
        batch_op.drop_index('app_annotation_hit_histories_app_idx')
        batch_op.drop_index('app_annotation_hit_histories_annotation_idx')
        batch_op.drop_index('app_annotation_hit_histories_account_idx')

    op.drop_table('app_annotation_hit_histories')
    # ### end Alembic commands ###

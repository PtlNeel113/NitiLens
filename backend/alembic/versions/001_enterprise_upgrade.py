"""Enterprise upgrade: scan history and review logs

Revision ID: 001_enterprise_upgrade
Revises: 
Create Date: 2026-02-21 20:51:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_enterprise_upgrade'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scan_history table
    op.create_table(
        'scan_history',
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_type', sa.String(length=50), nullable=True),
        sa.Column('initiated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('policies_scanned', sa.Integer(), nullable=True),
        sa.Column('rules_executed', sa.Integer(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True),
        sa.Column('violations_detected', sa.Integer(), nullable=True),
        sa.Column('critical_violations', sa.Integer(), nullable=True),
        sa.Column('high_violations', sa.Integer(), nullable=True),
        sa.Column('medium_violations', sa.Integer(), nullable=True),
        sa.Column('low_violations', sa.Integer(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_trend', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.org_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('scan_id')
    )
    op.create_index(op.f('ix_scan_history_org_id'), 'scan_history', ['org_id'], unique=False)
    op.create_index(op.f('ix_scan_history_created_at'), 'scan_history', ['created_at'], unique=False)
    op.create_index(op.f('ix_scan_history_risk_score'), 'scan_history', ['risk_score'], unique=False)
    op.create_index(op.f('ix_scan_history_scan_id'), 'scan_history', ['scan_id'], unique=False)

    # Create review_logs table
    op.create_table(
        'review_logs',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('violation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_role', sa.Enum('SUPER_ADMIN', 'COMPLIANCE_ADMIN', 'REVIEWER', 'VIEWER', name='userrole'), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('previous_status', sa.Enum('PENDING', 'REVIEWED', 'RESOLVED', 'FALSE_POSITIVE', name='violationstatus'), nullable=False),
        sa.Column('new_status', sa.Enum('PENDING', 'REVIEWED', 'RESOLVED', 'FALSE_POSITIVE', name='violationstatus'), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('supporting_evidence', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=False),
        sa.Column('time_to_review_hours', sa.Float(), nullable=True),
        sa.Column('risk_score_before', sa.Float(), nullable=True),
        sa.Column('risk_score_after', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.org_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['violation_id'], ['violations.violation_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_review_logs_org_id'), 'review_logs', ['org_id'], unique=False)
    op.create_index(op.f('ix_review_logs_reviewed_at'), 'review_logs', ['reviewed_at'], unique=False)
    op.create_index(op.f('ix_review_logs_violation_id'), 'review_logs', ['violation_id'], unique=False)

    # Add new columns to violations table
    op.add_column('violations', sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('violations', sa.Column('explanation_text', sa.Text(), nullable=False, server_default=''))
    op.add_column('violations', sa.Column('field_evaluated', sa.String(length=255), nullable=True))
    op.add_column('violations', sa.Column('actual_value', sa.String(length=1000), nullable=True))
    op.add_column('violations', sa.Column('expected_condition', sa.String(length=500), nullable=True))
    op.add_column('violations', sa.Column('policy_reference', sa.String(length=500), nullable=True))
    op.add_column('violations', sa.Column('first_detected_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')))
    op.add_column('violations', sa.Column('last_detected_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')))
    op.add_column('violations', sa.Column('occurrence_count', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('violations', sa.Column('is_recurring', sa.Boolean(), nullable=True, server_default='false'))
    
    op.create_foreign_key('fk_violations_scan_id', 'violations', 'scan_history', ['scan_id'], ['scan_id'])
    op.create_index(op.f('ix_violations_scan_id'), 'violations', ['scan_id'], unique=False)
    op.create_index(op.f('ix_violations_first_detected_at'), 'violations', ['first_detected_at'], unique=False)
    op.create_index(op.f('ix_violations_is_recurring'), 'violations', ['is_recurring'], unique=False)


def downgrade() -> None:
    # Drop indexes and columns from violations
    op.drop_index(op.f('ix_violations_is_recurring'), table_name='violations')
    op.drop_index(op.f('ix_violations_first_detected_at'), table_name='violations')
    op.drop_index(op.f('ix_violations_scan_id'), table_name='violations')
    op.drop_constraint('fk_violations_scan_id', 'violations', type_='foreignkey')
    
    op.drop_column('violations', 'is_recurring')
    op.drop_column('violations', 'occurrence_count')
    op.drop_column('violations', 'last_detected_at')
    op.drop_column('violations', 'first_detected_at')
    op.drop_column('violations', 'policy_reference')
    op.drop_column('violations', 'expected_condition')
    op.drop_column('violations', 'actual_value')
    op.drop_column('violations', 'field_evaluated')
    op.drop_column('violations', 'explanation_text')
    op.drop_column('violations', 'scan_id')

    # Drop review_logs table
    op.drop_index(op.f('ix_review_logs_violation_id'), table_name='review_logs')
    op.drop_index(op.f('ix_review_logs_reviewed_at'), table_name='review_logs')
    op.drop_index(op.f('ix_review_logs_org_id'), table_name='review_logs')
    op.drop_table('review_logs')

    # Drop scan_history table
    op.drop_index(op.f('ix_scan_history_scan_id'), table_name='scan_history')
    op.drop_index(op.f('ix_scan_history_risk_score'), table_name='scan_history')
    op.drop_index(op.f('ix_scan_history_created_at'), table_name='scan_history')
    op.drop_index(op.f('ix_scan_history_org_id'), table_name='scan_history')
    op.drop_table('scan_history')

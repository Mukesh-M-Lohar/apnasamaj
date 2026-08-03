"""initial_schema

Revision ID: 100bd314cce7
Revises: 
Create Date: 2026-08-03 11:11:46.851914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '100bd314cce7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Reordered for correct FK dependency resolution ###

    # --- Tier 0: No external dependencies ---
    op.create_table('otp_records',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('mobile', sa.String(length=15), nullable=False),
    sa.Column('otp_hash', sa.String(length=512), nullable=False),
    sa.Column('purpose', sa.String(length=50), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('max_attempts', sa.Integer(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otp_records_mobile'), 'otp_records', ['mobile'], unique=False)
    op.create_table('permissions',
    sa.Column('code', sa.String(length=100), nullable=False),
    sa.Column('display_name', sa.String(length=255), nullable=False),
    sa.Column('module', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)
    op.create_table('tenants',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('logo_url', sa.String(length=512), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('website', sa.String(length=512), nullable=True),
    sa.Column('address_line1', sa.String(length=255), nullable=True),
    sa.Column('address_line2', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('pincode', sa.String(length=10), nullable=True),
    sa.Column('primary_language', sa.String(length=10), nullable=False),
    sa.Column('secondary_language', sa.String(length=10), nullable=True),
    sa.Column('timezone', sa.String(length=50), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('social_links', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenants_slug'), 'tenants', ['slug'], unique=True)
    op.create_table('users',
    sa.Column('mobile', sa.String(length=15), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('avatar_url', sa.String(length=512), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('is_super_admin', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('google_id', sa.String(length=255), nullable=True),
    sa.Column('apple_id', sa.String(length=255), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('apple_id'),
    sa.UniqueConstraint('google_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_mobile'), 'users', ['mobile'], unique=True)

    # --- Tier 1: Depends on tenants (families WITHOUT circular FK to members yet) ---
    op.create_table('families',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('family_code', sa.String(length=50), nullable=True),
    sa.Column('family_head_id', sa.UUID(), nullable=True),
    sa.Column('address_line1', sa.String(length=255), nullable=True),
    sa.Column('address_line2', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('pincode', sa.String(length=10), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('family_code')
    )
    op.create_index('ix_families_tenant_active', 'families', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_families_tenant_id'), 'families', ['tenant_id'], unique=False)
    op.create_table('audit_logs',
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('user_name', sa.String(length=255), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('action', sa.String(length=50), nullable=False),
    sa.Column('entity_type', sa.String(length=50), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('performed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_index('ix_audit_logs_tenant_active', 'audit_logs', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_audit_logs_tenant_id'), 'audit_logs', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_table('committees',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('term_start', sa.Date(), nullable=True),
    sa.Column('term_end', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_committees_tenant_active', 'committees', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_committees_tenant_id'), 'committees', ['tenant_id'], unique=False)
    op.create_table('documents',
    sa.Column('uploaded_by_id', sa.UUID(), nullable=True),
    sa.Column('entity_type', sa.String(length=50), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('file_type', sa.String(length=100), nullable=False),
    sa.Column('file_size', sa.BigInteger(), nullable=False),
    sa.Column('file_url', sa.String(length=512), nullable=False),
    sa.Column('storage_path', sa.String(length=512), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_entity_id'), 'documents', ['entity_id'], unique=False)
    op.create_index('ix_documents_tenant_active', 'documents', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_documents_tenant_id'), 'documents', ['tenant_id'], unique=False)
    op.create_table('facilities',
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('hourly_rate', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_facilities_tenant_active', 'facilities', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_facilities_tenant_id'), 'facilities', ['tenant_id'], unique=False)
    op.create_table('roles',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('display_name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_system', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_tenant_id'), 'roles', ['tenant_id'], unique=False)
    op.create_table('user_sessions',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('device_name', sa.String(length=255), nullable=True),
    sa.Column('device_type', sa.String(length=50), nullable=True),
    sa.Column('os', sa.String(length=100), nullable=True),
    sa.Column('browser', sa.String(length=100), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('refresh_token_hash', sa.String(length=512), nullable=False),
    sa.Column('is_revoked', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)

    # --- Tier 2: members depends on tenants + users + families ---
    op.create_table('members',
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('family_id', sa.UUID(), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('middle_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('photo_url', sa.String(length=512), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('anniversary_date', sa.Date(), nullable=True),
    sa.Column('occupation', sa.String(length=255), nullable=True),
    sa.Column('education', sa.String(length=255), nullable=True),
    sa.Column('company', sa.String(length=255), nullable=True),
    sa.Column('blood_group', sa.String(length=5), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('mobile', sa.String(length=15), nullable=True),
    sa.Column('alternate_mobile', sa.String(length=15), nullable=True),
    sa.Column('address_line1', sa.String(length=255), nullable=True),
    sa.Column('address_line2', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('pincode', sa.String(length=10), nullable=True),
    sa.Column('emergency_contact_name', sa.String(length=255), nullable=True),
    sa.Column('emergency_contact_mobile', sa.String(length=15), nullable=True),
    sa.Column('emergency_contact_relation', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('membership_number', sa.String(length=50), nullable=True),
    sa.Column('membership_expiry', sa.Date(), nullable=True),
    sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('membership_number')
    )
    op.create_index(op.f('ix_members_family_id'), 'members', ['family_id'], unique=False)
    op.create_index(op.f('ix_members_mobile'), 'members', ['mobile'], unique=False)
    op.create_index('ix_members_tenant_active', 'members', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_members_tenant_id'), 'members', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_members_user_id'), 'members', ['user_id'], unique=False)
    # Now that members exists, close the circular FK on families
    op.create_foreign_key('fk_families_family_head_id_members', 'families', 'members', ['family_head_id'], ['id'], ondelete='SET NULL')

    # --- Tier 3: Depends on members / committees / facilities ---
    op.create_table('family_members',
    sa.Column('family_id', sa.UUID(), nullable=False),
    sa.Column('member_id', sa.UUID(), nullable=False),
    sa.Column('related_to_member_id', sa.UUID(), nullable=True),
    sa.Column('relationship_type', sa.String(length=50), nullable=False),
    sa.Column('generation', sa.Integer(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['related_to_member_id'], ['members.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_family_members_family_id'), 'family_members', ['family_id'], unique=False)
    op.create_index(op.f('ix_family_members_member_id'), 'family_members', ['member_id'], unique=False)
    op.create_index('ix_family_members_tenant_active', 'family_members', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_family_members_tenant_id'), 'family_members', ['tenant_id'], unique=False)
    op.create_table('volunteers',
    sa.Column('member_id', sa.UUID(), nullable=False),
    sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('availability', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('total_hours', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.Column('total_events', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_volunteers_member_id'), 'volunteers', ['member_id'], unique=False)
    op.create_index('ix_volunteers_tenant_active', 'volunteers', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_volunteers_tenant_id'), 'volunteers', ['tenant_id'], unique=False)
    op.create_table('committee_members',
    sa.Column('committee_id', sa.UUID(), nullable=False),
    sa.Column('member_id', sa.UUID(), nullable=False),
    sa.Column('position', sa.String(length=100), nullable=False),
    sa.Column('responsibilities', sa.Text(), nullable=True),
    sa.Column('joined_date', sa.Date(), nullable=True),
    sa.Column('left_date', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['committee_id'], ['committees.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_committee_members_committee_id'), 'committee_members', ['committee_id'], unique=False)
    op.create_index(op.f('ix_committee_members_member_id'), 'committee_members', ['member_id'], unique=False)
    op.create_index('ix_committee_members_tenant_active', 'committee_members', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_committee_members_tenant_id'), 'committee_members', ['tenant_id'], unique=False)
    op.create_table('complaints',
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'RESOLVED', 'REJECTED', name='complaintstatus'), nullable=False),
    sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='complaintpriority'), nullable=False),
    sa.Column('reporter_id', sa.UUID(), nullable=False),
    sa.Column('assigned_committee_id', sa.UUID(), nullable=True),
    sa.Column('resolution_notes', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['assigned_committee_id'], ['committees.id'], ),
    sa.ForeignKeyConstraint(['reporter_id'], ['members.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_complaints_tenant_active', 'complaints', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_complaints_tenant_id'), 'complaints', ['tenant_id'], unique=False)
    op.create_table('events',
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('start_time', sa.Time(), nullable=True),
    sa.Column('end_time', sa.Time(), nullable=True),
    sa.Column('venue', sa.String(length=255), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('maps_url', sa.String(length=512), nullable=True),
    sa.Column('is_online', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('online_url', sa.String(length=512), nullable=True),
    sa.Column('is_registration_open', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('max_attendees', sa.Integer(), nullable=True),
    sa.Column('registration_deadline', sa.DateTime(timezone=True), nullable=True),
    sa.Column('banner_url', sa.String(length=512), nullable=True),
    sa.Column('gallery_urls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('qr_code_url', sa.String(length=512), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('organizer_id', sa.UUID(), nullable=True),
    sa.Column('committee_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['committee_id'], ['committees.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organizer_id'], ['members.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_events_tenant_active', 'events', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_events_tenant_id'), 'events', ['tenant_id'], unique=False)
    op.create_table('notifications',
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('channel', sa.Enum('PUSH', 'SMS', 'EMAIL', name='notificationchannel'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'SENT', 'FAILED', name='notificationstatus'), nullable=False),
    sa.Column('target_committee_id', sa.UUID(), nullable=True),
    sa.Column('provider_reference', sa.String(length=255), nullable=True),
    sa.Column('sender_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['sender_id'], ['members.id'], ),
    sa.ForeignKeyConstraint(['target_committee_id'], ['committees.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_tenant_active', 'notifications', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_notifications_tenant_id'), 'notifications', ['tenant_id'], unique=False)
    op.create_table('polls',
    sa.Column('question', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('target_committee_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['target_committee_id'], ['committees.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_polls_tenant_active', 'polls', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_polls_tenant_id'), 'polls', ['tenant_id'], unique=False)
    op.create_table('role_permissions',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('permission_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_tenant_roles',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_tenant_roles_tenant_id'), 'user_tenant_roles', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_user_tenant_roles_user_id'), 'user_tenant_roles', ['user_id'], unique=False)
    op.create_table('transactions',
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'SUCCEEDED', 'FAILED', 'REFUNDED', name='transactionstatus'), nullable=False),
    sa.Column('provider', sa.Enum('STRIPE', 'RAZORPAY', 'MANUAL', name='paymentprovider'), nullable=False),
    sa.Column('provider_reference', sa.String(length=255), nullable=True),
    sa.Column('related_entity_type', sa.Enum('DONATION', 'FACILITY_BOOKING', name='entitytype'), nullable=False),
    sa.Column('related_entity_id', sa.Uuid(), nullable=False),
    sa.Column('payer_id', sa.UUID(), nullable=False),
    sa.Column('provider_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['payer_id'], ['members.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider_reference')
    )
    op.create_index('ix_transactions_tenant_active', 'transactions', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_transactions_tenant_id'), 'transactions', ['tenant_id'], unique=False)
    op.create_table('facility_bookings',
    sa.Column('facility_id', sa.UUID(), nullable=False),
    sa.Column('booked_by_id', sa.UUID(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', name='bookingstatus'), nullable=False),
    sa.Column('total_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['booked_by_id'], ['members.id'], ),
    sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_facility_bookings_tenant_active', 'facility_bookings', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_facility_bookings_tenant_id'), 'facility_bookings', ['tenant_id'], unique=False)

    # --- Tier 4: Depends on events / polls ---
    op.create_table('donations',
    sa.Column('member_id', sa.UUID(), nullable=True),
    sa.Column('family_id', sa.UUID(), nullable=True),
    sa.Column('donor_name', sa.String(length=255), nullable=True),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('donation_date', sa.Date(), nullable=False),
    sa.Column('purpose', sa.String(length=100), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('sub_category', sa.String(length=100), nullable=True),
    sa.Column('payment_mode', sa.String(length=50), nullable=False),
    sa.Column('transaction_reference', sa.String(length=255), nullable=True),
    sa.Column('cheque_number', sa.String(length=50), nullable=True),
    sa.Column('bank_name', sa.String(length=255), nullable=True),
    sa.Column('receipt_number', sa.String(length=50), nullable=True),
    sa.Column('receipt_url', sa.String(length=512), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('remarks', sa.Text(), nullable=True),
    sa.Column('event_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('receipt_number')
    )
    op.create_index(op.f('ix_donations_family_id'), 'donations', ['family_id'], unique=False)
    op.create_index(op.f('ix_donations_member_id'), 'donations', ['member_id'], unique=False)
    op.create_index('ix_donations_tenant_active', 'donations', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_donations_tenant_id'), 'donations', ['tenant_id'], unique=False)
    op.create_table('event_registrations',
    sa.Column('event_id', sa.UUID(), nullable=False),
    sa.Column('member_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('check_in_method', sa.String(length=20), nullable=True),
    sa.Column('guests', sa.Integer(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_registrations_event_id'), 'event_registrations', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_registrations_member_id'), 'event_registrations', ['member_id'], unique=False)
    op.create_index('ix_event_registrations_tenant_active', 'event_registrations', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_event_registrations_tenant_id'), 'event_registrations', ['tenant_id'], unique=False)
    op.create_table('volunteer_assignments',
    sa.Column('volunteer_id', sa.UUID(), nullable=False),
    sa.Column('event_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.String(length=100), nullable=True),
    sa.Column('hours', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('attended', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('check_in_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('check_out_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('feedback', sa.Text(), nullable=True),
    sa.Column('certificate_url', sa.String(length=512), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['volunteer_id'], ['volunteers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_volunteer_assignments_event_id'), 'volunteer_assignments', ['event_id'], unique=False)
    op.create_index('ix_volunteer_assignments_tenant_active', 'volunteer_assignments', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_volunteer_assignments_tenant_id'), 'volunteer_assignments', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_volunteer_assignments_volunteer_id'), 'volunteer_assignments', ['volunteer_id'], unique=False)
    op.create_table('poll_options',
    sa.Column('poll_id', sa.UUID(), nullable=False),
    sa.Column('text', sa.String(length=255), nullable=False),
    sa.Column('vote_count', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_poll_options_tenant_active', 'poll_options', ['tenant_id', 'is_deleted'], unique=False)
    op.create_index(op.f('ix_poll_options_tenant_id'), 'poll_options', ['tenant_id'], unique=False)

    # --- Tier 5: Depends on poll_options ---
    op.create_table('poll_votes',
    sa.Column('poll_id', sa.UUID(), nullable=False),
    sa.Column('option_id', sa.UUID(), nullable=False),
    sa.Column('member_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ),
    sa.ForeignKeyConstraint(['option_id'], ['poll_options.id'], ),
    sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('poll_id', 'member_id', name='uix_one_vote_per_member')
    )
    op.create_index(op.f('ix_poll_votes_tenant_id'), 'poll_votes', ['tenant_id'], unique=False)
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_poll_votes_tenant_id'), table_name='poll_votes')
    op.drop_table('poll_votes')
    op.drop_index(op.f('ix_volunteer_assignments_volunteer_id'), table_name='volunteer_assignments')
    op.drop_index(op.f('ix_volunteer_assignments_tenant_id'), table_name='volunteer_assignments')
    op.drop_index('ix_volunteer_assignments_tenant_active', table_name='volunteer_assignments')
    op.drop_index(op.f('ix_volunteer_assignments_event_id'), table_name='volunteer_assignments')
    op.drop_table('volunteer_assignments')
    op.drop_index(op.f('ix_poll_options_tenant_id'), table_name='poll_options')
    op.drop_index('ix_poll_options_tenant_active', table_name='poll_options')
    op.drop_table('poll_options')
    op.drop_index(op.f('ix_event_registrations_tenant_id'), table_name='event_registrations')
    op.drop_index('ix_event_registrations_tenant_active', table_name='event_registrations')
    op.drop_index(op.f('ix_event_registrations_member_id'), table_name='event_registrations')
    op.drop_index(op.f('ix_event_registrations_event_id'), table_name='event_registrations')
    op.drop_table('event_registrations')
    op.drop_index(op.f('ix_donations_tenant_id'), table_name='donations')
    op.drop_index('ix_donations_tenant_active', table_name='donations')
    op.drop_index(op.f('ix_donations_member_id'), table_name='donations')
    op.drop_index(op.f('ix_donations_family_id'), table_name='donations')
    op.drop_table('donations')
    op.drop_index(op.f('ix_user_tenant_roles_user_id'), table_name='user_tenant_roles')
    op.drop_index(op.f('ix_user_tenant_roles_tenant_id'), table_name='user_tenant_roles')
    op.drop_table('user_tenant_roles')
    op.drop_table('role_permissions')
    op.drop_index(op.f('ix_polls_tenant_id'), table_name='polls')
    op.drop_index('ix_polls_tenant_active', table_name='polls')
    op.drop_table('polls')
    op.drop_index(op.f('ix_notifications_tenant_id'), table_name='notifications')
    op.drop_index('ix_notifications_tenant_active', table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_facility_bookings_tenant_id'), table_name='facility_bookings')
    op.drop_index('ix_facility_bookings_tenant_active', table_name='facility_bookings')
    op.drop_table('facility_bookings')
    op.drop_index(op.f('ix_events_tenant_id'), table_name='events')
    op.drop_index('ix_events_tenant_active', table_name='events')
    op.drop_table('events')
    op.drop_index(op.f('ix_complaints_tenant_id'), table_name='complaints')
    op.drop_index('ix_complaints_tenant_active', table_name='complaints')
    op.drop_table('complaints')
    op.drop_index(op.f('ix_committee_members_tenant_id'), table_name='committee_members')
    op.drop_index('ix_committee_members_tenant_active', table_name='committee_members')
    op.drop_index(op.f('ix_committee_members_member_id'), table_name='committee_members')
    op.drop_index(op.f('ix_committee_members_committee_id'), table_name='committee_members')
    op.drop_table('committee_members')
    op.drop_index(op.f('ix_volunteers_tenant_id'), table_name='volunteers')
    op.drop_index('ix_volunteers_tenant_active', table_name='volunteers')
    op.drop_index(op.f('ix_volunteers_member_id'), table_name='volunteers')
    op.drop_table('volunteers')
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_index(op.f('ix_transactions_tenant_id'), table_name='transactions')
    op.drop_index('ix_transactions_tenant_active', table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_roles_tenant_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_family_members_tenant_id'), table_name='family_members')
    op.drop_index('ix_family_members_tenant_active', table_name='family_members')
    op.drop_index(op.f('ix_family_members_member_id'), table_name='family_members')
    op.drop_index(op.f('ix_family_members_family_id'), table_name='family_members')
    op.drop_table('family_members')
    op.drop_index(op.f('ix_facilities_tenant_id'), table_name='facilities')
    op.drop_index('ix_facilities_tenant_active', table_name='facilities')
    op.drop_table('facilities')
    op.drop_index(op.f('ix_documents_tenant_id'), table_name='documents')
    op.drop_index('ix_documents_tenant_active', table_name='documents')
    op.drop_index(op.f('ix_documents_entity_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_committees_tenant_id'), table_name='committees')
    op.drop_index('ix_committees_tenant_active', table_name='committees')
    op.drop_table('committees')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_tenant_id'), table_name='audit_logs')
    op.drop_index('ix_audit_logs_tenant_active', table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_users_mobile'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_tenants_slug'), table_name='tenants')
    op.drop_table('tenants')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')
    op.drop_table('permissions')
    op.drop_index(op.f('ix_otp_records_mobile'), table_name='otp_records')
    op.drop_table('otp_records')
    op.drop_index(op.f('ix_members_user_id'), table_name='members')
    op.drop_index(op.f('ix_members_tenant_id'), table_name='members')
    op.drop_index('ix_members_tenant_active', table_name='members')
    op.drop_index(op.f('ix_members_mobile'), table_name='members')
    op.drop_index(op.f('ix_members_family_id'), table_name='members')
    op.drop_table('members')
    op.drop_index(op.f('ix_families_tenant_id'), table_name='families')
    op.drop_index('ix_families_tenant_active', table_name='families')
    op.drop_table('families')
    # ### end Alembic commands ###

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from apps.api.core.config import get_settings
from apps.api.core.base_model import BaseModel, GlobalBaseModel

# Import all models here so Alembic can discover them
from apps.api.modules.tenant.models import Tenant
from apps.api.modules.auth.models import User, UserSession, OTPRecord, Role, Permission, RolePermission, UserTenantRole
from apps.api.modules.member.models import Member
from apps.api.modules.family.models import Family, FamilyMember
from apps.api.modules.committee.models import Committee, CommitteeMember
from apps.api.modules.donation.models import Donation
from apps.api.modules.event.models import Event, EventRegistration
from apps.api.modules.volunteer.models import Volunteer, VolunteerAssignment
from apps.api.modules.complaint.models import Complaint
from apps.api.modules.document.models import Document
from apps.api.modules.notification.models import Notification, NotificationTemplate
from apps.api.modules.audit.models import AuditLog

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

settings = get_settings()
# Ensure asyncpg is used
db_url = str(settings.DATABASE_URL)
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = [BaseModel.metadata, GlobalBaseModel.metadata]

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

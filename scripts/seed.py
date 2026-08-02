"""
ApnaSamaj – Database Seeder

Populates the PostgreSQL database with mock tenants, members, and facilities
for local development.
"""

import asyncio
import logging
from uuid import uuid4
from passlib.context import CryptContext

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.api.core.config import get_settings
from apps.api.modules.tenant.models import Tenant
from apps.api.modules.member.models import Member, MemberRole, ApprovalStatus
from apps.api.modules.facility.models import Facility

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake = Faker("en_IN")

async def seed_database():
    settings = get_settings()
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        logger.info("Seeding Database...")

        # 1. Create a Tenant (Community)
        tenant_id = uuid4()
        tenant = Tenant(
            id=tenant_id,
            name="ApnaSamaj Demo Community",
            subdomain="demo",
            domain="demo.apnasamaj.local",
            is_active=True,
            created_by=tenant_id,
            updated_by=tenant_id,
        )
        session.add(tenant)
        await session.flush()
        logger.info(f"Created Tenant: {tenant.name} (ID: {tenant.id})")

        # 2. Create Admin Member
        admin_id = uuid4()
        hashed_password = pwd_context.hash("Admin@123")
        
        admin = Member(
            id=admin_id,
            tenant_id=tenant.id,
            first_name="Super",
            last_name="Admin",
            phone_number="+919999999999",
            password_hash=hashed_password,
            role=MemberRole.ADMIN,
            is_active=True,
            approval_status=ApprovalStatus.APPROVED,
            created_by=admin_id,
            updated_by=admin_id,
        )
        session.add(admin)
        await session.flush()
        logger.info(f"Created Admin: +919999999999 (Password: Admin@123)")

        # 3. Create Dummy Members
        for _ in range(10):
            member_id = uuid4()
            member = Member(
                id=member_id,
                tenant_id=tenant.id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=fake.phone_number().replace(" ", ""),
                password_hash=hashed_password,
                role=MemberRole.MEMBER,
                is_active=True,
                approval_status=ApprovalStatus.APPROVED,
                created_by=admin_id,
                updated_by=admin_id,
            )
            session.add(member)
        logger.info("Created 10 Dummy Members.")

        # 4. Create Dummy Facilities
        facilities = [
            {"name": "Grand Community Hall", "capacity": 500, "rate": 5000.00},
            {"name": "Badminton Court", "capacity": 4, "rate": 200.00},
            {"name": "Swimming Pool", "capacity": 50, "rate": 1000.00},
        ]
        
        for f in facilities:
            facility = Facility(
                id=uuid4(),
                tenant_id=tenant.id,
                name=f["name"],
                description=f"A state-of-the-art {f['name'].lower()}.",
                capacity=f["capacity"],
                hourly_rate=f["rate"],
                is_active=True,
                created_by=admin_id,
                updated_by=admin_id,
            )
            session.add(facility)
        logger.info("Created 3 Facilities.")

        await session.commit()
        logger.info("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_database())

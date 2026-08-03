"""
ApnaSamaj – Comprehensive Database Seeder

Populates the PostgreSQL database with mock data across ALL models
for local development.
"""

import asyncio
import logging
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.api.core.config import get_settings

# --- Imports for all modules ---
from apps.api.modules.auth.models import User
from apps.api.modules.committee.models import Committee, CommitteeMember
from apps.api.modules.complaint.models import Complaint
from apps.api.modules.donation.models import Donation
from apps.api.modules.event.models import Event, EventRegistration
from apps.api.modules.facility.models import Facility, FacilityBooking
from apps.api.modules.family.models import Family, FamilyMember
from apps.api.modules.member.models import Member
from apps.api.modules.notification.models import Notification
from apps.api.modules.payment.models import EntityType, PaymentProvider, Transaction, TransactionStatus
from apps.api.modules.poll.models import Poll, PollOption, PollVote
from apps.api.modules.tenant.models import Tenant
from apps.api.modules.volunteer.models import Volunteer, VolunteerAssignment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker("en_IN")


async def seed_database():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        logger.info("Starting Comprehensive Database Seeding...")

        # 1. Tenant (Community)
        tenant_id = uuid4()
        tenant = Tenant(
            id=tenant_id,
            name="ApnaSamaj Demo Community",
            slug="demo",
            is_active=True,
            created_by=tenant_id,
            updated_by=tenant_id,
        )
        session.add(tenant)
        await session.flush()
        logger.info(f"Created Tenant: {tenant.name} (ID: {tenant.id})")

        # 2. Members (Admin + Regular)
        admin_id = uuid4()
        admin_user_id = uuid4()

        admin_user = User(
            id=admin_user_id,
            mobile="+919999999999",
            email="admin@apnasamaj.com",
            full_name="Super Admin",
            is_active=True,
        )
        session.add(admin_user)

        admin = Member(
            id=admin_id,
            tenant_id=tenant.id,
            user_id=admin_user_id,
            first_name="Super",
            last_name="Admin",
            mobile="+919999999999",
            status="active",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(admin)
        await session.flush()

        members = []
        for _ in range(15):
            u_id = uuid4()
            mob = fake.phone_number().replace(" ", "")[:15]
            user = User(id=u_id, mobile=mob, full_name=fake.name())
            session.add(user)
            member = Member(
                id=uuid4(),
                tenant_id=tenant.id,
                user_id=u_id,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                mobile=mob,
                status="active",
                created_by=admin_user_id,
                updated_by=admin_user_id,
            )
            session.add(member)
            members.append(member)

        await session.flush()
        logger.info(f"Created 1 Admin and {len(members)} Members.")

        # 3. Families
        family = Family(
            id=uuid4(),
            tenant_id=tenant.id,
            family_head_id=admin.id,
            name="Admin Household",
            address_line1=fake.address()[:255],
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(family)
        await session.flush()

        family_member = FamilyMember(
            id=uuid4(),
            tenant_id=tenant.id,
            family_id=family.id,
            member_id=members[0].id,
            relationship_type="head",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(family_member)
        logger.info("Created Family linkages.")

        # 4. Committees
        committee = Committee(
            id=uuid4(),
            tenant_id=tenant.id,
            name="Cultural Committee",
            description="Manages festivals and events.",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(committee)
        await session.flush()

        committee_member = CommitteeMember(
            id=uuid4(),
            tenant_id=tenant.id,
            committee_id=committee.id,
            member_id=admin.id,
            position="President",
            joined_date=date.today(),
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(committee_member)
        logger.info("Created Cultural Committee.")

        # 5. Events & Registrations
        today = date.today()
        event = Event(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Diwali Gala 2026",
            description="Annual community Diwali celebration.",
            event_type="festival",
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=10),
            venue="Community Hall",
            committee_id=committee.id,
            status="upcoming",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(event)
        await session.flush()

        registration = EventRegistration(
            id=uuid4(),
            tenant_id=tenant.id,
            event_id=event.id,
            member_id=members[1].id,
            status="registered",
            guests=2,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(registration)
        logger.info("Created Event and Registrations.")

        # 6. Volunteers & Assignments
        volunteer = Volunteer(
            id=uuid4(),
            tenant_id=tenant.id,
            member_id=members[2].id,
            skills=["decoration", "logistics"],
            availability="weekends",
            status="active",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(volunteer)
        await session.flush()

        assignment = VolunteerAssignment(
            id=uuid4(),
            tenant_id=tenant.id,
            volunteer_id=volunteer.id,
            event_id=event.id,
            role="Stage Setup",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(assignment)
        logger.info("Created Volunteer and Assignment.")

        # 7. Donations
        donation = Donation(
            id=uuid4(),
            tenant_id=tenant.id,
            member_id=members[3].id,
            amount=5000.00,
            currency="INR",
            donation_date=today,
            purpose="festival",
            payment_mode="upi",
            status="completed",
            event_id=event.id,
            remarks="For Diwali firecrackers",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(donation)
        logger.info("Created Donations.")

        # 8. Complaints
        complaint = Complaint(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Leaking pipe in Block A",
            description="Water is leaking near the parking area.",
            reporter_id=members[4].id,
            assigned_committee_id=committee.id,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(complaint)
        logger.info("Created Complaints.")

        # 9. Facilities & Bookings
        facility = Facility(
            id=uuid4(),
            tenant_id=tenant.id,
            name="Community Hall",
            description="Main AC Hall",
            capacity=200,
            hourly_rate=1500.00,
            is_active=True,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(facility)
        await session.flush()

        booking = FacilityBooking(
            id=uuid4(),
            tenant_id=tenant.id,
            facility_id=facility.id,
            booked_by_id=members[5].id,
            start_time=datetime.now(UTC) + timedelta(days=2),
            end_time=datetime.now(UTC) + timedelta(days=2, hours=3),
            status="confirmed",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(booking)
        logger.info("Created Facilities and Bookings.")

        # 10. Notifications
        notification = Notification(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Maintenance Drive",
            message="Please clear the parking lot on Sunday.",
            sender_id=admin.id,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(notification)
        logger.info("Created Notifications.")

        # 11. Polls & Votes
        poll = Poll(
            id=uuid4(),
            tenant_id=tenant.id,
            question="Should we install solar panels?",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            is_active=True,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(poll)
        await session.flush()

        opt_yes = PollOption(id=uuid4(), tenant_id=tenant.id, poll_id=poll.id, text="Yes", vote_count=1)
        opt_no = PollOption(id=uuid4(), tenant_id=tenant.id, poll_id=poll.id, text="No", vote_count=0)
        session.add_all([opt_yes, opt_no])
        await session.flush()

        vote = PollVote(
            id=uuid4(),
            tenant_id=tenant.id,
            poll_id=poll.id,
            option_id=opt_yes.id,
            member_id=members[6].id,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(vote)
        logger.info("Created Polls and Votes.")

        # 12. Payments (Transactions)
        transaction = Transaction(
            id=uuid4(),
            tenant_id=tenant.id,
            amount=5000.00,
            currency="INR",
            status=TransactionStatus.SUCCEEDED,
            provider=PaymentProvider.RAZORPAY,
            provider_reference=f"pay_{str(fake.uuid4())[:14]}",
            related_entity_type=EntityType.DONATION,
            related_entity_id=donation.id,
            payer_id=members[3].id,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(transaction)
        logger.info("Created Payment Transactions.")

        await session.commit()
        logger.info("🎉 Database Seeding completely finished! All 12 modules populated.")


if __name__ == "__main__":
    asyncio.run(seed_database())

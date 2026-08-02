"""
ApnaSamaj – Comprehensive Database Seeder

Populates the PostgreSQL database with mock data across ALL models
for local development.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.api.core.config import get_settings

# --- Imports for all modules ---
from apps.api.modules.auth.models import User
from apps.api.modules.tenant.models import Tenant
from apps.api.modules.member.models import Member
from apps.api.modules.family.models import Family, FamilyMember
from apps.api.modules.committee.models import Committee, CommitteeMember
from apps.api.modules.event.models import Event, EventRSVP
from apps.api.modules.volunteer.models import VolunteerTask, TaskAssignment
from apps.api.modules.donation.models import Donation
from apps.api.modules.complaint.models import Complaint
from apps.api.modules.facility.models import Facility, FacilityBooking
from apps.api.modules.notification.models import Notification
from apps.api.modules.poll.models import Poll, PollOption, PollVote
from apps.api.modules.payment.models import Transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker("en_IN")


async def seed_database():
    settings = get_settings()
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
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
            head_member_id=admin.id,
            family_name="Admin Household",
            address=fake.address(),
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
            relation="spouse",
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
            role="head",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(committee_member)
        logger.info("Created Cultural Committee.")

        # 5. Events & RSVPs
        event = Event(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Diwali Gala 2026",
            description="Annual community Diwali celebration.",
            start_time=datetime.now(timezone.utc) + timedelta(days=10),
            end_time=datetime.now(timezone.utc) + timedelta(days=10, hours=5),
            location="Community Hall",
            organizer_committee_id=committee.id,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(event)
        await session.flush()

        rsvp = EventRSVP(
            id=uuid4(),
            tenant_id=tenant.id,
            event_id=event.id,
            member_id=members[1].id,
            status="going",
            guest_count=2,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(rsvp)
        logger.info("Created Event and RSVPs.")

        # 6. Volunteer Tasks
        task = VolunteerTask(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Stage Setup for Diwali",
            description="Help setup the main stage.",
            status="open",
            priority="high",
            associated_event_id=event.id,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(task)
        await session.flush()

        assignment = TaskAssignment(
            id=uuid4(),
            tenant_id=tenant.id,
            task_id=task.id,
            volunteer_id=members[2].id,
            status="accepted",
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(assignment)
        logger.info("Created Volunteer Tasks and Assignments.")

        # 7. Donations
        donation = Donation(
            id=uuid4(),
            tenant_id=tenant.id,
            member_id=members[3].id,
            amount=5000.00,
            currency="INR",
            type="event",
            status="completed",
            event_id=event.id,
            notes="For Diwali firecrackers",
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
            status="open",
            priority="high",
            raised_by_id=members[4].id,
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
            start_time=datetime.now(timezone.utc) + timedelta(days=2),
            end_time=datetime.now(timezone.utc) + timedelta(days=2, hours=3),
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
            channel="push",
            status="sent",
            sender_id=admin_user_id,
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
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            is_active=True,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(poll)
        await session.flush()

        opt_yes = PollOption(
            id=uuid4(), tenant_id=tenant.id, poll_id=poll.id, text="Yes", vote_count=1
        )
        opt_no = PollOption(
            id=uuid4(), tenant_id=tenant.id, poll_id=poll.id, text="No", vote_count=0
        )
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
            status="succeeded",
            provider="razorpay",
            provider_reference=f"pay_{fake.uuid4()[:14]}",
            related_entity_type="donation",
            related_entity_id=donation.id,
            payer_id=members[3].id,
            created_by=admin_user_id,
            updated_by=admin_user_id,
        )
        session.add(transaction)
        logger.info("Created Payment Transactions.")

        await session.commit()
        logger.info(
            "🎉 Database Seeding completely finished! All 12 modules populated."
        )


if __name__ == "__main__":
    asyncio.run(seed_database())

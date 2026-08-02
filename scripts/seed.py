"""
ApnaSamaj – Comprehensive Database Seeder

Populates the PostgreSQL database with mock data across ALL models
for local development.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from passlib.context import CryptContext

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.api.core.config import get_settings

# --- Imports for all modules ---
from apps.api.modules.tenant.models import Tenant
from apps.api.modules.member.models import Member, MemberRole, ApprovalStatus
from apps.api.modules.family.models import Family, FamilyMember, FamilyRelation
from apps.api.modules.committee.models import Committee, CommitteeMember, CommitteeRole
from apps.api.modules.event.models import Event, EventRSVP, RSVPStatus
from apps.api.modules.volunteer.models import VolunteerTask, TaskStatus, TaskPriority, TaskAssignment, AssignmentStatus
from apps.api.modules.donation.models import Donation, DonationStatus, DonationType
from apps.api.modules.complaint.models import Complaint, ComplaintStatus, ComplaintPriority
from apps.api.modules.facility.models import Facility, FacilityBooking, BookingStatus
from apps.api.modules.notification.models import Notification, NotificationChannel, NotificationStatus
from apps.api.modules.poll.models import Poll, PollOption, PollVote
from apps.api.modules.payment.models import Transaction, TransactionStatus, PaymentProvider, EntityType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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
            subdomain="demo",
            domain="demo.apnasamaj.local",
            is_active=True,
            created_by=tenant_id,
            updated_by=tenant_id,
        )
        session.add(tenant)
        await session.flush()
        logger.info(f"Created Tenant: {tenant.name} (ID: {tenant.id})")

        # 2. Members (Admin + Regular)
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

        members = []
        for _ in range(15):
            member = Member(
                id=uuid4(),
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
            created_by=admin_id,
            updated_by=admin_id,
        )
        session.add(family)
        await session.flush()
        
        family_member = FamilyMember(
            id=uuid4(),
            tenant_id=tenant.id,
            family_id=family.id,
            member_id=members[0].id,
            relation=FamilyRelation.SPOUSE,
            created_by=admin_id,
            updated_by=admin_id,
        )
        session.add(family_member)
        logger.info("Created Family linkages.")

        # 4. Committees
        committee = Committee(
            id=uuid4(),
            tenant_id=tenant.id,
            name="Cultural Committee",
            description="Manages festivals and events.",
            created_by=admin_id,
            updated_by=admin_id,
        )
        session.add(committee)
        await session.flush()

        committee_member = CommitteeMember(
            id=uuid4(),
            tenant_id=tenant.id,
            committee_id=committee.id,
            member_id=admin.id,
            role=CommitteeRole.HEAD,
            created_by=admin_id,
            updated_by=admin_id,
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
            created_by=admin_id,
            updated_by=admin_id,
        )
        session.add(event)
        await session.flush()

        rsvp = EventRSVP(
            id=uuid4(),
            tenant_id=tenant.id,
            event_id=event.id,
            member_id=members[1].id,
            status=RSVPStatus.GOING,
            guest_count=2,
            created_by=members[1].id,
            updated_by=members[1].id,
        )
        session.add(rsvp)
        logger.info("Created Event and RSVPs.")

        # 6. Volunteer Tasks
        task = VolunteerTask(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Stage Setup for Diwali",
            description="Help setup the main stage.",
            status=TaskStatus.OPEN,
            priority=TaskPriority.HIGH,
            associated_event_id=event.id,
            created_by=admin_id,
            updated_by=admin_id,
        )
        session.add(task)
        await session.flush()

        assignment = TaskAssignment(
            id=uuid4(),
            tenant_id=tenant.id,
            task_id=task.id,
            volunteer_id=members[2].id,
            status=AssignmentStatus.ACCEPTED,
            created_by=admin_id,
            updated_by=admin_id,
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
            type=DonationType.EVENT,
            status=DonationStatus.COMPLETED,
            event_id=event.id,
            notes="For Diwali firecrackers",
            created_by=members[3].id,
            updated_by=members[3].id,
        )
        session.add(donation)
        logger.info("Created Donations.")

        # 8. Complaints
        complaint = Complaint(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Leaking pipe in Block A",
            description="Water is leaking near the parking area.",
            status=ComplaintStatus.OPEN,
            priority=ComplaintPriority.HIGH,
            raised_by_id=members[4].id,
            assigned_committee_id=committee.id,
            created_by=members[4].id,
            updated_by=members[4].id,
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
            created_by=admin_id,
            updated_by=admin_id,
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
            status=BookingStatus.CONFIRMED,
            created_by=members[5].id,
            updated_by=members[5].id,
        )
        session.add(booking)
        logger.info("Created Facilities and Bookings.")

        # 10. Notifications
        notification = Notification(
            id=uuid4(),
            tenant_id=tenant.id,
            title="Maintenance Drive",
            message="Please clear the parking lot on Sunday.",
            channel=NotificationChannel.PUSH,
            status=NotificationStatus.SENT,
            sender_id=admin_id,
            created_by=admin_id,
            updated_by=admin_id,
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
            created_by=admin_id,
            updated_by=admin_id,
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
            created_by=members[6].id,
            updated_by=members[6].id,
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
            provider_reference=f"pay_{fake.uuid4()[:14]}",
            related_entity_type=EntityType.DONATION,
            related_entity_id=donation.id,
            payer_id=members[3].id,
            created_by=admin_id,
            updated_by=admin_id,
        )
        session.add(transaction)
        logger.info("Created Payment Transactions.")

        await session.commit()
        logger.info("🎉 Database Seeding completely finished! All 12 modules populated.")

if __name__ == "__main__":
    asyncio.run(seed_database())

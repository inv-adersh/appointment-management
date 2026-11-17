from django.db import transaction
from django.utils import timezone

from .models import (
    Appointment,
    AppointmentStatus,
    AppointmentActivity,
    AppointmentAssignment,
    AssignmentStatus,
    ActivityAction,
)

from grpc_client import get_provider_details


def create_appointment(
    customer_id,
    title,
    description,
    scheduled_at,
    duration_minutes
):
    if scheduled_at <= timezone.now():
        raise ValueError("Appointment must be scheduled in the future.")

    if duration_minutes <= 0:
        raise ValueError("Duration must be greater than zero.")

    # 3. Create appointment and activity together
    with transaction.atomic():

        appointment = Appointment.objects.create(
            customer_id=customer_id,
            title=title,
            description=description,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            status=AppointmentStatus.PENDING
        )

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=customer_id,
            actor_role="CUSTOMER",
            action=ActivityAction.CREATED,
            new_value={
                "status": AppointmentStatus.PENDING,
                "title": title
            },
            description="Appointment created"
        )

    return appointment



def get_appointment(appointment_id):
    try:
        return Appointment.objects.get(id=appointment_id)

    except Appointment.DoesNotExist:
        return None


def list_appointments(customer_id=None,status=None,start_date=None,end_date=None):
    appointments = Appointment.objects.all()

    if customer_id is not None:
        appointments = appointments.filter(customer_id=customer_id)

    if status:
        appointments = appointments.filter(status=status)

    if start_date:
        appointments = appointments.filter(scheduled_at__date__gte=start_date)

    if end_date:
        appointments = appointments.filter(scheduled_at__date__lte=end_date)

    return appointments.order_by("-scheduled_at")



def update_appointment(appointment_id, data, actor_id=None):
    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        # Prevent modification of completed or cancelled appointments
        if appointment.status in [
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED
        ]:
            raise ValueError(
                "Completed or cancelled appointments cannot be updated."
            )

        allowed_fields = ["title", "description", "duration_minutes"]

        old_values = {}
        new_values = {}

        for field in allowed_fields:

            if field in data:
                old_value = getattr(appointment, field)
                new_value = data[field]

                if old_value != new_value:
                    old_values[field] = old_value
                    new_values[field] = new_value
                    setattr(appointment, field, new_value)

        # Validate duration if it was changed
        if (
            "duration_minutes" in new_values
            and appointment.duration_minutes <= 0
        ):
            raise ValueError("Duration must be greater than zero.")

        if not new_values:
            return appointment

        appointment.save()

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=actor_id,
            actor_role="CUSTOMER",
            action=ActivityAction.UPDATED,
            old_value=old_values,
            new_value=new_values,
            description="Appointment details updated"
        )

        return appointment


def assign_provider(appointment_id, provider_id, assigned_by=None):

    # Step 1: Check provider through gRPC
    provider = get_provider_details(provider_id)

    if not provider.is_active:
        raise ValueError("Provider is not active.")

    if not provider.is_available:
        raise ValueError("Provider is currently unavailable.")

    # Step 2: Perform appointment database operations
    with transaction.atomic():
        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        # Step 3: Validate appointment status
        allowed_statuses = [
            AppointmentStatus.PENDING,
            AppointmentStatus.REJECTED
        ]

        if appointment.status not in allowed_statuses:
            raise ValueError("Appointment cannot be assigned in its current status.")

        # Step 4: Update previous current assignment, if any
        AppointmentAssignment.objects.filter(
            appointment=appointment,
            is_current=True
        ).update(
            is_current=False,
            status=AssignmentStatus.REPLACED
        )
        # Step 5: Create new assignment
        assignment = AppointmentAssignment.objects.create(
            appointment=appointment,
            provider_id=provider_id,
            assigned_by=assigned_by,
            status=AssignmentStatus.ASSIGNED,
            is_current=True
        )

        # Step 6: Update appointment
        appointment.provider_id = provider_id
        appointment.status = AppointmentStatus.ASSIGNED
        appointment.save(
            update_fields=["provider_id", "status", "updated_at"]
        )

        # Step 7: Create activity history
        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=assigned_by,
            actor_role="ADMIN",
            action=ActivityAction.ASSIGNED,
            old_value=None,
            new_value={
                "provider_id": provider_id,
                "provider_name": provider.name,
                "status": AppointmentStatus.ASSIGNED
            },
            description=f"Appointment assigned to provider {provider.name}"
        )

    return appointment



def accept_appointment(appointment_id, provider_id):

    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        if appointment.provider_id != provider_id:
            raise ValueError("This appointment is not assigned to you.")

        if appointment.status != AppointmentStatus.ASSIGNED:
            raise ValueError("Appointment cannot be accepted.")

        assignment = AppointmentAssignment.objects.get(
            appointment=appointment,
            provider_id=provider_id,
            is_current=True
        )

        appointment.status = AppointmentStatus.ACCEPTED
        appointment.save(update_fields=["status", "updated_at"])

        assignment.status = AssignmentStatus.ACCEPTED
        assignment.responded_at = timezone.now()
        assignment.save(update_fields=["status", "responded_at"])

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=provider_id,
            actor_role="PROVIDER",
            action=ActivityAction.ACCEPTED,
            new_value={"status": AppointmentStatus.ACCEPTED},
            description="Provider accepted the appointment"
        )

    return appointment




def reject_appointment(appointment_id, provider_id):

    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        if appointment.provider_id != provider_id:
            raise ValueError("This appointment is not assigned to you.")

        if appointment.status != AppointmentStatus.ASSIGNED:
            raise ValueError("Appointment cannot be rejected.")

        assignment = AppointmentAssignment.objects.get(
            appointment=appointment,
            provider_id=provider_id,
            is_current=True
        )

        appointment.status = AppointmentStatus.REJECTED
        appointment.provider_id = None
        appointment.save(
            update_fields=["status", "provider_id", "updated_at"]
        )

        assignment.status = AssignmentStatus.REJECTED
        assignment.is_current = False
        assignment.responded_at = timezone.now()
        assignment.save(
            update_fields=["status", "is_current", "responded_at"]
        )

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=provider_id,
            actor_role="PROVIDER",
            action=ActivityAction.REJECTED,
            old_value={"status": AppointmentStatus.ASSIGNED},
            new_value={"status": AppointmentStatus.REJECTED},
            description="Provider rejected the appointment"
        )

    return appointment  



def start_appointment(appointment_id, provider_id):

    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        if appointment.provider_id != provider_id:
            raise ValueError("This appointment is not assigned to you.")

        if appointment.status != AppointmentStatus.ACCEPTED:
            raise ValueError("Only accepted appointments can be started.")

        assignment = AppointmentAssignment.objects.get(
            appointment=appointment,
            provider_id=provider_id,
            is_current=True
        )

        appointment.status = AppointmentStatus.IN_PROGRESS
        appointment.save(update_fields=["status", "updated_at"])

        assignment.status = AssignmentStatus.IN_PROGRESS
        assignment.save(update_fields=["status"])

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=provider_id,
            actor_role="PROVIDER",
            action=ActivityAction.STARTED,
            old_value={"status": AppointmentStatus.ACCEPTED},
            new_value={"status": AppointmentStatus.IN_PROGRESS},
            description="Appointment started"
        )

    return appointment



def complete_appointment(appointment_id, provider_id):

    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        if appointment.provider_id != provider_id:
            raise ValueError("This appointment is not assigned to you.")

        if appointment.status != AppointmentStatus.IN_PROGRESS:
            raise ValueError("Only in-progress appointments can be completed.")

        assignment = AppointmentAssignment.objects.get(
            appointment=appointment,
            provider_id=provider_id,
            is_current=True
        )

        appointment.status = AppointmentStatus.COMPLETED
        appointment.save(update_fields=["status", "updated_at"])

        assignment.status = AssignmentStatus.COMPLETED
        assignment.save(update_fields=["status"])

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=provider_id,
            actor_role="PROVIDER",
            action=ActivityAction.COMPLETED,
            old_value={"status": AppointmentStatus.IN_PROGRESS},
            new_value={"status": AppointmentStatus.COMPLETED},
            description="Appointment completed"
        )

    return appointment




def reschedule_appointment(appointment_id, new_scheduled_at, actor_id=None):

    if new_scheduled_at <= timezone.now():
        raise ValueError("New appointment date must be in the future.")

    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        if appointment.status in [
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.IN_PROGRESS
        ]:
            raise ValueError("Appointment cannot be rescheduled.")

        old_date = appointment.scheduled_at

        appointment.scheduled_at = new_scheduled_at
        appointment.save(update_fields=["scheduled_at", "updated_at"])

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=actor_id,
            actor_role="CUSTOMER",
            action=ActivityAction.RESCHEDULED,
            old_value={"scheduled_at": old_date.isoformat()},
            new_value={"scheduled_at": new_scheduled_at.isoformat()},
            description="Appointment rescheduled"
        )

    return appointment



def cancel_appointment(appointment_id, actor_id=None):

    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        if appointment.status in [
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.IN_PROGRESS
        ]:
            raise ValueError("Appointment cannot be cancelled.")

        old_status = appointment.status

        appointment.status = AppointmentStatus.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])

        # Update current assignment if one exists
        AppointmentAssignment.objects.filter(
            appointment=appointment,
            is_current=True
        ).update(
            status=AssignmentStatus.CANCELLED,
            is_current=False
        )

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=actor_id,
            actor_role="CUSTOMER",
            action=ActivityAction.CANCELLED,
            old_value={"status": old_status},
            new_value={"status": AppointmentStatus.CANCELLED},
            description="Appointment cancelled"
        )

    return appointment


def update_appointment_status(
    appointment_id,
    new_status,
    actor_id=None,
    actor_role="ADMIN"
):

    with transaction.atomic():

        try:
            appointment = Appointment.objects.select_for_update().get(id=appointment_id)

        except Appointment.DoesNotExist:
            return None

        allowed_transitions = {
            AppointmentStatus.PENDING: [
                AppointmentStatus.CANCELLED
            ],
            AppointmentStatus.ASSIGNED: [
                AppointmentStatus.ACCEPTED,
                AppointmentStatus.REJECTED,
                AppointmentStatus.CANCELLED
            ],
            AppointmentStatus.REJECTED: [
                AppointmentStatus.ASSIGNED,
                AppointmentStatus.CANCELLED
            ],
            AppointmentStatus.ACCEPTED: [
                AppointmentStatus.IN_PROGRESS,
                AppointmentStatus.CANCELLED
            ],
            AppointmentStatus.IN_PROGRESS: [
                AppointmentStatus.COMPLETED
            ],
        }

        if new_status not in allowed_transitions.get(
            appointment.status, []
        ):
            raise ValueError(
                f"Cannot change status from "
                f"{appointment.status} to {new_status}"
            )

        old_status = appointment.status

        appointment.status = new_status
        appointment.save(update_fields=["status", "updated_at"])

        AppointmentActivity.objects.create(
            appointment=appointment,
            actor_id=actor_id,
            actor_role=actor_role,
            action=ActivityAction.STATUS_UPDATED,
            old_value={"status": old_status},
            new_value={"status": new_status},
            description=f"Status changed from {old_status} to {new_status}"
        )

    return appointment
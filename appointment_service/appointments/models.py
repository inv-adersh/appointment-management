from django.db import models


class AppointmentStatus(models.TextChoices):

    PENDING = "PENDING", "Pending"
    ASSIGNED = "ASSIGNED", "Assigned"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"    

class Appointment(models.Model):

    customer_id = models.IntegerField(db_index=True)
    provider_id = models.IntegerField(null=True,blank=True,db_index=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)

    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment {self.id} - {self.status}"


    
class AssignmentStatus(models.TextChoices):

    ASSIGNED = "ASSIGNED", "Assigned"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    REPLACED = "REPLACED", "Replaced"



class AppointmentAssignment(models.Model):

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    provider_id = models.IntegerField(db_index=True)
    assigned_by = models.IntegerField(null=True,blank=True)

    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ASSIGNED
    )

    is_current = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"Appointment {self.appointment_id} - Provider {self.provider_id}"

    
class ActivityAction(models.TextChoices):

    CREATED = "CREATED", "Created"
    UPDATED = "UPDATED", "Updated"
    ASSIGNED = "ASSIGNED", "Assigned"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    STARTED = "STARTED", "Started"
    STATUS_UPDATED = "STATUS_UPDATED", "Status Updated"
    RESCHEDULED = "RESCHEDULED", "Rescheduled"
    CANCELLED = "CANCELLED", "Cancelled"
    COMPLETED = "COMPLETED", "Completed"


class AppointmentActivity(models.Model):

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    actor_id = models.IntegerField(null=True,blank=True)
    actor_role = models.CharField(max_length=30,blank=True)
    action = models.CharField(max_length=30,choices=ActivityAction.choices)
    old_value = models.JSONField(null=True,blank=True)
    new_value = models.JSONField(null=True,blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.appointment_id} - {self.action}"
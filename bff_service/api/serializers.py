from rest_framework import serializers


class CreateAppointmentSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False,allow_blank=True)
    scheduled_at = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(min_value=1)


class AppointmentFilterSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(min_value=1,required=False)
    status = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


class UpdateAppointmentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200,required=False)
    description = serializers.CharField(required=False,allow_blank=True)
    duration_minutes = serializers.IntegerField(min_value=1,required=False)
    actor_id = serializers.IntegerField(required=False)

class AssignProviderSerializer(serializers.Serializer):
    provider_id = serializers.IntegerField(min_value=1)
    assigned_by = serializers.IntegerField(required=False)

class ProviderActionSerializer(serializers.Serializer):
    provider_id = serializers.IntegerField(min_value=1)

class RescheduleAppointmentSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()
    actor_id = serializers.IntegerField(required=False)

class UpdateAppointmentStatusSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(
        choices=[
            "PENDING",
            "ASSIGNED",
            "ACCEPTED",
            "REJECTED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED",
        ]
    )
    actor_id = serializers.IntegerField(required=False)

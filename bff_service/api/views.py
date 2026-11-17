import grpc

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from proto import appointment_pb2

from grpc_client import (
    create_appointment,
    get_appointment,
    list_appointments,
    update_appointment,
    assign_provider,
    accept_appointment,
    reject_appointment,
    start_appointment,
    complete_appointment,
    cancel_appointment,
    reschedule_appointment,
    update_appointment_status,
)

from .serializers import (
    CreateAppointmentSerializer,
    AppointmentFilterSerializer,
    UpdateAppointmentSerializer,
    AssignProviderSerializer,
    ProviderActionSerializer,
    RescheduleAppointmentSerializer,
    UpdateAppointmentStatusSerializer,

)


def appointment_to_dict(appointment):
    return {
        "id": appointment.id,
        "customer_id": appointment.customer_id,
        "provider_id": appointment.provider_id or None,
        "title": appointment.title,
        "description": appointment.description,
        "scheduled_at": appointment.scheduled_at,
        "duration_minutes": appointment.duration_minutes,
        "status": appointment.status,
    }


def grpc_error_response(error):
    if error.code() == grpc.StatusCode.NOT_FOUND:
        return Response(
            {"error": error.details()},
            status=status.HTTP_404_NOT_FOUND
        )

    if error.code() == grpc.StatusCode.INVALID_ARGUMENT:
        return Response(
            {"error": error.details()},
            status=status.HTTP_400_BAD_REQUEST
        )

    if error.code() == grpc.StatusCode.FAILED_PRECONDITION:
        return Response(
            {"error": error.details()},
            status=status.HTTP_409_CONFLICT
        )

    if error.code() == grpc.StatusCode.UNAVAILABLE:
        return Response(
            {"error": "Appointment Service is unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return Response(
        {"error": error.details()},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )



class CreateAppointmentView(APIView):

    def post(self, request):

        serializer = CreateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        grpc_request = appointment_pb2.CreateAppointmentRequest(
            customer_id=data["customer_id"],
            title=data["title"],
            description=data.get("description", ""),
            scheduled_at=data["scheduled_at"].isoformat(),
            duration_minutes=data["duration_minutes"],
        )

        try:
            response = create_appointment(grpc_request)
            return Response(
                appointment_to_dict(response),
                status=status.HTTP_201_CREATED
            )

        except grpc.RpcError as error:
            return grpc_error_response(error)

class GetAppointmentView(APIView):

    def get(self, request, appointment_id):

        grpc_request = appointment_pb2.GetAppointmentRequest(appointment_id=appointment_id)

        try:
            response = get_appointment(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)

class ListAppointmentsView(APIView):

    def get(self, request):

        serializer = AppointmentFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        grpc_request = appointment_pb2.ListAppointmentsRequest(
            customer_id=data.get("customer_id") or 0,
            status=data.get("status", ""),
            start_date=(
                data["start_date"].isoformat()
                if data.get("start_date") else ""
            ),
            end_date=(
                data["end_date"].isoformat()
                if data.get("end_date") else ""
            ),
        )

        try:
            response = list_appointments(grpc_request)
            appointments = [appointment_to_dict(appointment) for appointment in response.appointments]

            return Response(appointments)

        except grpc.RpcError as error:
            return grpc_error_response(error)

class UpdateAppointmentView(APIView):

    def patch(self, request, appointment_id):

        serializer = UpdateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not data:
            return Response(
                {"error": "Provide at least one field to update"},
                status=status.HTTP_400_BAD_REQUEST
            )

        grpc_request = appointment_pb2.UpdateAppointmentDetailsRequest(
            appointment_id=appointment_id,
            title=data.get("title", ""),
            description=data.get("description", ""),
            duration_minutes=data.get("duration_minutes", 0),
            actor_id=request.data.get("actor_id", 0),
        )

        try:
            response = update_appointment(grpc_request)

            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)


class AssignProviderView(APIView):

    def post(self, request, appointment_id):

        serializer = AssignProviderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        grpc_request = appointment_pb2.AssignProviderRequest(
            appointment_id=appointment_id,
            provider_id=data["provider_id"],
            assigned_by=data.get("assigned_by", 0),
        )

        try:
            response = assign_provider(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)

class AcceptAppointmentView(APIView):

    def post(self, request, appointment_id):

        serializer = ProviderActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        grpc_request = appointment_pb2.UpdateAppointmentRequest(
            appointment_id=appointment_id,
            provider_id=serializer.validated_data["provider_id"],
        )

        try:
            response = accept_appointment(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)

class RejectAppointmentView(APIView):

    def post(self, request, appointment_id):

        serializer = ProviderActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        grpc_request = appointment_pb2.UpdateAppointmentRequest(
            appointment_id=appointment_id,
            provider_id=serializer.validated_data["provider_id"],
        )

        try:
            response = reject_appointment(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)

class StartAppointmentView(APIView):

    def post(self, request, appointment_id):

        serializer = ProviderActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        grpc_request = appointment_pb2.UpdateAppointmentRequest(
            appointment_id=appointment_id,
            provider_id=serializer.validated_data["provider_id"],
        )

        try:
            response = start_appointment(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)

class CompleteAppointmentView(APIView):

    def post(self, request, appointment_id):

        serializer = ProviderActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        grpc_request = appointment_pb2.UpdateAppointmentRequest(
            appointment_id=appointment_id,
            provider_id=serializer.validated_data["provider_id"],
        )

        try:
            response = complete_appointment(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)

class CancelAppointmentView(APIView):

    def post(self, request, appointment_id):

        grpc_request = appointment_pb2.UpdateAppointmentRequest(
            appointment_id=appointment_id,
            actor_id=request.data.get("actor_id", 0),
        )

        try:
            response = cancel_appointment(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)

class RescheduleAppointmentView(APIView):

    def post(self, request, appointment_id):

        serializer = RescheduleAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        grpc_request = appointment_pb2.RescheduleAppointmentRequest(
            appointment_id=appointment_id,
            scheduled_at=data["scheduled_at"].isoformat(),
            actor_id=data.get("actor_id", 0),
        )

        try:
            response = reschedule_appointment(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)   


class UpdateAppointmentStatusView(APIView):

    def patch(self, request, appointment_id):

        serializer = UpdateAppointmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        grpc_request = appointment_pb2.UpdateAppointmentStatusRequest(
            appointment_id=appointment_id,
            new_status=data["new_status"],
            actor_id=data.get("actor_id", 0),
            actor_role="ADMIN",
        )

        try:
            response = update_appointment_status(grpc_request)
            return Response(appointment_to_dict(response))

        except grpc.RpcError as error:
            return grpc_error_response(error)
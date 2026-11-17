import grpc
from datetime import datetime, date

from django.utils import timezone

from proto import appointment_pb2
from proto import appointment_pb2_grpc

from appointments import services


class AppointmentServiceHandler(appointment_pb2_grpc.AppointmentServiceServicer):

    def convert_appointment(self, appointment):
        return appointment_pb2.AppointmentResponse(
            id=appointment.id,
            customer_id=appointment.customer_id,
            provider_id=appointment.provider_id or 0,
            title=appointment.title,
            description=appointment.description,
            scheduled_at=appointment.scheduled_at.isoformat(),
            duration_minutes=appointment.duration_minutes,
            status=appointment.status,
        )

    def CreateAppointment(self, request, context):
        try:
            scheduled_at = datetime.fromisoformat(request.scheduled_at)

            if timezone.is_naive(scheduled_at):
                scheduled_at = timezone.make_aware(scheduled_at)

            appointment = services.create_appointment(
                customer_id=request.customer_id,
                title=request.title,
                description=request.description,
                scheduled_at=scheduled_at,
                duration_minutes=request.duration_minutes,
            )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                str(error),
            )

    def GetAppointment(self, request, context):
        appointment = services.get_appointment(request.appointment_id)

        if appointment is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Appointment not found",
            )

        return self.convert_appointment(appointment)

    def ListAppointments(self, request, context):
        try:
            start_date = (date.fromisoformat(request.start_date) if request.start_date else None)
            end_date = (date.fromisoformat(request.end_date) if request.end_date else None)

            appointments = services.list_appointments(
                customer_id=request.customer_id or None,
                status=request.status or None,
                start_date=start_date,
                end_date=end_date,
            )

            response = appointment_pb2.ListAppointmentsResponse()

            for appointment in appointments:
                response.appointments.add(
                    id=appointment.id,
                    customer_id=appointment.customer_id,
                    provider_id=appointment.provider_id or 0,
                    title=appointment.title,
                    description=appointment.description,
                    scheduled_at=appointment.scheduled_at.isoformat(),
                    duration_minutes=appointment.duration_minutes,
                    status=appointment.status,
                )

            return response

        except ValueError as error:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                str(error),
            )

    def UpdateAppointment(self, request, context):
        data = {}

        if request.title:
            data["title"] = request.title

        if request.description:
            data["description"] = request.description

        if request.duration_minutes > 0:
            data["duration_minutes"] = request.duration_minutes

        try:
            appointment = services.update_appointment(
                appointment_id=request.appointment_id,
                data=data,
                actor_id=request.actor_id,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

    def AssignProvider(self, request, context):
        try:
            appointment = services.assign_provider(
                appointment_id=request.appointment_id,
                provider_id=request.provider_id,
                assigned_by=request.assigned_by,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

        except ConnectionError as error:
            context.abort(
                grpc.StatusCode.UNAVAILABLE,
                str(error),
            )

        except RuntimeError as error:
            context.abort(
                grpc.StatusCode.INTERNAL,
                str(error),
            )

    def AcceptAppointment(self, request, context):
        try:
            appointment = services.accept_appointment(
                appointment_id=request.appointment_id,
                provider_id=request.provider_id,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

    def RejectAppointment(self, request, context):
        try:
            appointment = services.reject_appointment(
                appointment_id=request.appointment_id,
                provider_id=request.provider_id,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

    def StartAppointment(self, request, context):
        try:
            appointment = services.start_appointment(
                appointment_id=request.appointment_id,
                provider_id=request.provider_id,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

    def CompleteAppointment(self, request, context):
        try:
            appointment = services.complete_appointment(
                appointment_id=request.appointment_id,
                provider_id=request.provider_id,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

    def CancelAppointment(self, request, context):
        try:
            appointment = services.cancel_appointment(
                appointment_id=request.appointment_id,
                actor_id=request.actor_id,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

    def RescheduleAppointment(self, request, context):
        try:
            scheduled_at = datetime.fromisoformat(request.scheduled_at)

            if timezone.is_naive(scheduled_at):
                scheduled_at = timezone.make_aware(scheduled_at)

            appointment = services.reschedule_appointment(
                appointment_id=request.appointment_id,
                new_scheduled_at=scheduled_at,
                actor_id=request.actor_id,
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                str(error),
            )

    def UpdateAppointmentStatus(self, request, context):
        try:
            appointment = services.update_appointment_status(
                appointment_id=request.appointment_id,
                new_status=request.new_status,
                actor_id=request.actor_id,
                actor_role=request.actor_role or "ADMIN",
            )

            if appointment is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Appointment not found",
                )

            return self.convert_appointment(appointment)

        except ValueError as error:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                str(error),
            )

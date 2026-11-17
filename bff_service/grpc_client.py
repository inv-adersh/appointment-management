import grpc

from proto import appointment_pb2_grpc


APPOINTMENT_SERVICE_ADDRESS = "127.0.0.1:50052"

channel = grpc.insecure_channel(APPOINTMENT_SERVICE_ADDRESS)

stub = appointment_pb2_grpc.AppointmentServiceStub(channel)


def create_appointment(request):
    return stub.CreateAppointment(request, timeout=5)


def get_appointment(request):
    return stub.GetAppointment(request, timeout=5)


def list_appointments(request):
    return stub.ListAppointments(request, timeout=5)


def update_appointment(request):
    return stub.UpdateAppointment(request, timeout=5)


def assign_provider(request):
    return stub.AssignProvider(request, timeout=5)


def accept_appointment(request):
    return stub.AcceptAppointment(request, timeout=5)


def reject_appointment(request):
    return stub.RejectAppointment(request, timeout=5)


def start_appointment(request):
    return stub.StartAppointment(request, timeout=5)


def complete_appointment(request):
    return stub.CompleteAppointment(request, timeout=5)


def cancel_appointment(request):
    return stub.CancelAppointment(request, timeout=5)


def reschedule_appointment(request):
    return stub.RescheduleAppointment(request, timeout=5)


def update_appointment_status(request):
    return stub.UpdateAppointmentStatus(request, timeout=5)
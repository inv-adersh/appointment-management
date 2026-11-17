from django.urls import path

from .views import (
    CreateAppointmentView,
    GetAppointmentView,
    ListAppointmentsView,
    UpdateAppointmentView,
    AssignProviderView,
    AcceptAppointmentView,
    RejectAppointmentView,
    StartAppointmentView,
    CompleteAppointmentView,
    CancelAppointmentView,
    RescheduleAppointmentView,
    UpdateAppointmentStatusView,
)


urlpatterns = [

    # Create appointment
    path(
        "appointments/",
        CreateAppointmentView.as_view(),
        name="create-appointment"
    ),

    # List and filter appointments
    path(
        "appointments/list/",
        ListAppointmentsView.as_view(),
        name="list-appointments"
    ),

    # Get appointment details
    path(
        "appointments/<int:appointment_id>/",
        GetAppointmentView.as_view(),
        name="get-appointment"
    ),

    # Update appointment details
    path(
        "appointments/<int:appointment_id>/update/",
        UpdateAppointmentView.as_view(),
        name="update-appointment"
    ),

    # Assign provider
    path(
        "appointments/<int:appointment_id>/assign/",
        AssignProviderView.as_view(),
        name="assign-provider"
    ),

    # Accept appointment
    path(
        "appointments/<int:appointment_id>/accept/",
        AcceptAppointmentView.as_view(),
        name="accept-appointment"
    ),

    # Reject appointment
    path(
        "appointments/<int:appointment_id>/reject/",
        RejectAppointmentView.as_view(),
        name="reject-appointment"
    ),

    # Start appointment
    path(
        "appointments/<int:appointment_id>/start/",
        StartAppointmentView.as_view(),
        name="start-appointment"
    ),

    # Complete appointment
    path(
        "appointments/<int:appointment_id>/complete/",
        CompleteAppointmentView.as_view(),
        name="complete-appointment"
    ),

    # Cancel appointment
    path(
        "appointments/<int:appointment_id>/cancel/",
        CancelAppointmentView.as_view(),
        name="cancel-appointment"
    ),

    # Reschedule appointment
    path(
        "appointments/<int:appointment_id>/reschedule/",
        RescheduleAppointmentView.as_view(),
        name="reschedule-appointment"
    ),

    # Update appointment status
    path(
        "appointments/<int:appointment_id>/status/",
        UpdateAppointmentStatusView.as_view(),
        name="update-appointment-status"
    ),

]
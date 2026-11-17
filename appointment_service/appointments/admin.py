from django.contrib import admin

from .models import (
    Appointment,
    AppointmentAssignment,
    AppointmentActivity,
)


admin.site.register(Appointment)
admin.site.register(AppointmentAssignment)
admin.site.register(AppointmentActivity)
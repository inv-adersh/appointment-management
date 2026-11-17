from django.contrib import admin
from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user_id',
        'name',
        'specialization',
        'is_active',
        'is_available',
    )

    list_filter = ('is_active', 'is_available')

    search_fields = ('name', 'specialization')
from .models import Provider


def get_provider(provider_id):
    try:
        return Provider.objects.get(id=provider_id)
        
    except Provider.DoesNotExist:
        return None


def list_providers():
    return Provider.objects.filter(is_active=True)


def check_provider_availability(provider_id):
    provider = get_provider(provider_id)

    if provider is None:
        return None

    return provider.is_active and provider.is_available
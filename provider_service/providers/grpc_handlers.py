import grpc

from proto import provider_pb2
from proto import provider_pb2_grpc

from .services import (
    get_provider,
    list_providers,
    check_provider_availability,
)


class ProviderServiceHandler(provider_pb2_grpc.ProviderServiceServicer):

    def GetProvider(self, request, context):

        provider = get_provider(request.provider_id)

        if provider is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Provider not found"
            )

        return provider_pb2.ProviderResponse(
            id=provider.id,
            name=provider.name,
            specialization=provider.specialization,
            is_active=provider.is_active,
            is_available=provider.is_available,
        )

    def ListProviders(self, request, context):

        providers = list_providers()

        response = provider_pb2.ListProvidersResponse()

        for provider in providers:
            response.providers.add(
                id=provider.id,
                name=provider.name,
                specialization=provider.specialization,
                is_active=provider.is_active,
                is_available=provider.is_available,
            )

        return response

    def CheckProviderAvailability(self, request, context):

        is_available = check_provider_availability(
            request.provider_id
        )

        if is_available is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Provider not found"
            )

        return provider_pb2.AvailabilityResponse(
            is_available=is_available
        )
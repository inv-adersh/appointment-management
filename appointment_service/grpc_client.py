import grpc

from proto import provider_pb2
from proto import provider_pb2_grpc


PROVIDER_SERVICE_ADDRESS = "127.0.0.1:50051"

channel = grpc.insecure_channel(PROVIDER_SERVICE_ADDRESS)
stub = provider_pb2_grpc.ProviderServiceStub(channel)


def get_provider_details(provider_id):
    try:
        request = provider_pb2.ProviderRequest(provider_id=provider_id)

        response = stub.GetProvider(
            request,
            timeout=5
        )

        return response

    except grpc.RpcError as error:

        if error.code() == grpc.StatusCode.NOT_FOUND:
            raise ValueError("Provider does not exist.")

        elif error.code() == grpc.StatusCode.UNAVAILABLE:
            raise ConnectionError("Provider Service is unavailable.")

        elif error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            raise TimeoutError("Provider Service request timed out.")

        raise RuntimeError(f"Provider Service error: {error.details()}")
from concurrent import futures

import grpc

from django.core.management.base import BaseCommand

from proto import provider_pb2_grpc
from providers.grpc_handlers import ProviderServiceHandler


class Command(BaseCommand):

    help = "Run Provider gRPC Server"

    def handle(self, *args, **options):

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        provider_pb2_grpc.add_ProviderServiceServicer_to_server(
            ProviderServiceHandler(),
            server
        )

        port = server.add_insecure_port("127.0.0.1:50051")

        if port == 0:
            raise RuntimeError("Failed to bind gRPC server")

        server.start()

        self.stdout.write(
            self.style.SUCCESS(
                "Provider gRPC server running on port 50051"
            )
        )

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            server.stop(grace=5)
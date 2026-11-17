from concurrent import futures

import grpc

from django.core.management.base import BaseCommand

from proto import appointment_pb2_grpc
from appointments.grpc_handlers import AppointmentServiceHandler


class Command(BaseCommand):

    # help = "Run Appointment gRPC Server"

    def handle(self, *args, **options):

        # Create gRPC server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Register our handler
        appointment_pb2_grpc.add_AppointmentServiceServicer_to_server(
            AppointmentServiceHandler(),
            server
        )

        # Configure port
        port = server.add_insecure_port("127.0.0.1:50052")

        if port == 0:
            raise RuntimeError(
                "Failed to start Appointment gRPC server"
            )

        # Start server
        server.start()

        self.stdout.write(
            self.style.SUCCESS(
                f"Appointment gRPC server running on port {port}"
            )
        )

        # Keep server running
        try:
            server.wait_for_termination()

        except KeyboardInterrupt:
            server.stop(grace=5)
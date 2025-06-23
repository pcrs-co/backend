from rest_framework.response import Response
from rest_framework import status
import base64
from .tasks import process_benchmark_file


class AsynchronousBenchmarkUploadMixin:
    """
    A Mixin to handle file uploads and delegate processing to Celery.
    """

    def _handle_upload(self, request, item_type):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "File is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            file_content_base64 = base64.b64encode(file.read()).decode("utf-8")
            process_benchmark_file.delay(file_content_base64, file.name, item_type)
            return Response(
                {"message": "File received. Processing has started in the background."},
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from django.urls import path
from .views import UploadCSVView, DownloadCSVView, StatusAPIView, WebhookReceiverView

urlpatterns = [
    # Endpoint for uploading CSV files containing image processing requests.
    path('api/upload/', UploadCSVView.as_view(), name='upload_csv'),

    # Endpoint for downloading the output CSV file that contains details of processed images.
    path('api/download/', DownloadCSVView.as_view(), name='download_output_csv'),

    # Endpoint for checking the status of image processing requests.
    path('api/status/', StatusAPIView.as_view(), name='status_api'),

    # Endpoint for receiving webhooks to trigger actions upon request completion.
    path('api/webhook/', WebhookReceiverView.as_view(), name='webhook_receiver'),
]

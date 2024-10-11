import requests
import json
import csv
import os
import uuid
from urllib.parse import urlparse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from .models import ImageProcessingRequest
from .tasks import process_csv

def validate_csv(file):
    """
    Validate the CSV file format.
    - Check if the header is correct.
    - Ensure all rows have the correct number of columns.
    - Validate that S. No. is a number.
    - Ensure Product Name is not empty.
    - Check if Input Image URLs are valid URLs.
    """
    try:
        csv_reader = csv.reader(file.read().decode('utf-8').splitlines())
        header = next(csv_reader, None)  # Read header
        
        # Check if the header matches the expected format
        expected_header = ['S. No.', 'Product Name', 'Input Image Urls']
        if header != expected_header:
            return f"Invalid CSV header format. Expected: {expected_header}, Found: {header}"

        for row_number, row in enumerate(csv_reader, start=2):  # Start at row 2 for CSV rows
            if len(row) != 3:
                return f"Row {row_number} must have exactly 3 columns."

            s_no, product_name, image_urls = row

            # Check if 'S. No.' is a number
            if not s_no.isdigit():
                return f"Invalid 'S. No.' in row {row_number}: {s_no}"

            # Check if product name is empty
            if not product_name.strip():
                return f"Product Name cannot be empty in row {row_number}."

            # Validate URLs
            urls = image_urls.split(',')
            for url in urls:
                parsed_url = urlparse(url.strip())
                if not all([parsed_url.scheme, parsed_url.netloc]):
                    return f"Invalid URL in row {row_number}: {url.strip()}"

        return None  
    except Exception as e:
        return f"An error occurred during validation: {str(e)}"



class UploadCSVView(APIView):
    """
    UploadCSVView handles the uploading of CSV files for image processing requests.
    It validates the uploaded file and initiates processing if the file is valid.

    """
    def post(self, request):
        """
        Handle POST requests to upload a CSV file.

        """
        
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']

            # Ensure it's a CSV file
            if not uploaded_file.name.endswith('.csv'):
                return Response({"error": "Only CSV files are allowed."}, status=http_status.HTTP_400_BAD_REQUEST)

            # Validate CSV content
            validation_error = validate_csv(uploaded_file)
            if validation_error:
                return Response({"error": validation_error}, status=http_status.HTTP_400_BAD_REQUEST)
        
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            
            # Generate request ID and create processing request
            request_id = str(uuid.uuid4())
            ImageProcessingRequest.objects.create(
                request_id=request_id,
                file=filename,
                status='Pending'
            )
            # Trigger the CSV processing task asynchronously
            process_csv.delay(request_id)

            return Response({"request_id": request_id, "message": "CSV uploaded and processing started."}, status=http_status.HTTP_202_ACCEPTED)

        return Response({"error": "No file uploaded."}, status=http_status.HTTP_400_BAD_REQUEST)




class DownloadCSVView(APIView):
    """
    DownloadCSVView handles requests for downloading CSV files containing 
    details of compressed image processing requests.

    """
    def get(self, request):
        """
        Handle GET requests to download a CSV file for a specific image processing request.

        """
        try:
            request_id = request.GET.get('request_id')
            processing_request = ImageProcessingRequest.objects.get(request_id=request_id)
            products = processing_request.products.all()  # Get products related to this request

            # Prepare the response as CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="processed_images_{request_id}.csv"'

            writer = csv.writer(response)
            writer.writerow(['S. No.', 'Product Name', 'Input Image Urls', 'Output Image Urls'])

            # Write each product's details into the CSV
            for product in products:
                writer.writerow([
                    product.s_no,
                    product.name,
                    product.input_image_urls,
                    product.output_image_urls
                ])

            return response
        except ImageProcessingRequest.DoesNotExist:
            return Response({"error": "Invalid request ID"}, status=http_status.HTTP_404_NOT_FOUND)



class StatusAPIView(APIView):
    """
    StatusAPIView handles status check requests for image processing tasks.
    It retrieves the status of a specific processing request based on request_id.

    """
    def get(self, request):
        try:
            request_id = request.GET.get('request_id')
            processing_request = ImageProcessingRequest.objects.get(request_id=request_id)
            return Response({
                "request_id": request_id,
                "status": processing_request.status,
            }, status=http_status.HTTP_200_OK)
        except ImageProcessingRequest.DoesNotExist:
            return Response({"error": "Invalid request ID"}, status=http_status.HTTP_404_NOT_FOUND)






class WebhookReceiverView(APIView):
    """
    WebhookReceiverView handles incoming webhook requests.

    """
    def post(self, request):
        try:
            payload = request.data
            request_id = payload.get("request_id")
            status = payload.get("status")

            # Optionally update the database
            ImageProcessingRequest.objects.filter(request_id=request_id).update(status=status)

            print(f"Webhook received for request ID: {request_id} with status: {status}")
            return Response({"message": "Webhook received successfully"}, status=http_status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)








def trigger_webhook(request_id):
    """
    Triggers a webhook to notify the completion status of an image processing request.
    
    """
    try:
        #Get the BASE_URL environment variable
        base_url = os.getenv('BASE_URL')
        
        if not base_url:
            raise ValueError("BASE_URL environment variable is not set. Fallback to localhost will be used.")
        
        webhook_url = f"{base_url}/api/webhook/"
        data = {"request_id": request_id, "status": "Completed"}

        # Send POST request to the webhook URL
        response = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        
        # Check the response status code
        if response.status_code == 200:
            print(f"Webhook for request {request_id} sent successfully")
        else:
            print(f"Failed to send webhook for request {request_id}. Status Code: {response.status_code}")
            print(f"Response content: {response.text}")  # Optional: Print response content for debugging
            
    except ValueError as ve:
        print(f"ValueError: {str(ve)}")
    except Exception as e:
        print(f"An error occurred while sending the webhook for request {request_id}: {str(e)}")

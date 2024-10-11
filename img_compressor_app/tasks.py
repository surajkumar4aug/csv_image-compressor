from celery import shared_task
from .models import Product, ImageProcessingRequest
from PIL import Image
import requests
from io import BytesIO
from . import views
import csv
import cloudinary.uploader
import cloudinary
import os

@shared_task
def process_csv(request_id):
    """
    Processes the uploaded CSV file for image compression requests

    """
    
    request_obj = ImageProcessingRequest.objects.get(request_id=request_id)
    request_obj.status = 'Processing'
    request_obj.save()

    # Process the CSV file and compress the images
    file = request_obj.file
    with open(file.path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            s_no = int(row[0])  # Ensure S. No. is an integer
            product_name = row[1]
            input_urls = row[2].split(',')

            output_urls = []
            for url in input_urls:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url.strip(), headers=headers, stream=True)

                    if response.status_code == 200 and 'image' in response.headers['Content-Type']:
                        img = Image.open(BytesIO(response.content)).convert('RGB')
                        output_io = BytesIO()
                        img.save(output_io, format='JPEG', quality=50)  # Compress the image
                        output_io.seek(0)
                        image_name = os.path.basename(url.split("?")[0])  # Remove query parameters if any
                        print(image_name)
                        # Upload to Cloudinary with the same image name (without extension for public_id)
                        public_id = os.path.splitext(image_name)[0]
                        # Upload to Cloudinary
                        print(public_id)
                        upload_result = cloudinary.uploader.upload(output_io, resource_type='image',public_id=public_id,unique_filename=True)
                        output_url = upload_result['secure_url']
                        output_urls.append(output_url)
                    else:
                        print(f"Failed to retrieve image: {url} (Status Code: {response.status_code})")
                except Exception as e:
                    print(f"Error processing URL {url}: {str(e)}")

            # Save processed product information
            Product.objects.create(
                s_no=s_no,
                name=product_name,
                input_image_urls=','.join(input_urls),
                output_image_urls=','.join(output_urls),
                request=request_obj  # Link to the processing request
            )

    # Update the status to 'Completed'
    request_obj.status = 'Completed'
    request_obj.save()

    # Trigger the webhook once processing is complete
    views.trigger_webhook(request_id)

    # Delete the CSV file from media
    if os.path.exists(file.path):
        os.remove(file.path)  # Remove the CSV file after processing
        print(f"Deleted CSV file: {file.path}")
    else:
        print(f"CSV file not found: {file.path}")

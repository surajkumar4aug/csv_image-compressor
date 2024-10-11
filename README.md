# CSV Image Compressor

This project is a Django application designed to compress images based on data provided in a CSV file. It uses Celery for asynchronous task processing and supports image upload, compression, and download functionalities.

## Features

- Upload a CSV file containing image URLs.
- Asynchronously compress images to 50% quality using Celery.
- Download the processed images via a provided URL.
- Store the results in a database.

## Technologies Used

- Django
- Celery
- Redis (as the message broker)
- Pillow (for image processing)
- Cloudinary (for store image)

## Getting Started

### Prerequisites

- Python 3.8 or later
- Django
- Redis
- Celery
- Pillow
- Cloudinary

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd csv_image_compressor
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `.\env\Scripts\Activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the environment variables:**
   Create a `.env` file in the root of the project and add the following variables:
   ```env
   Cloudinary configuration
   CLOUD_NAME=
   API_KEY=
   API_SECRET=
   
   Celery configuration
   CELERY_BROKER_URL=
   CELERY_RESULT_BACKEND=
   SECRET_KEY=
   
   DEBUG=
   
   Webhook_URL
   BASE_URL=
   ```

5. **Run database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run the Celery worker:**
   Open a new terminal, activate the virtual environment, and run:
   ```bash
   'celery -A csv_images_compresser worker --loglevel=info'

   or
   
   `.celery -A csv_images_compressor worker --loglevel=info --pool=gevent` # On Windows use
   ```

7. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```

### Usage

1. **Upload a CSV file** containing the URLs of images to be compressed.
2. **Trigger the compression process.** Initiate image compression after CSV upload.
3. **Check Status of Processing:** Monitor processing status using the request ID.
4. **Download the processed images** using the provided download link.

### API Endpoints

- **Upload CSV:** `/api/upload/`
- **Download Processed Images:** `/api/download/?request_id=<request_id>`
- **Check Status of Processing:** `/api/status/?request_id=<request_id>`
- **Webhook Trigger Api:**  `/api/webhook/`

### License

This project is licensed under the MIT License.


from django.db import models

# class Product(models.Model):
#     s_no = models.IntegerField(max_length=5)
#     name = models.CharField(max_length=255)
#     input_image_urls = models.TextField()
#     output_image_urls = models.TextField(blank=True, null=True)

# class ImageProcessingRequest(models.Model):
#     request_id = models.CharField(max_length=255)
#     file = models.FileField(upload_to='uploads/')
#     status = models.CharField(max_length=20, default='Pending')
#     created_at = models.DateTimeField(auto_now_add=True)


class ImageProcessingRequest(models.Model):
    request_id = models.CharField(max_length=255, unique=True)
    file = models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    s_no = models.IntegerField()
    name = models.CharField(max_length=255)
    input_image_urls = models.TextField()
    output_image_urls = models.TextField(blank=True, null=True)
    request = models.ForeignKey('ImageProcessingRequest', on_delete=models.CASCADE, related_name='products')
    


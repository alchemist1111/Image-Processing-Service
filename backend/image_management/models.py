from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from PIL import Image as PilImage
from io import BytesIO
import requests

# Model to represent an image uploaded by a user
class Image(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original = CloudinaryField('image')
    image_url = models.URLField(blank=True, null=True)
    original_format = models.CharField(max_length=10, blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    size_bytes = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # On save, update image_url with the Cloudinary URL and extract image details
        if not self.image_url and self.original:
            self.image_url = self.original.url
        
        # Fetch the image from Cloudinary and calculate properties
        if self.original:
            response = requests.get(self.original.url)
            img = PilImage.open(BytesIO(response.content))
            
            # Extract image details
            self.original_format = img.format.lower() # Image format
            self.width, self.height = img.size    # Image width and height
            self.size_bytes = len(response.content) # Image size in bytes
        super().save(*args, **kwargs)    

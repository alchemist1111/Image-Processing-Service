from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from PIL import Image as PilImage
from io import BytesIO
import requests
import uuid

# Model to represent an image uploaded by a user
class Image(models.Model):
    image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    original = CloudinaryField('image')
    image_url = models.URLField(blank=True, null=True)
    original_format = models.CharField(max_length=10, blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    size_bytes = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # First save to ensure file is uploaded and .url is available
        super().save(*args, **kwargs)

        updated = False
        # Only update image_url if not set and file has .url
        if not self.image_url and self.original and hasattr(self.original, 'url'):
            self.image_url = self.original.url
            updated = True

        # Extract image details if not already set (to prevent overwriting on updates)
        if self.original and hasattr(self.original, 'url') and not (self.original_format and self.width and self.height and self.size_bytes):
            try:
                response = requests.get(self.original.url)
                response.raise_for_status()  # Raise an exception for any failed request
                img = PilImage.open(BytesIO(response.content))
                self.original_format = img.format.lower()  # Image format
                self.width, self.height = img.size        # Image width and height
                self.size_bytes = len(response.content)   # Image size in bytes
                updated = True
            except requests.exceptions.RequestException as e:
                raise ValidationError(f"Error fetching image: {e}")
            except Exception as e:
                raise ValidationError(f"Error processing image: {e}")

        # Save again if we updated any fields
        if updated:
            super().save(update_fields=[
                f for f in ['image_url', 'original_format', 'width', 'height', 'size_bytes']
                if getattr(self, f, None) is not None
            ])

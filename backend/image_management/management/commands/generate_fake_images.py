# images/management/commands/generate_fake_images.py

import io
import random
from django.core.management.base import BaseCommand
from PIL import Image as PilImage, ImageDraw, ImageFont
from faker import Faker
from image_management.models import Image  # Your Image model
import cloudinary.uploader

fake = Faker()

def generate_fake_image():
    """
    Generates a fake image with random colors, text, and some noise.
    """
    # Create a blank image
    width, height = 200, 200
    image = PilImage.new("RGB", (width, height), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    # Draw some text on the image
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()  # Use default font
    text = fake.name()  # Use Faker to generate a fake name

    # Use textbbox() to get the bounding box (width and height) of the text
    textbbox = draw.textbbox((0, 0), text, font=font)
    textwidth = textbbox[2] - textbbox[0]  # Calculate the width
    textheight = textbbox[3] - textbbox[1]  # Calculate the height

    position = (width // 2 - textwidth // 2, height // 2 - textheight // 2)
    draw.text(position, text, fill=(255, 255, 255), font=font)

    # Optionally add some random shapes
    for _ in range(random.randint(10, 30)):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=random.randint(1, 5))

    # Save the image to a BytesIO object
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr

class Command(BaseCommand):
    help = 'Generates fake images and uploads them to Cloudinary, saving the URL in the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting fake image generation...'))

        # Generate and upload 10 fake images as an example
        for _ in range(50):
            # Generate a fake image
            fake_image = generate_fake_image()

            # Upload the image to Cloudinary
            upload_result = cloudinary.uploader.upload(fake_image, folder="fake_images/")

            # Get the image URL from Cloudinary
            image_url = upload_result.get("url")

            # Save the image URL to the database
            self.save_image_url_to_database(image_url)

            self.stdout.write(self.style.SUCCESS(f'Fake image uploaded and URL saved: {image_url}'))

        self.stdout.write(self.style.SUCCESS('Fake image generation completed.'))

    def save_image_url_to_database(self, image_url):
        """
        Save the image URL into the database.
        """
        image = Image(
            owner=None,  # Or assign the appropriate user
            original=image_url  # Save Cloudinary image URL
        )
        image.save()

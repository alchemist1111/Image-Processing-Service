from rest_framework.exceptions import ValidationError

# Image type validations
def validate_image_type(value):
    # Check if the file type is valid (you can adjust this list as needed)
    valid_image_formats = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif']
    if value.content_type not in valid_image_formats:
        raise ValidationError("Unsupported file type. Only JPEG, PNG, and GIF are allowed.")
    return value


# Image size validations
def validate_image_size(value, max_size=5 * 1024 * 1024):
    # Check if image size exceeds the maximum allowed size (default is 5MB)
    if value.size > max_size:
        raise ValidationError(f"File size exceeds the maximum allowed size of {max_size / (1024 * 1024)}MB.")
    return value
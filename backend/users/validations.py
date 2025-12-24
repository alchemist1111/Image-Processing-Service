from django.core.exceptions import ValidationError
import re

def validate_email(value):
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, value):
        raise ValidationError("Please enter a valid email address.")
    return value

def validate_password(value):
    """Validate password strength."""
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in value):
        raise ValidationError("Password must contain at least one digit.")
    if not any(char.isupper() for char in value):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in value):
        raise ValidationError("Password must contain at least one lowercase letter.")
    return value

def validate_name(first_name, last_name):
    """Validate that the first and last name are not empty."""
    if not first_name or not last_name:
        raise ValidationError("First name and Last name are required.")
    return True
from rest_framework import serializers
from .models import Image
from users.serializers import UserSerializer
from .validations import validate_image_size, validate_image_type
from rest_framework.exceptions import ValidationError

# Image serializer
class ImageSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    image_url = serializers.URLField(read_only=True)
    
    class Meta:
        model = Image
        fields = ('image_id', 'owner', 'original', 'image_url', 'original_format', 'width', 'height', 'size_bytes', 'created_at')



# Image upload serializer
class ImageUploadSerializer(serializers.ModelSerializer):
    original = serializers.ImageField(
        label="Image",
        help_text="Select an image file to upload (JPEG, jpg, PNG, GIF, max 5MB)."
    )

    class Meta:
        model = Image
        fields = ['original']

    def validate(self, attrs):
        file = attrs.get('original')
        if not file:
            raise ValidationError("No file provided.")
        validate_image_size(file)
        validate_image_type(file)
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            image_instance = Image.objects.create(owner=user, **validated_data)
        else:
            image_instance = Image.objects.create(**validated_data)
        return image_instance
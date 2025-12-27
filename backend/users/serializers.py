from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError
import re
from .validations import validate_email, validate_password, validate_name

# User serializer for serializing and deserializing User model instances
class UserSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and updating user details, including password update."""
    # Password-related fields, required only for password update scenarios
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    confirm_new_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'created_at', 'updated_at', 'old_password', 'new_password', 'confirm_new_password']
        read_only_fields = ['user_id', 'created_at', 'updated_at']
        
    def validate_old_password(self, value):
        """Validate the old password when updating password"""
        user = self.context.get('user')  # Access the current authenticated user
        if value and not user.check_password(value):
            raise ValidationError("The old password is incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Validate the new password"""
        if value:
            return validate_password(value)
        return value
    
    def validate(self, attrs):
        """Cross-field validation to ensure new password and confirm new password match"""
        if attrs.get('new_password') != attrs.get('confirm_new_password'):
            raise ValidationError("The new passwords do not match.")
        return attrs
    
    def update(self, instance, validated_data):
        """Override the update method to handle password updates"""
        
        # If the password fields are provided, handle password update
        if 'new_password' in validated_data:
            # Ensure old password is provided and valid
            old_password = validated_data.get('old_password')
            if not old_password:
                raise ValidationError("Old password is required for password update.")
            
            # Validate old password
            if not instance.check_password(old_password):
                raise ValidationError("The old password is incorrect.")
            
            # Set the new password and remove password fields from validated data
            instance.set_password(validated_data['new_password'])
            validated_data.pop('old_password', None)
            validated_data.pop('new_password', None)
            validated_data.pop('confirm_new_password', None)

        # Update other fields (excluding the password fields)
        return super().update(instance, validated_data)    


# User registration serializer with password validation
class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password'] 
    
    def validate_email(self, value):
        """Custom email validation"""
        return validate_email(value)
    
    def validate_password(self, value):
        """Custom password validation"""
        return validate_password(value)    
    
    def validate(self, attrs):
        """Cross-field validation"""
        validate_name(attrs['first_name'], attrs['last_name'])
        return attrs
    
    def create(self, validated_data):
        """Override create method to handle password encryption"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user      
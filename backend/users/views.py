from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.request import Request
from .serializers import UserSerializer, UserRegistrationSerializer
from rest_framework.exceptions import ValidationError
from .tokens import generate_tokens, blacklist_token
from django.contrib.auth import authenticate
import logging
from typing import Any

# Configure user
User = get_user_model()

# Configure logger
logger = logging.getLogger(__name__)


# User Registration View
class UserRegistrationView(APIView):
    """API view for user registration."""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        """Handle the post request for user registration."""
        
        try:
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                user = serializer.save()
                
                # Return limited user details excluding password
                user_data = {
                    'user_id': str(user.user_id),
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
                
                # Response data
                message = {
                    'status': 'success',
                    'message': 'User registered successfully.',
                    'data': user_data
                }
                logger.info(f"Successfully registered user: {user.email}")
                return Response(message, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Registration failed due to validation errors: {serializer.errors}")
            message = {
                'status': 'error',
                'message': 'Registration failed.',
                'errors': serializer.errors
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            message = {
                'status': 'error',
                'message': 'An error occurred during registration.'
            }
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# User Login View
class UserLoginView(APIView):
    """
        Handles user login.
            - Authenticates the user with email and password.
            - Returns JWT tokens (access and refresh tokens) on successful login.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response: 
        """
            Handle POST request for user login.
            
            Args:
                request: HTTP request object containing login credentials
                
            Returns:
                Response object with authentication tokens and user data
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            message = {
                'status': 'error',
                'message': "Email and password are required."
            }
            logger.warning("Login failed: Missing email or password.")
            raise ValidationError(message)  
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            message = {
                'status': 'error',
                'message': 'Invalid email or password.'
            }
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        
        if user is None:
            message = {
                'status': 'error',
                'message': 'Invalid email or password.'
            }
            logger.warning(f"Login failed for email: {email}")
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens for the authenticated user
        token = generate_tokens(user)
        logger.info(f"Successful login for user: {email}")
        
        # Return response with tokens and user details
        response_data = {
            'status': 'success',
            'message': 'Login successful.',
            'data': {
                'refresh': token['refresh'],
                'access': token['access'],
                'user': {
                    'user_id': str(user.user_id),
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            }
        } 
        logger.debug(f"Login response data for user {email}: {response_data}")
        return Response(response_data, status=status.HTTP_200_OK)        
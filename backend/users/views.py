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
from .pagination import CustomPagination
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
    

# User Logout View
class UserLogoutView(APIView):
    pass


# User Retrieval, update, and deletion View
class UserDetailView(APIView):
    """API view for retrieving, updating, and deleting user details."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get(self, request):
        """Retrieve user details for the authenticated user."""
        try:
            user = request.user # Get the currently authenticated user
            
            serializer = self.serializer_class(user) # Serialize the user data
            logger.info(f"Retrieved details for user: {user.email}")
            
            response_data = {
                'status': 'success',
                'message': 'User details retrieved successfully.',
                'data': serializer.data
            }
            logger.debug(f"User details response data for {user.email}: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error retrieving user details: {str(e)}")
            response_data = {
                'status': 'error',
                'message': 'An error occurred while retrieving user details.'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, *args, **kwargs):
        """Update user details."""
        user = request.user  # Get the currently authenticated user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save() # Save the updated user data
            logger.info(f"Updated details for user: {user.email}")
            
            message = {
                'status': 'success',
                'message': 'User details updated successfully.',
                'data': serializer.data
            }
            logger.debug(f"User update response data for {user.email}: {message}")
            return Response(message, status=status.HTTP_200_OK)
        
        logger.warning(f"User update failed for {user.email} due to validation errors: {serializer.errors}")
        message = {
            'status': 'error',
            'message': 'Failed to update user details.',
            'errors': serializer.errors
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, *args, **kwargs):
        """Delete the user."""
        user = request.user # Get the currently authenticated user
        
        try:
            user.delete() # Delete the user
            logger.info(f"Deleted user: {user.email}")
            
            message= {
                'status': 'success',
                'message': 'User deleted successfully.'
            } 
            logger.debug(f"User deletion response data for {user.email}: {message}")
            return Response(message, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent user: {user.email}")
            
            message = {
                'status': 'error',
                'message': 'User does not exist.'
            }
            logger.debug(f"User deletion response data for non-existent user {user.email}: {message}")
            return Response(message, status=status.HTTP_404_NOT_FOUND)   


# User List View
class UserListView(APIView):
    """API view for listing all registered users."""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    
    def get(self, request):
        """Retrieve a paginated list of all users."""
        try:
            users = User.objects.all() # Get all users
            
            # An instance of the custom pagination class
            paginator = CustomPagination()
            
            # Paginate the queryset and get the serialized data for the current page
            page = paginator.paginate_queryset(users, request)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True) # Serialize the user data
                return paginator.get_paginated_response(serializer.data) # Return the custom paginated response
            
            # If the queryset is smaller than a page, serialize all users
            serializer = self.serializer_class(users, many=True)
            logger.info(f"Retrieved list of all users. Total users: {users.count()}")
            response_data = {
                'status': 'success',
                'message': 'User list retrieved successfully.',
                'data': serializer.data
            }
            logger.debug(f"User list response data: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error retrieving user list: {str(e)}")
            response_data = {
                'status': 'error',
                'message': 'An error occurred while retrieving user list.'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
                    
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.exceptions import InvalidToken
import logging

# Configure logger
logger = logging.getLogger(__name__)

def generate_tokens(user):
    """
    Generate JWT access and refresh tokens for a given user.
    
    Args:
        user: The user for whom the tokens are generated.
    
    Returns:
        dict: A dictionary containing the access and refresh tokens as strings.
    """
    refresh = RefreshToken.for_user(user)

    # Set custom expiration times if they are defined in settings
    refresh.set_exp(lifetime=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])
    refresh.access_token.set_exp(lifetime=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
    
    # Return the tokens as strings
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }

def blacklist_token(refresh_token):
    """
    Blacklist a given refresh token by adding it to the BlacklistedToken model.
    
    Args:
        refresh_token (str): The refresh token string to be blacklisted.
    
    Returns:
        bool: True if the token was successfully blacklisted, otherwise False.
    """
    try:
        # Attempt to validate and decode the refresh token
        refresh_token = RefreshToken(refresh_token)
        
        # Create a new BlacklistedToken entry with the decoded refresh token
        BlacklistedToken.objects.create(token=refresh_token)

        # Log successful blacklisting
        logger.info(f"Token {refresh_token} successfully blacklisted.")
        return True
    except InvalidToken:
        # Invalid refresh token provided
        logger.error(f"Invalid refresh token: {refresh_token}")
        return False
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Error blacklisting token: {str(e)}")
        return False
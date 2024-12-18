from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from graphql_jwt.utils import jwt_decode
from django.core.exceptions import PermissionDenied
from channels.middleware import BaseMiddleware
from ...models import CustomUser

class JWTAuthMiddleware(BaseMiddleware):
    """Custom middleware to authenticate WebSocket connections using JWT."""

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope, receive, send):
        # Get JWT token from WebSocket connection headers
        token = None
        for header in scope["headers"]:
            if header[0] == b"authorization":
                token = header[1].decode("utf-8").split("JWT ")[-1]
                break

        # If a token is provided, decode it using graphql-jwt
        if token:
            try:
                payload = jwt_decode(token)
                # Attach the user to the scope
                scope['user'] = self.get_user_from_payload(payload)
            except Exception as e:
                # Return a permission denied error if the token is invalid
                scope['user'] = None
        else:
            scope['user'] = None

        return super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_payload(self, payload):
        """Helper function to get the user from the payload."""
        
        try:
            user = CustomUser.objects.get(username=payload['username'])
        except CustomUser.DoesNotExist:
            return None
        return user

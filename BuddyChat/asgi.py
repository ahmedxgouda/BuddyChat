"""
ASGI config for BuddyChat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from BuddyChatAPI.GraphQL.subscriptions.consumers import MainConsumer
from django.urls import re_path
from BuddyChatAPI.GraphQL.subscriptions.middleware import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BuddyChat.settings')

asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter([
            re_path(r'graphql', MainConsumer.as_asgi()),
        ])    
    ),
})

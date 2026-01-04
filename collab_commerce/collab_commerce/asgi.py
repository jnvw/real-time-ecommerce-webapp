"""
ASGI config for collab_commerce project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application

# Set the environment variable first to ensure Django knows which settings to use.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collab_commerce.settings')

# Initialize Django's settings and get the default HTTP application.
# This MUST happen before importing anything that relies on Django models,
# such as our consumers or routing.
django_asgi_app = get_asgi_application()

# Now that Django is initialized, we can safely import our routing.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import shop.routing

application = ProtocolTypeRouter({
    # For standard HTTP requests, use the initialized Django application.
    "http": django_asgi_app,
    
    # For WebSocket requests, use our custom routing configuration.
    "websocket": AuthMiddlewareStack(
        URLRouter(
            shop.routing.websocket_urlpatterns
        )
    ),
})

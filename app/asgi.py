import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django_asgi_app = get_asgi_application()

from app.token_auth import TokenAuthMiddleware  
# Import your custom middleware after setting DJANGO_SETTINGS_MODULE
from notifications.consumer import NotificationConsumer


application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(  # Use your custom middleware
            URLRouter([
                path("ws/noti-<str:pk>/", NotificationConsumer.as_asgi()),                
            ])
        )
    ),
})
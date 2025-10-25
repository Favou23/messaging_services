import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Set Django settings first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_api.settings")
django.setup()

# Import after setup to avoid ImproperlyConfigured errors
from chat.middleware import JwtAuthMiddlewareStack
from chat import routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(routing.websocket_urlpatterns)
    ),
})

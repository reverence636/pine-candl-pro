import os
from django.core.asgi import get_asgi_application
#from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.urls import path, re_path

from testsocket.routing import websocket_urlpatterns
from testsocket.consumers import PracticeWorker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectpine.settings')
django_asgi_app = get_asgi_application()
from channels_auth_token_middlewares.middleware import QueryStringDRFAuthTokenMiddleware

application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": QueryStringDRFAuthTokenMiddleware(
        #"websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns)),
        "channel":ChannelNameRouter(
            {
                "worker_group": PracticeWorker.as_asgi()
            }
        )

    })

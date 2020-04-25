from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import exlibris.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            exlibris.routing.websocket_urlpatterns
        )
    ),
})
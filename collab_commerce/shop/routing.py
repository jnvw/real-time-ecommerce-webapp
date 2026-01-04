from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/group/(?P<secret_code>\w+)/$', consumers.GroupConsumer.as_asgi()),
]

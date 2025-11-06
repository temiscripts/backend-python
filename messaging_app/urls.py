from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from chats.views import ConversationViewSet, MessageViewSet  

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

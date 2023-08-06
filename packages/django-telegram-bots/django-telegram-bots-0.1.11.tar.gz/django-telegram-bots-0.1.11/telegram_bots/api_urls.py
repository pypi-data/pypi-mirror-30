from rest_framework import routers
from .viewsets import BotViewSet, TelegramUserViewSet, AuthorizationViewSet, WebhookViewSet
from django.urls import re_path

app_name = 'api_telegram_bots'

router = routers.SimpleRouter()
router.register(r'^(?P<api_key>.+)/$', WebhookViewSet, base_name='webhook')
router.register(r'bots', BotViewSet)
router.register(r'users', TelegramUserViewSet)
router.register(r'authorizations', AuthorizationViewSet)
urlpatterns = router.urls
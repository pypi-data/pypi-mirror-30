from django.contrib import admin
from .models import Bot, TelegramUser
# Register your models here.

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
	fields = ['api_key']

admin.site.register(TelegramUser)
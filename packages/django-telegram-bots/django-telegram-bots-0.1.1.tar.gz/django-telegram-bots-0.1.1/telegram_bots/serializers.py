from rest_framework import serializers
from .models import Bot, TelegramUser, Authorization
from rest_framework.utils import html, humanize_datetime, json, representation
import collections


class BotListSerializer(serializers.ModelSerializer):

	class Meta:
		model = Bot
		fields = ['first_name', 'username', 'avatar']
		retrieve_fields = ['id']


class MessageSerializer(serializers.Serializer):
	
	type = serializers.ChoiceField(required=True, choices=['HTML', 'Markdown', 'Text'])
	payload = serializers.CharField(required=True, max_length=2000)
	chat_ids = serializers.ListField(min_length=1, max_length=10000, required=True,
		child=serializers.IntegerField(min_value=1, max_value=10000000000))


class BotSerializer(serializers.ModelSerializer):

	class Meta:
		model = Bot
		fields = '__all__'
		retrieve_fields = ['id']


class TelegramUserSerializer(serializers.ModelSerializer):

	class Meta:
		model = TelegramUser
		exclude = ['token', 'chat_id']


class AuthorizationSerializer(serializers.ModelSerializer):

	class Meta:
		model = Authorization
		fields = '__all__'
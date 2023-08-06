from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Bot, TelegramUser, Authorization
from .serializers import BotListSerializer, BotSerializer, MessageSerializer, TelegramUserSerializer, AuthorizationSerializer
from .permissions import IsOwnerOrReadOnly
import ujson as json

from .utils import extract_command, decode_signin, get_bot_model, get_telegram_user_model
from .signals import authorize_user, receive_message, receive_callback_query, receive_command
from .validators import message_schema

from django.shortcuts import get_object_or_404

from cerberus import Validator

v = Validator()


class WebhookViewSet(viewsets.ViewSet):

	@detail_route(methods=['post'])
	def webhook(self, request, api_key):

		bot = get_object_or_404(Bot, api_key=api_key)
		body_unicode = request.body.decode('utf-8')
		payload = json.loads(json.dumps(body_unicode))
		try:
			payload = json.loads(request.body.decode('utf-8'))
		except ValueError:
			return Response('Invalid request body', status=status.HTTP_400_BAD_REQUEST) #HttpResponseBadRequest('Invalid request body')
		else:
			message = payload.get('message', None)
			callback_query = payload.get('callback_query', None)
			if message:
				chat_id = payload['message']['chat']['id']
				#type = payload['message']['chat']['type']
				text = payload['message']['text'] # command
				message = payload['message']
				receive_message.send(sender=Bot, bot_id=bot.bot_id, user_id=chat_id, text=text, message=message)
				command = extract_command(text)
				if command:
					receive_command.send(sender=Bot, bot_id=bot.bot_id, user_id=chat_id, command=command, payload=text)
			if callback_query:
				receive_callback_query.send(sender=Bot, bot_id=bot.bot_id, user_id=callback_query['from']['id'], data=callback_query['data'])
		return Response(status=status.HTTP_200_OK)


class SubscribeViewSet(viewsets.ViewSet):

	@detail_route(methods=['post'])
	def subscribe(self, request, signature):
		data = decode_signin(signature)
		if data:
			user = get_object_or_404(TelegramUser, user__username=data['user_username'])
			bot = get_object_or_404(Bot, username=data['bot_username'])
		try:
			authorize_user.send(
				sender = Bot, 
				key = data['key']
			)
			response = {'link': 'https://telegram.me/{}?start={}'.format(bot.username, user.token)}
			return Response(response, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(e, status=status.HTTP_400_BAD_REQUEST)
		content = {"signature": ["This field is required."]}
		return Response(content, status=status.HTTP_400_BAD_REQUEST)


class BotViewSet(viewsets.ModelViewSet):

	queryset = Bot.objects.all()

	def get_serializer_class(self):
		if not self.action:
			print('hello')
		if self.action == 'list':
			return BotListSerializer
		else:
			return BotSerializer

	def get_permission_classes(self):
		print(self.action)
		if self.action == 'list':
			permission_classes = [IsAuthenticatedOrReadOnly]
		else:
			permission_classes = [IsOwnerOrReadOnly]
		return [permission() for permission in permission_classes]

	@detail_route(methods=['post'])
	def send_message(self, request, pk=None):
		serializer = MessageSerializer(data=request.data)		
		if serializer.is_valid():
			bot = self.get_object()
			users_list = [user_id for user_id in serializer.data['chat_ids'] if user_id in bot.active_auth_user_ids]
			for user_id in users_list:
				bot.send_message(chat_id, serializer.data['payload'])
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@detail_route(methods=['post'])
	def unsubscribe(self, request, pk=None):
		bot = get_object_or_404(Bot, pk=pk)
		user = self.request.user.telegramuser
		#user = get_object_or_404(TelegramUser, user=self.request.user)
		authorization = Authorization.objects.filter(user=user, bot=bot).first()
		if authorization:
			if authorization.is_active:
				authorization.is_active = False
				authorization.save()
				content = {'message': 'You successfully unsubscribed from this bot'}
				return Response(content, status=status.HTTP_200_OK)
		content = {'message': 'You are not a subscriber on this bot'}
		return Response(content, status=status.HTTP_404_NOT_FOUND)

	def create(self, request):
		if 'api_key' in request.data:
			try:
				bot, created = Bot.objects.get_or_create(api_key=request.data['api_key'], owner=self.request.user)
				serializer = self.get_serializer(bot)
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			except Exception as e:
				content = {"message": "Bot with this api key not found"}
				error = json.dumps(e.json)
				message = json.loads(error)
				message.update(content)
				return Response(message, status=status.HTTP_404_NOT_FOUND)
		content = {"api_key": ["This field is required."]}
		return Response(content, status=status.HTTP_400_BAD_REQUEST)


class TelegramUserViewSet(viewsets.ModelViewSet):

	'''
	permissions = IsAuthenticatedOrReadOnly
	queryset = TelegramUser.objects.all()
	serializer_class = TelegramUserSerializer
	'''
	queryset = TelegramUser.objects.all()
	serializer_class = TelegramUserSerializer
	permission_classes = [IsOwnerOrReadOnly]

	@detail_route(methods=['post'])
	def reset_token(self, request, pk=None):
		user = self.get_object()
		if user:
			user.set_token
			serializer = TelegramUserSerializer(user)
			for user in user.authorizations.filter(is_active=True):
				user.is_active = False
				user.save()
			response = {'status': 'The token is reset, all accounts are deactivated'}
			return Response(response, status=status.HTTP_200_OK)
		return Response(status=status.HTTP_404_NOT_FOUND)


class AuthorizationViewSet(viewsets.ModelViewSet):
	'''
	permissions = IsAuthenticatedOrReadOnly
	queryset = Authorization.objects.all()
	serializer_class = AuthorizationSerializer
	'''
	queryset = Authorization.objects.all()
	serializer_class = AuthorizationSerializer
	permission_classes = [IsOwnerOrReadOnly]

	@detail_route(methods=['post'])
	def reset_token(self, request, pk=None):
		'''
		user = self.request.user
        telegramuser = Telegramuser.objects.filter(user=user)
        if telegramuser:
            telegramuser.set_unique_code
            telegramuser.authorization.is_activate = False
            telegramuser.authorization.save()
            telegramuser.save()
		'''
		return Response(status=status.HTTP_200_OK)
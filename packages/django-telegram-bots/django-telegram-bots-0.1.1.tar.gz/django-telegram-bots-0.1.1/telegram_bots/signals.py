from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import Signal
from .utils import extract_data_from_command, get_bot_model, get_telegram_user_model, get_authorization_model
from .services import get_user_from_storage, activate_user


User = get_user_model()
Bot = get_bot_model()
TelegramUser = get_telegram_user_model()
Authentication = get_authorization_model()


receive_message = Signal(providing_args=['bot_id', 'chat_id', 'type', 'text', 'message'])
receive_command = Signal(providing_args=['bot_id', 'chat_id', 'type', 'command', 'payload', 'chat_id'])
receive_callback_query = Signal(providing_args=['bot_id', 'chat_id', 'data'])
authorize_user = Signal(providing_args=['key'])


@receiver(post_save, sender=User)
def create_bot_user(sender, instance, created, **kwargs):
	if created:
		TelegramUser.objects.create(user=instance)


@receiver(receive_command, sender=Bot)
def authentication_user(sender, **kwargs):
	if all(k in kwargs for k in ('command', 'payload', 'chat_id', 'type')):
		command = kwargs['command']
		payload = kwargs['payload']
		chat_id = kwargs['chat_id']
		type = kwargs['type']

		if command == '/start' and payload:
			unique_code = extract_data_from_command(payload)
			if unique_code:
				user = get_user_from_storage(unique_code)
				if user:
					if not user.is_authorized:
						activate_user(user.id, bot_id)
						save_chat_id(chat_id, user)
						reply = 'Hi, {}, the authentication was successful!'.format(user.user.username)
					else:
						reply = '{}, you are already authenticated'.format(user.user.username)
				else:
					reply = 'Unfortunately, I can not authenticate you :('


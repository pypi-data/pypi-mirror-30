from .models import TelegramUser
from annoying.functions import get_object_or_None
from .utils import get_authorization_model, get_bot_model, get_telegram_user_model


Bot = get_bot_model()
User = get_telegram_user_model()
Authorization = get_authorization_model()


def get_user_from_storage(unique_code): 
	user = get_object_or_None(TelegramUser, unique_code=unique_code)
	return user	

def activate_user(user_id, bot_id):
	bot = get_object_or_None(Bot, bot_id=bot_id)
	user = get_object_or_None(User, id=user_id)

	if user and bot:
		authorization, created = Authorization.objects.get_or_create(bot=bot, user=user)
		if not authorization.is_active:
			authorization.is_active = True
			authorization.save()

def deactivate_user(user_id, bot_id):
	bot = get_object_or_None(Bot, bot_id=bot_id)
	user = get_object_or_None(User, id=user_id)

	if user and bot:
		authorization, created = Authorization.objects.get_or_create(bot=bot, user=user)
		if not authorization.is_active:
			authorization.is_active = False
			authorization.save()

def save_chat_id(chat_id, user):
	telegram_user, created = User.objects.get_or_create(user)
	#chat, created = Chat.objects.get_or_create(chat_id=chat_id)
	#chat.type = type
	telegram_user.chat_id = chat_id
	chat.save()
	return chat
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
import logging


logger = logging.getLogger(__name__)


def extract_data_from_command(text):
	return text.split()[1] if len(text.split()) > 1 else None

def extract_command(text):
	return text.split()[0] if text.split()[0].startswith('/', 0, 1) is True else None

def siging_auth(bot_username, user_username, key):
	signature = signing.dumps({
		'bot_username': bot_username,
		'user_username': user_username,
		'key': key
		})
	return signature

def decode_signin(signature):
	sign = None
	try:
		sign = signing.loads(signature, max_age=60*60*24*30)
	except SignatureExpired:
		logger.exception("signature expired")
	except BadSignature:
		logger.exception("signature invalid")
	return sign


def get_bot_model():
	from .models import Bot
	return Bot

def get_telegram_user_model():
	from .models import TelegramUser
	return TelegramUser

def get_authorization_model():
	from .models import Authorization
	return Authorization
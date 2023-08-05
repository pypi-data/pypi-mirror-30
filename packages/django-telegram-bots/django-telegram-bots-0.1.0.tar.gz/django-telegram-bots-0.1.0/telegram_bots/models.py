import telepot
import environ
import string
import random
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from telepot.loop import OrderedWebhook
from collections import defaultdict


env = environ.Env()

@python_2_unicode_compatible
class Bot(models.Model):
	
	api_key = models.CharField(max_length=255, verbose_name=_('API_KEY'), unique=True)
	chat_id = models.CharField(max_length=255, verbose_name=_('Id'))
	first_name = models.CharField(max_length=255, verbose_name=_('First name'))
	username = models.CharField(max_length=255, verbose_name=_('Username'))

	owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Owner'), related_name='bots', on_delete=models.CASCADE)

	@property
	def get_me(self):
		data = self.bot.getMe()
		self.bot_id = data['id']
		self.first_name = data['first_name']
		self.username = data['username']
		return data

	@property
	def bot(self):
		return telepot.Bot(self.api_key)

	@staticmethod
	def send_message(self, chat_id, payload, parse_mode, reply_markup):
		self.bot.sendMessage(chat_id, payload, parse_mode=parse_mode, reply_markup=reply_markup)

	def save(self, *args, **kwargs):
		if not self.pk:
			self.get_me
			self.bot.setWebhook('https://{domain}/bots/{bot_token}/'.format(domain=env('DOMAIN_NAME', default='stagingserver.xyz'), bot_token=self.api_key))
		return super(Bot, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self.bot.deleteWebhook()
		return super(Bot, self).delete(*args, **kwargs)

	@property
	def photos(self):
		photos = defaultdict()
		all_photos = self.bot.bot.getUserProfilePhotos(self.id)
		for photo_counter in range(all_photos['total_count']):
			for photo in all_photos['photos'][photo_counter]:
				if not photo in photos:
					photos[photo] = defaultdict()
				file = self.bot.getFile(photo['file_id'])
				photos[photo] = defaultdict({
					photo['height']: 'https://api.telegram.org/file/bot{}/{}'.format(
						self.api_key,
						file['file_path']
						)
					})
		return photos

	@property
	def avatar(self):
		if self.photos:
			for photos in self.photos:
				for photo in self.photos[photos]:
					return self.photos[photos][photo]
		return None

	class Meta:
		verbose_name = _('Bot')
		verbose_name_plural = _('Bots')

	def __str__(self):
		return '%s' % str(self.first_name)


@python_2_unicode_compatible
class TelegramUser(models.Model):

	user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, verbose_name=_('User'), related_name='telegramuser', on_delete=models.CASCADE)
	token = models.CharField(max_length=255, verbose_name=_('Token'))
	chat_id = models.CharField(max_length=255, verbose_name='User id', null=True, blank=False)

	@property
	def generate_token(self, size=64, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
		token = ''.join(random.choice(chars) for _ in range(size))
		return token

	@property
	def set_token(self):
		self.token = self.generate_token

	@staticmethod
	def check_token(token):
		return self.token == token

	@property
	def authorized(self):
		return self.authorization.is_active

	def save(self, *args, **kwargs):
		if not self.pk or not self.token:
			self.set_token
		return super(TelegramUser, self).save(*args, **kwargs)

	def __str__(self):
		return '%s' % str(self.user.username)


@python_2_unicode_compatible
class Authorization(models.Model):

	bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='authorizations')
	user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name='authorization')
	is_active = models.BooleanField(default=False, verbose_name=_('Is active'))

	@property
	def activation_url(self):
		from .utils import siging_auth
		mamespase = env('TELEGRAM_BOTS_NAMESPACE', default='telegram_bots')
		signature = siging_auth(self.bot.username, self.user.user.username, self.pk)
		return reverse('{}:subscribe/{}'.format(mamespase, signature))


	class Meta:
		unique_together = (('bot', 'user'),)
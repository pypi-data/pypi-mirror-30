from django import forms
from .utils import get_bot_model, get_telegram_user_model
from django.utils.translation import ugettext_lazy as _


Bot = get_bot_model()
User = get_telegram_user_model()

class MessageForm(forms.Form):
	bot = forms.ModelChoiceField(queryset=[], label=_(''))
	type = forms.ChoiceField(choices=['HTML', 'TEXT'])
	users = forms.ModelChoiceField(queryset=[], label=_(''))
	message = forms.CharField(widget=forms.Textarea)

	def __init__(self, request, *args, **kwargs):
		super(MessageForm, self).__init__(*args, **kwargs)
		if request.user:
			bot_queryset = Bot.objects.filter(owner=request.user)
			self.fields['bot'].queryset = bot_queryset
			self.fields['bot'].label = _('Select Telegram bot')

			if bot_queryset:
				users_queryset = []
				for bot in bot_queryset:
					for authorization in bot.authorizations.all():
						users_queryset.append(authorization.user)
				self.fields['users'].queryset = users_queryset
				self.fields['users'].label = _('Select users to send the message')
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404, redirect

from django.http import HttpResponseBadRequest, JsonResponse
from django.http.response import HttpResponse

from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView, RedirectView, FormView
from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _


from .utils import extract_command, decode_signin, get_bot_model, get_telegram_user_model
from .signals import authorize_user, receive_message, receive_callback_query, receive_command
from .forms import MessageForm

import ujson as json


Bot = get_bot_model()
TelegramUser = get_telegram_user_model()


class BotListView(LoginRequiredMixin, ListView):

    model = Bot
    def get_queryset(self):
        queryset = super(BotListView, self).get_queryset()
        return  queryset.filter(signal_sender__user=self.request.user)


class BotDetailView(LoginRequiredMixin, DetailView):

    model = Bot


class BotCreateView(LoginRequiredMixin, CreateView):
    
    model = Bot
    fields = ['api_key']


class BotUpdateView(LoginRequiredMixin, UpdateView):
    
    model = Bot
    fields = ['api_key']


class BotDeleteView(LoginRequiredMixin, DeleteView):

    model = Bot


class CommandReceiveView(View):

    def post(self, request, bot_token):
        bot = get_object_or_404(Bot, api_key=bot_token)
        body_unicode = request.body.decode('utf-8')
        payload = json.loads(json.dumps(body_unicode))
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
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
        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)


class BotSubscribeView(LoginRequiredMixin, RedirectView):

    def get(self, request, signature):
        data = decode_signin(signature)
        if data:
            user = get_object_or_404(TelegramUser, user__username=data['user_username'])
            bot = get_object_or_404(Bot, username=data['bot_username'])
        try:
            authorize_user.send(
                sender = Bot, 
                key = data['key']
            )
            return redirect('https://telegram.me/{}?start={}'.format(bot.username, user.unique_code))
        except Exception as e:
            return HttpResponse(e)

        return super(BotSubscribeView, self).get(request, signature)


class BotUnsubscribeView(LoginRequiredMixin, RedirectView):

    def get(self, request):

        user = self.request.user
        telegramuser = Telegramuser.objects.filter(user=user)
        if telegramuser:
            telegramuser.delete()

        return super(BotSubscribeView, self).get(request)


class BotRefresUserUniqueCode(LoginRequiredMixin, RedirectView):

    def get(self, request):

        user = self.request.user
        telegramuser = Telegramuser.objects.filter(user=user)
        if telegramuser:
            telegramuser.set_unique_code
            telegramuser.authorization.is_activate = False
            telegramuser.authorization.save()
            telegramuser.save()

        return super(BotRefresUserUniqueCode, self).get(request)


class SendMessageView(LoginRequiredMixin, FormView):
    form_class = MessageForm

    def post(self, request, *args, **kwargs):
        
        bot = request.POST.get('bot', None)
        type = request.POST.get('type', None)
        message = request.POST.get('message', None)
        
        if bot and type and message:
            print(bot)
            print(type)
            print(message)
            bot.sendMessage()
        return super(SendMessageView, self).post(request, *args, **kwargs)

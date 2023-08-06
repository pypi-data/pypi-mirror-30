from django.conf.urls import url
from . import views

app_name = 'telegram_bots'
urlpatterns = [
    url(
        regex=r'^$',
        view=views.BotListView.as_view(),
        name='list',
    ),
    url(
        regex=r'^(?P<pk>\d+)/$',
        view=views.BotDetailView.as_view(),
        name='detail',
    ),
    url(
        regex=r'^~create/$',
        view=views.BotCreateView.as_view(),
        name='create',
    ),
    url(
        regex=r'^~update/$',
        view=views.BotUpdateView.as_view(),
        name='update',
    ),
    url(
        regex=r'^~delete/$',
        view=views.BotDeleteView.as_view(),
        name='delete',
    ),
    url(
        regex=r'^~subscribe/(?P<signature>.+)/$',
        view=views.BotSubscribeView.as_view(), 
        name='subscribe'
    ),
    url(
        regex=r'^(?P<bot_token>.+)/$', 
        view=views.CommandReceiveView.as_view(), 
        name='auth'
    ),
]
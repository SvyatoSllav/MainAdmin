from django.urls import path

from . import views

urlpatterns = [
    path(
        'create_user/',
        views.TelegramUserCreateView.as_view(),
        name='telegram_user_create'
    ),
    path(
        'user_info/',
        views.UserInfoView.as_view(),
        name='user_info'
    ),
    path(
        'webinar/',
        views.WebSubscribeView.as_view(),
        name='webinar'
    ),
    path(
        'lead/',
        views.LeadView.as_view(),
        name='telegram_user_create'
    ),
    path(
        'send_msg/',
        views.SendMessageView.as_view(),
        name='msg_by_btn'
    ),
    path(
        'send_contacts/',
        views.MainLeadView.as_view(),
        name='send_contacts'
    ),
]

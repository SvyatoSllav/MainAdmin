from django.contrib import admin
from .models import TelegramUser, UserMessage, CRMMessage


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'first_name',
        'last_name',
        'username',
        'created_at',
    )
    search_fields = ('first_name', 'last_name')


@admin.register(UserMessage)
class UsersMessageAdmin(admin.ModelAdmin):
    list_display = (
        'message',
        'hours_after_registration',
    )


@admin.register(CRMMessage)
class CRMMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'message_id',
        'created_at',
    )

from django.contrib import admin
from django.utils.text import Truncator

from .models import CommandMsg


@admin.register(CommandMsg)
class CommandMsgAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cmd_params',
        'full_link',
        'short_message',
    )

    def short_message(self, obj):
        return Truncator(obj.message).chars(15)

    short_message.short_description = 'Описание'

    @admin.display(description='Полная ссылка')
    def full_link(self, obj):
        return f"https://t.me/web3mainbot?start={obj.cmd_params}"

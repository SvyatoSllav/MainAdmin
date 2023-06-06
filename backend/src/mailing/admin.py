from django.contrib import admin
from django.utils.text import Truncator

from .models import Mailing, MailingButtons


class LinkInline(admin.TabularInline):
    model = MailingButtons


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    inlines = (LinkInline, )

    def short_content_text(self, obj):
        return Truncator(obj.content_text).chars(15)

    short_content_text.short_description = 'Описание'
    list_display = (
        'id',
        'short_content_text',
    )

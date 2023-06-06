from django.contrib import admin
from django.utils.text import Truncator

from .models import Webinar


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'webinar_started_date'
    )
    list_filter = ('webinar_started_date', )
    search_fields = ('title', )

from django.db import models
from src.telegram_user.mixins import UUIDMixin, TimeStampedMixin


class Webinar(UUIDMixin, TimeStampedMixin):
    title = models.CharField(max_length=300, verbose_name='Заголовок')
    description = models.TextField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Описание вебинара в вебапп"
    )
    web_format = models.TextField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Формат встречи"
    )
    day_bf_description = models.TextField(
        verbose_name='Описание вебинара за день'
    )
    hour_bf_description = models.TextField(
        verbose_name='Описание вебинара за час'
    )
    minute_bf_description = models.TextField(
        verbose_name='Описание вебинара за 10 минут'
    )

    day_bf_content = models.ImageField(
        verbose_name='Медиа за день',
        null=True,
        blank=True
    )
    hour_bf_content = models.ImageField(
        verbose_name='Медиа за час',
        null=True,
        blank=True
    )
    minute_bf_content = models.ImageField(
        verbose_name='Медиа за 10 минут',
        null=True,
        blank=True
    )
    webinar_started_date = models.DateTimeField()

    day_bf_calendar_link = models.URLField(
        max_length=200,
        verbose_name='Ссылка на календарь за день',
        blank=True,
    )
    day_bf_webinar_link = models.URLField(
        max_length=200,
        verbose_name='Ссылка на вебинар за день',
        blank=True,
    )

    hour_bf_calendar_link = models.URLField(
        max_length=200,
        verbose_name='Ссылка на календарь за час',
        blank=True,
    )
    hour_bf_webinar_link = models.URLField(
        max_length=200,
        verbose_name='Ссылка на вебинар за час',
        blank=True,
    )

    minute_bf_calendar_link = models.URLField(
        max_length=200,
        verbose_name='Ссылка на календарь за 10 минут',
        blank=True,
    )
    minute_bf_webinar_link = models.URLField(
        max_length=200,
        verbose_name='Ссылка на вебинар за 10 минут',
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вебинар'
        verbose_name_plural = 'Вебинары'

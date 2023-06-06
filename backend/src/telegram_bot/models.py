from django.db import models
from src.telegram_user.mixins import UUIDMixin, TimeStampedMixin


class CommandMsg(UUIDMixin, TimeStampedMixin):
    cmd_params = models.CharField(
        max_length=50,
        blank=False,
        verbose_name="Параметр команды"
    )
    link = models.URLField(
        max_length=200,
        verbose_name='Ссылка на файл',
        blank=True,
        null=True)
    message = models.CharField(
        max_length=3500,
        blank=True,
        verbose_name="Текст сообщения"
    )

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

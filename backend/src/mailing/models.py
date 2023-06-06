from django.db import models
from src.telegram_user.mixins import UUIDMixin, TimeStampedMixin


class Mailing(UUIDMixin, TimeStampedMixin):
    content_text = models.TextField(verbose_name='Текст рассылки')
    content_image = models.ImageField(
        verbose_name='Медиа рассылки (фото)',
        null=True,
        blank=True
    )
    content_video = models.FileField(
        verbose_name='Медиа рассылки (видео)',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.content_text

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class MailingButtons(UUIDMixin):
    button_text = models.CharField(max_length=200, verbose_name='Тескт кнопки')
    mailing_link = models.URLField(max_length=200, verbose_name='Ссылка для кнопки')
    mail = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='mail_link'
    )

    def __str__(self):
        return self.mailing_link

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

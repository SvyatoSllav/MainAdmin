from django.db import models
from .mixins import UUIDMixin, TimeStampedMixin


class TelegramUser(UUIDMixin, TimeStampedMixin):
    user_id = models.BigIntegerField(verbose_name='Юзер ID', unique=True)
    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Имя пользователя"
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Фамилия пользователя',
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Юзернейм'
    )
    subcribed_to_web = models.BooleanField(default=False)
    onboarding_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"""
        {self.user_id}
        {self.first_name}
        {self.username}
        """

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserMessage(UUIDMixin, TimeStampedMixin):
    message = models.CharField(verbose_name='Сообщение', max_length=5000)
    hours_after_registration = models.PositiveIntegerField(
        verbose_name='Часы после регистрации',
        default=0
    )
    content_image = models.ImageField(
        verbose_name='Медиа(фото)',
        null=True,
        blank=True
    )
    content_video = models.FileField(
        verbose_name='Медиа(видео)',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = 'Сообщение пользователю'
        verbose_name_plural = 'Сообщения пользователям'


class CRMMessage(UUIDMixin):
    message_id = models.CharField(
        verbose_name='CRM message id',
        max_length=1000
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="created"
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

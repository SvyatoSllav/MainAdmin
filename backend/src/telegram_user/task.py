from loguru import logger
from datetime import timedelta
from django.utils import timezone

from config.celery import BaseTask, app
from config.settings import BOT, DOMAIN_URL

from .models import UserMessage
from src.telegram_user.models import TelegramUser


class SendMessageTask(BaseTask):
    autoretry_for = ()
    messages_per_minute = 3200

    def proccess(self):
        now = timezone.localtime(timezone.now())
        for message in UserMessage.objects.all():
            logger.info(f'MESSAGE: {message}')
            logger.info(f"NOW: {now}")
            registration_time = now - timedelta(hours=message.hours_after_registration)
            logger.info(f"REGISTRATION TIME: {registration_time}")
            users_to_message = TelegramUser.objects.filter(
                created_at__year=registration_time.year,
                created_at__month=registration_time.month,
                created_at__day=registration_time.day,
                created_at__hour=registration_time.hour,
                created_at__minute=registration_time.minute,
            )

            for user in users_to_message:
                try:
                    if message.content_image:
                        BOT.send_photo(
                            user.user_id,
                            DOMAIN_URL + "/media/" + message.content_image.name.__str__(),
                            caption=message.messge,
                            parse_mode="markdown",
                        )
                    elif message.content_video:
                        BOT.send_video(
                            user.user_id,
                            DOMAIN_URL + "/media/" + message.content_video.name.__str__(),
                            caption=message.content_text,
                            parse_mode="markdown",
                        )
                    else:
                        BOT.send_message(
                            user.user_id,
                            message.content_text,
                            parse_mode="markdown",
                        )
                except Exception as _exc:
                    logger.error(f"ERROR: {_exc}")


send_message_task = app.register_task(SendMessageTask())
app.add_periodic_task(30, send_message_task)

from loguru import logger
from telebot import types
from datetime import timedelta
from django.utils import timezone

from config.celery import BaseTask, app
from config.settings import BOT, DOMAIN_URL

from .models import Webinar
from src.telegram_user.models import TelegramUser


class SendWebinarNotificationsTask(BaseTask):
    autoretry_for = ()
    messages_per_minute = 3200

    def proccess(self):
        now = timezone.now()
        webinars = Webinar.objects.filter(
            webinar_started_date__gte=now,
        )
        logger.info(str(webinars), "WEBINARS")

        for webinar in webinars:
            telegram_users = TelegramUser.objects.filter(subcribed_to_web=True)
            logger.info(str(telegram_users), "TGUSEERS")
            for user in telegram_users:
                SendWebinarNotificationsTask._send_webinar_notification(
                    webinar=webinar,
                    user=user
                )

    @classmethod
    def _send_webinar_notification(cls, webinar, user):
        now = timezone.localtime(timezone.now())
        time_difference = webinar.webinar_started_date - now
        message = ""
        description = ""
        content_name = ""
        reply_markup = None
        logger.info(str(time_difference))
        logger.info('-'*20)
        logger.info(str(timedelta(days=1) >= time_difference >
                    timedelta(hours=23, minutes=59)), "FINAL ")

        if timedelta(minutes=10) >= time_difference > timedelta(minutes=0):
            reply_markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(
                    text="Переходи на вебинар!",
                    url=webinar.minute_bf_webinar_link
                )
            )
            if webinar.minute_bf_calendar_link:
                reply_markup.add(
                    types.InlineKeyboardButton(
                        text="Смотри в календарь!",
                        url=webinar.minute_bf_calendar_link
                    )
                )
            user.subcribed_to_web = False
            user.save()
            message = "Вебинар начнется через 10 минут."
            description = webinar.minute_bf_description
            content_name = webinar.minute_bf_content.name.__str__()
        elif timedelta(hours=1) >= time_difference > timedelta(minutes=59):
            reply_markup = types.InlineKeyboardMarkup()
            if webinar.hour_bf_calendar_link:
                reply_markup.add(
                    types.InlineKeyboardButton(
                        text="Смотри в календарь!",
                        url=webinar.hour_bf_calendar_link
                    )
                )
            if webinar.hour_bf_webinar_link:
                reply_markup.add(
                    types.InlineKeyboardButton(
                        text="Вебинар начнется через час.",
                        url=webinar.hour_bf_webinar_link
                    )
                )
            message = "Вебинар начнется через час."
            description = webinar.hour_bf_description
            content_name = webinar.hour_bf_content.name.__str__()
        elif timedelta(days=1) >= time_difference > timedelta(hours=23, minutes=59):
            reply_markup = types.InlineKeyboardMarkup()
            if webinar.day_bf_calendar_link:
                reply_markup.add(
                    types.InlineKeyboardButton(
                        text="Смотри в календарь!",
                        url=webinar.day_bf_calendar_link
                    )
                )
            if webinar.day_bf_webinar_link:
                reply_markup.add(
                    types.InlineKeyboardButton(
                        text="Вебинар начнется через день.",
                        url=webinar.day_bf_webinar_link
                    )
                )
            message = "Вебинар начнется завтра."
            description = webinar.day_bf_description
            content_name = webinar.day_bf_content.name.__str__()

        if message:
            try:
                webinar_content = [
                    webinar.day_bf_content,
                    webinar.hour_bf_content,
                    webinar.minute_bf_content
                ]
                if not any(webinar_content):
                    BOT.send_message(
                        user.user_id,
                        f"{description}\n{message}",
                        parse_mode="markdown",
                        reply_markup=reply_markup
                    )
                else:
                    BOT.send_photo(
                        user.user_id,
                        DOMAIN_URL + "/media/" + content_name,
                        f"{description}\n{message}",
                        parse_mode="markdown",
                        reply_markup=reply_markup
                    )
            except Exception as _exc:
                logger.info(f"ERROR: {_exc}")


send_webinar_notifications_task = app.register_task(
    SendWebinarNotificationsTask())

app.add_periodic_task(60, send_webinar_notifications_task)

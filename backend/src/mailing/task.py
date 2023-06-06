import time
import logging

from loguru import logger
from telebot import types

from config.celery import BaseTask, app
from .models import Mailing
from src.telegram_user.models import TelegramUser
from config.settings import BOT, DOMAIN_URL


class SendNewsletterTask(BaseTask):
    autoretry_for = ()
    messages_per_minute = 3200

    def proccess(self, newsletter_id):
        mail = Mailing.objects.get(id=newsletter_id)
        telegram_users = TelegramUser.objects.all()
        mailing_buttons = mail.mail_link.all()

        delay = 60 / self.messages_per_minute

        for user in telegram_users:
            try:
                keyboards = types.InlineKeyboardMarkup()
                if mailing_buttons:
                    for button in mailing_buttons:
                        keyboards.add(types.InlineKeyboardButton(
                                text=button.button_text,
                                url=button.mailing_link
                            )
                        )
                if mail.content_image:
                    BOT.send_photo(
                        user.user_id,
                        DOMAIN_URL + "/media/" + mail.content_image.name.__str__(),
                        mail.content_text,
                        parse_mode="markdown",
                        reply_markup=keyboards if mailing_buttons else None
                    )
                elif mail.content_video:
                    BOT.send_video(
                        user.user_id,
                        DOMAIN_URL + "/media/" + mail.content_video.name.__str__(),
                        caption=mail.content_text,
                        parse_mode="markdown",
                        reply_markup=keyboards if mailing_buttons else None
                    )
                else:
                    BOT.send_message(
                        user.user_id,
                        mail.content_text,
                        parse_mode="markdown",
                        reply_markup=keyboards if mailing_buttons else None
                    )

            except Exception as _exc:
                logging.error(f"ERROR: {_exc}")

            time.sleep(delay)


send_newsletter_task = app.register_task(SendNewsletterTask())

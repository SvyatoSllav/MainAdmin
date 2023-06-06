import os
import time
from pathlib import Path
from dotenv import load_dotenv

from telebot import types

from urllib.parse import unquote
from urllib3.exceptions import ConnectTimeoutError

from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from amocrm.v2 import Contact as _Contact, Lead as _Lead, tokens, custom_field

from config.settings import BOT

from src.telegram_bot.models import CommandMsg

from src.telegram_user.models import TelegramUser, CRMMessage
from src.telegram_user import message_const
from src.telegram_user import error_const
from src.telegram_bot.views import get_menu_web_app


from loguru import logger


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
load_dotenv()

tokens.default_token_manager(
    client_id=str(os.environ.get("CRM_CLIENT_ID")),
    client_secret=str(os.environ.get("CRM_CLIENT_SECRET")),
    subdomain=str(os.environ.get("CRM_SUBDOMAIN")),
    redirect_url="https://ya.ru",
    storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
)
tokens.default_token_manager.init(
    code=os.environ.get("CRM_CODE"),
    skip_error=True
)


class Contact(_Contact):
    phone = custom_field.ContactPhoneField("Телефон")
    webinar = custom_field.CheckboxCustomField("Подписан на вебинар")
    user_id = custom_field.TextAreaCustomField("TelegramId_WZ")


class Lead(_Lead):
    phone = custom_field.ContactPhoneField("Телефон")


class TelegramUserCreateView(APIView):
    def post(self, request):
        """
        Creates user in db.
        Processes commands, that are saved to db.
        """
        try:
            body_dict = self._parse_crm_message_body(body=request.body)
            logger.info(f"BODY DICT: {body_dict}")
            contact_id = body_dict["message[add][0][contact_id]"]
            crm_message_id = body_dict["message[add][0][id]"]
            message_text = body_dict["message[add][0][text]"]
            contact = Contact.objects.get(query=contact_id)
            user_id = contact.user_id
            # Проверяю, не является ли сообщение дубликатом
            if CRMMessage.objects.filter(id=crm_message_id).first():
                return JsonResponse(
                    {"error": "message are duplicated"}, status=400
                )
            # Сохраняю сообщения и удаляю те, которые старше 1 дня
            self._save_new_delete_old_crm_msg(crm_message_id)
            self._create_unexisted_user(
                user_id=user_id,
                username=contact.name
            )
            self._handle_msg(user_id=user_id, message_text=message_text)
            return Response("Expected start cmd.")
        except AssertionError:
            return JsonResponse(
                {"Error": error_const.CRM_RESPONSE_ERROR},
                status=500
            )
        except ConnectTimeoutError as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {
                    'Error': error_const.TELEGRAM_CONNECTION_TIMEOUT
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def _parse_crm_message_body(body):
        """
        Parse the body of the request from CRM.
        Returns a dictionary with message attrs.
        """
        try:
            body_text = body.decode('utf-8')
            body_text = unquote(body_text)
            body_list = [el.split("=") for el in body_text.split("&")]
            return dict(body_list)
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return JsonResponse(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def _save_new_delete_old_crm_msg(crm_message_id: int):
        """
        Creates new message in db
        and delete all messages, that older than 1 day.
        """
        CRMMessage.objects.create(message_id=crm_message_id)
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        CRMMessage.objects.filter(created_at__lt=one_day_ago).delete()

    @staticmethod
    def _create_unexisted_user(user_id: int, username: str):
        """
        Creates user if it doesn't exist.
        """
        if not TelegramUser.objects.filter(user_id=user_id).exists():
            TelegramUser.objects.create(
                user_id=user_id,
                username=username
            )

    @classmethod
    def _send_file_msg(cls, user_id: str, cmd_params: str):
        """
        Handles start command with params
        if appropriate object are created in db.
        """
        if CommandMsg.objects.filter(cmd_params=cmd_params).exists():
            cmd = CommandMsg.objects.get(cmd_params=cmd_params)
            text = cmd.message.replace("<br/>", "\n")
            if cmd.link:
                reply_markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(
                        text="Ссылка на файл",
                        url=cmd.link
                    )
                )
                BOT.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                BOT.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="HTML"
                )
        BOT.set_chat_menu_button(
            chat_id=user_id, menu_button=get_menu_web_app())

    @staticmethod
    def _handle_msg(user_id: int, message_text: str):
        """
        Handles a message and executes appropriate actions.
        """
        BOT.set_chat_menu_button(
            chat_id=user_id,
            menu_button=get_menu_web_app()
        )
        if message_text[:7] == "/start+":
            cmd_params = message_text.split("+")[1]
            if cmd_params == "webinar":
                # TODO Скопировать функционал по добавлению в веб
                BOT.send_message(
                    chat_id=user_id,
                    text=message_const.WEBINAR_MSG
                )
                return Response("Success")
            TelegramUserCreateView._send_file_msg(
                user_id=user_id,
                cmd_params=cmd_params
            )
            return Response("Account is created successfully.")
        elif message_text == "/start":
            BOT.send_message(
                chat_id=user_id,
                text=message_const.FIRST_START_MESSAGE
            )
            time.sleep(10)
            BOT.send_message(
                chat_id=user_id,
                text=message_const.SECOND_START_MESSAGE
            )
            time.sleep(10)
            path_to_photo = BASE_DIR / "/media/msg_media.png/"
            print(path_to_photo)
            BOT.send_photo(
                chat_id=user_id,
                caption=message_const.THIRD_START_MESSAGE,
                photo=open(path_to_photo, 'rb'),
            )
            return JsonResponse(
                {"status": "Account is created successfully."},
                status=200
            )


class UserInfoView(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id').replace("/", "")
            user_from_db = get_object_or_404(TelegramUser, user_id=user_id)
            user_from_crm = Contact.objects.get(query=user_id)
            representation = {
                "onboarding_complete": user_from_db.onboarding_complete,
                "phone": ""
            }
            if user_from_crm.phone:
                representation["phone"] = user_from_crm.phone
            return JsonResponse(representation)
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            phone = request.data.get("phone")
            onboarding_complete = request.data.get("onboarding_complete")
            representation = {"user_id": user_id}
            user_from_db = get_object_or_404(TelegramUser, user_id=user_id)
            user_from_crm = Contact.objects.get(query=user_id)
            if not user_id:
                return Response("There was no user id")
            if phone:
                user_from_crm.phone = phone
                user_from_crm.save()
            if onboarding_complete:
                user_from_db.onboarding_complete = True
                user_from_db.save()
            representation["phone"] = user_from_crm.phone
            representation["onboarding_complete"] = onboarding_complete
            return JsonResponse(representation)
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )


class WebSubscribeView(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id').replace("/", "")
            user = get_object_or_404(TelegramUser, user_id=user_id)
            return JsonResponse({"is_subscribed": user.subcribed_to_web})
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            user_from_db = get_object_or_404(TelegramUser, user_id=user_id)
            user_from_crm = Contact.objects.get(query=user_id)
            user_from_db.subcribed_to_web = not user_from_db.subcribed_to_web
            webinar_tag = {"id": 76985, "name": "Вебинар"}
            new_tags = [webinar_tag] if not user_from_crm.webinar else []
            user_from_crm.webinar = not user_from_crm.webinar
            lead = Lead.objects.get(query=user_id)
            for tag in lead.tags:
                new_tags.append({"id": tag.id, "name": f"{tag.name}"})
            Lead.objects.update(
                lead.id,
                data={
                    "_embedded": {"tags": new_tags}
                }
            )
            user_from_crm.save()
            user_from_db.save()
            return JsonResponse({"is_subscribed": user_from_crm.webinar})
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )


class LeadView(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id').replace("/", "")
            lead = Lead.objects.get(query=user_id)
            return JsonResponse({"lead_id": lead.id})
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        """
        Получае тип кнопки нажатой на фронтенде.
        В соответствии с типом кнопки, создаёт сделку
        с нужными тегами и в нужном этапе amoCRM
        :return dict[lead_id, int]
        """
        try:
            user_id: int = request.data.get('user_id')
            btn_type: str = request.data.get('btn_type') or "support"
            # Первое число в списке отвечает за id тэга сделки.
            # Второй параметр отвечает за имя тэга
            # Третье число в списке отвечает за id этапа сделки.
            btn_type_to_tag = {
                "support": [73226, "Срочно свяжись с клиентом", 57798586],
                "buy_main": [73228, "Самостоятельное оформление", 57634970],
                "main_from_binance": [73228, "Самостоятельное оформление", 57168166],
                "main_from_crypto": [73228, "Самостоятельное оформление", 57168162],
                "main_from_numma": [73228, "Самостоятельное оформление", 57634970],
                "staking": [73230, "Стейкинг, проверь покупку", 57168170],
                "ask_access": [76957, "Доступ Бэкеры", 57168158],
            }
            lead = Lead.objects.get(query=user_id)
            new_tags = [
                {
                    "id": btn_type_to_tag[btn_type][0],
                    "name": btn_type_to_tag[btn_type][1]
                },
            ]
            # Функционал, который считывает изначальные теги,
            # которые необходимо оставить и добавляет их в новый список тегов
            for tag in lead.tags:
                if tag.id == 38499:
                    new_tags.append({"id": 38499, "name": "WZ (web3mainbot)"})
                if tag.id == 51063:
                    new_tags.append({"id": 51063, "name": f"{tag.name}"})
            Lead.objects.update(
                lead.id,
                data={
                    "status_id": btn_type_to_tag[btn_type][2],
                    "_embedded": {"tags": new_tags}
                }
            )
            return JsonResponse({"lead_id": lead.id})
        except ConnectTimeoutError as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {
                    'Error': 'There was an error with telegram services.'
                             'Please try again later'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )


class MainLeadView(APIView):
    def post(self, request):
        try:
            username: str = request.data.get('username')
            phone: str = request.data.get('phone')
            lead = Lead.objects.create(
                name=username,
                phone=phone,
            )
            return JsonResponse({"lead_id": lead.id})
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )


class SendMessageView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('user_id').replace("/", "")
            msg_btn = request.query_params.get('msg_btn').replace("/", "")
            if not any((user_id, msg_btn)):
                return JsonResponse({"error": "You need to provide user id and msg_btn"})
            btn_to_text = {
                "main_from_numma": message_const.MAIN_FROM_NUMMA,
                "main_from_crypto": message_const.MAIN_FROM_CRYPTO,
                "main_from_binance": message_const.MAIN_FROM_BINANCE,
                "staking_main": message_const.STAKING_MAIN,
                "sell_main": message_const.SELL_MAIN,
                "ask_access": message_const.ASK_ACCESS,
                "pancakeswap": message_const.PANCAKE_SWAP,
            }
            message = btn_to_text[msg_btn]
            BOT.send_message(user_id, message, parse_mode="HTML")
            return JsonResponse({"status": "message was sent"})
        except ConnectTimeoutError as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {
                    'Error': 'There was an error with telegram services.'
                             'Please try again later'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as _exc:
            logger.error(f"ERROR: {_exc}")
            return Response(
                {'Error': error_const.UNEXPECTED_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )

import os
from telebot import types


def get_menu_web_app():
    url = str(os.environ.get("WEBAPP_URL"))
    web_app = types.WebAppInfo(url=url)
    btn = types.MenuButtonWebApp(
        type="web_app",
        text="Меню",
        web_app=web_app
    )
    return btn

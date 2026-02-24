from asgiref.sync import sync_to_async
from django.db import InterfaceError, connection

from admin_panel.telebot.models import Users


@sync_to_async
def create_user(telegram_id, name, username):
    """
    Функция, позволяющая создать новую запись пользователя
    в соответствующей таблице

    telegram_id = id пользователя в телеграме
    name = имя пользователя
    username = username пользователя

    """

    try:
        Users.objects.get_or_create(
            telegram_id=telegram_id,
            name=name,
            username=username
        )
    except InterfaceError:
        connection.close()


@sync_to_async()
def get_user(telegram_id):
    """
    Функция, позволяющая получить информацию по пользователю из БД
    При вызове используем как объект.

    Пример:

    user = await get_user(message.from_user.id)

    print(user.id)
    print(user.telegram_id)
    print(user.name)
    print(user.username)

    """

    try:
        return Users.objects.filter(telegram_id=telegram_id).first()
    except InterfaceError:
        connection.close()

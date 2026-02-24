import logging

from aiogram import Dispatcher, types

from bot.data.config import admins


async def on_startup_notify(dp: Dispatcher):
    for admin in admins:
        try:
            await dp.bot.send_message(admin, "<b>Бот запущен!</b>", parse_mode=types.ParseMode.HTML)

        except Exception as err:
            logging.exception(err)

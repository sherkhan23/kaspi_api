import os

import django




async def on_startup(dp):
    from bot import filters
    from bot import middlewares
    filters.setup(dp)
    middlewares.setup(dp)
    from bot.utils.set_bot_commands import set_default_commands
    from bot.utils.notify_admins import on_startup_notify

    await on_startup_notify(dp)
    await set_default_commands(dp)


def setup_django():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        'admin_panel.admin_panel.settings'
    )
    os.environ.update({"DJANGO_ALLOW_ASYNC_UNSAFE": "true"})
    django.setup()


if __name__ == '__main__':
    setup_django()
    from aiogram import executor
    from bot.handlers import dp

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

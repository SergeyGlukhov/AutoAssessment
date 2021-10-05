from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from assessment_src.models import db
from assessment_src.telebot.handlers.registration_admin import register_handlers_admin
from assessment_src.telebot.handlers.create_work import create_work_handlers_admin
from assessment_src.telebot.handlers.estimate_work import estimate_work_handlers
from assessment_src.telebot.handlers.show_works import show_works_handlers


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/registration_admin", description="Регистрация админа"),
        BotCommand(command="/create_work", description="[Админ] Создать работу"),
        BotCommand(command="/show_works", description="[Админ] Посмотреть созданные работы"),
        BotCommand(command="/estimate_work", description="Отправить оценку"),
    ]
    await bot.set_my_commands(commands)


async def run_bot(dp: Dispatcher, bot: Bot):

    register_handlers_admin(dp)
    create_work_handlers_admin(dp)
    estimate_work_handlers(dp)
    show_works_handlers(dp)

    await set_commands(bot)

    await dp.skip_updates()
    await dp.start_polling()

    await db.pop_bind().close()
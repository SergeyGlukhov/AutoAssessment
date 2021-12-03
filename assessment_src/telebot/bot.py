from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from assessment_src.models import db

from assessment_src.telebot.handlers.admin.registration_admin import register_handlers_admin
from assessment_src.telebot.handlers.admin.create_work import create_work_handlers_admin
# from assessment_src.telebot.handlers.admin.settings_admin import settings_admin_handlers
from assessment_src.telebot.handlers.admin.show_works import show_works_handlers

from assessment_src.telebot.handlers.student.send_grade import send_grade_handlers
from assessment_src.telebot.handlers.admin.admin import admin_handlers
from assessment_src.telebot.handlers.common import menu_handlers_common
from assessment_src.telebot.handlers.student.settings import settings_handlers
from assessment_src.telebot.handlers.student.show_grades import show_grades_handlers


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Старт"),
        BotCommand(command="/admin", description="Действия для админа"),
        BotCommand(command="/registration_admin", description="Регистрация админа"),
        BotCommand(command="/create_work", description="[Админ] Создать работу"),
        BotCommand(command="/show_works", description="[Админ] Посмотреть созданные работы"),
        BotCommand(command="/send_grade", description="Отправить оценку"),
        BotCommand(command="/show_grades", description="Отправленные оценки"),
        BotCommand(command="/settings", description="Настройки"),
        BotCommand(command="/help", description="Справка"),
        BotCommand(command="/cancel", description="Отменить"),

    ]
    await bot.set_my_commands(commands)


async def run_bot(dp: Dispatcher, bot: Bot):

    settings_handlers(dp)
    admin_handlers(dp)
    menu_handlers_common(dp)
    register_handlers_admin(dp)
    # settings_admin_handlers(dp)
    show_grades_handlers(dp)
    # register_handlers_common(dp)
    create_work_handlers_admin(dp)
    send_grade_handlers(dp)
    show_works_handlers(dp)

    await set_commands(bot)

    await dp.skip_updates()
    await dp.start_polling()

    await db.pop_bind().close()
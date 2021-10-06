from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
#
# from assessment_src.telebot.handlers.admin.registration_admin import (
#     start_registration, AdminRegistrationState, register_handlers_admin, verify_new_student_for_registration
# )


class AdminState(StatesGroup):
    wait_for_start = State()
    wait_for_registration = State()
    wait_for_show_works = State()
    wait_for_settings = State()


def get_admin_keyboard():
    buttons = [
        "Регистрация", "Создать работу",
        "Мои работы", "Настройки",
        "Помощь", "В меню"
    ]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


async def back_menu_admin(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Добро пожаловать в меню админа!",
        reply_markup=get_admin_keyboard()
    )
    await AdminState.wait_for_start.set()


def admin_handlers(dp: Dispatcher):
    dp.register_message_handler(back_menu_admin, commands="admin", state="*")
    dp.register_message_handler(back_menu_admin, Text(equals="Админ", ignore_case=True), state="*")
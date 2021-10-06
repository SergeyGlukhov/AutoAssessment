from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from assessment_src.telebot.logic.query_db import (
    get_student_from_db,
    update_student_db_fio,
    update_student_db_email
)
from assessment_src.telebot.handlers.common import back_menu


class SetSettingsState(StatesGroup):
    wait_for_start = State()
    wait_for_fio = State()
    wait_for_email = State()


def get_settings_keyboard():
    buttons = [
        "ФИО", "Email",
        "Помощь", "В меню"
    ]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


async def cmd_settings(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Выберите настройки, которые хотите поменять:",
        reply_markup=get_settings_keyboard()
    )
    await SetSettingsState.wait_for_start.set()


async def start_settings(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("В меню")

    student = await get_student_from_db(message.from_user.id)
    if not student:
        await state.finish()
        await message.answer(
            """
            Вас нет в системе.\n
            Для начала вам нужно отправить оценку или зарегистрироваться админом.\n
            /send_grade - Отправить оценку\n
            /registration_admin - Регистрация админом\n
            """
        )
        return
    if message.text == "ФИО":
        await SetSettingsState.wait_for_fio.set()
        await message.answer(
            f"""
            Ваше ФИО: {student.fio}\n
            Новое значение:\n
            """,
            reply_markup=keyboard
        )
    elif message.text == "Email":
        await SetSettingsState.wait_for_email.set()
        await message.answer(
            f"""
            Ваш email: {student.fio}\n
            Новое значение:\n
            """,
            reply_markup=keyboard
        )
    elif message.text == "В меню":
        await back_menu(message, state)
    else:
        await cmd_settings(message, state)


async def update_fio(message: types.Message, state: FSMContext):
    await update_student_db_fio(message.from_user.id, message.text)
    await cmd_settings(message, state)


async def update_email(message: types.Message, state: FSMContext):
    await update_student_db_email(message.from_user.id, message.text)
    await cmd_settings(message, state)


def settings_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_settings, commands="settings", state="*")
    dp.register_message_handler(cmd_settings, Text(equals="Настройки", ignore_case=True), state="*")
    dp.register_message_handler(start_settings, state=SetSettingsState.wait_for_start)
    dp.register_message_handler(update_fio, state=SetSettingsState.wait_for_fio)
    dp.register_message_handler(update_email, state=SetSettingsState.wait_for_email)




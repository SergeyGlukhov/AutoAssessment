from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from assessment_src.telebot.logic.query_db import (
    get_admin_settings_from_db,
    update_group_db,
    update_faculty_db,
    update_university_db,
    update_city_db
)
from assessment_src.telebot.handlers.admin.admin import back_menu_admin


class SettingsAdminState(StatesGroup):
    wait_for_start = State()
    wait_for_city = State()
    wait_for_university = State()
    wait_for_faculty = State()
    wait_for_group = State()


def get_settings_admin_keyboard():
    buttons = [
        "Город", "Учебное заведение",
        "Факультет", "Группа",
        "Назад"
    ]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


async def cmd_settings(message: types.Message, state: FSMContext):
    await state.finish()

    admin_settings = await get_admin_settings_from_db(message.from_user.id)
    if not admin_settings:
        await message.answer(
            "У вас нет полномочий админа.\n/registration_admin - Регистрация админом\n"
        )
        await back_menu_admin(message, state)
        return

    await state.update_data(admin_settings=admin_settings)

    await message.answer(
        f"Ваши настройки:\nГород: {admin_settings.city}\nУниверситет: {admin_settings.university}\nФакультет: {admin_settings.faculty}\nГруппа: {admin_settings.group}"
    )

    await message.answer(
        "Выберите настройки, которые хотите поменять:",
        reply_markup=get_settings_admin_keyboard()
    )
    await SettingsAdminState.wait_for_start.set()


async def start_settings(message: types.Message, state: FSMContext):

    data = await state.get_data()
    admin_settings = data.get("admin_settings")

    if message.text == "Город":
        await SettingsAdminState.wait_for_city.set()
        await message.answer(
            f"Ваш город: {admin_settings.city}\nНовое значение:\n",
        )
    elif message.text == "Учебное заведение":
        await SettingsAdminState.wait_for_university.set()
        await message.answer(
            f"Ваш учебное заведение: {admin_settings.university}\nНовое значение:\n",
        )
    elif message.text == "Факультет":
        await SettingsAdminState.wait_for_faculty.set()
        await message.answer(
            f"Ваш факультет: {admin_settings.faculty}\nНовое значение:\n",
        )
    elif message.text == "Группа":
        await SettingsAdminState.wait_for_group.set()
        await message.answer(
            f"Ваш группа: {admin_settings.group}\nНовое значение:\n",
        )
    else:
        await cmd_settings(message, state)


async def update_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    admin_settings = data.get("admin_settings")
    await update_city_db(admin_settings.city_id, message.text)
    await cmd_settings(message, state)


async def update_university(message: types.Message, state: FSMContext):
    data = await state.get_data()
    admin_settings = data.get("admin_settings")
    await update_university_db(admin_settings.university_id, message.text)
    await cmd_settings(message, state)


async def update_faculty(message: types.Message, state: FSMContext):
    data = await state.get_data()
    admin_settings = data.get("admin_settings")
    await update_faculty_db(admin_settings.faculty_id, message.text)
    await cmd_settings(message, state)


async def update_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    admin_settings = data.get("admin_settings")
    await update_group_db(admin_settings.group_id, message.text)
    await cmd_settings(message, state)


def settings_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_settings, commands="settings_admin", state="*")
    dp.register_message_handler(cmd_settings, Text(equals="Настройки админа", ignore_case=True), state="*")

    dp.register_message_handler(back_menu_admin, Text(equals="Назад", ignore_case=True), state=SettingsAdminState)

    dp.register_message_handler(start_settings, state=SettingsAdminState.wait_for_start)
    dp.register_message_handler(update_city, state=SettingsAdminState.wait_for_city)
    dp.register_message_handler(update_university, state=SettingsAdminState.wait_for_university)
    dp.register_message_handler(update_faculty, state=SettingsAdminState.wait_for_faculty)
    dp.register_message_handler(update_group, state=SettingsAdminState.wait_for_group)




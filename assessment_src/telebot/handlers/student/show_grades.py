import os
from contextlib import suppress

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from assessment_src.telebot.logic.query_db import (
    get_student_from_db,
    get_subjects_from_db,
    get_my_grades_from_db
)
from assessment_src.telebot.handlers.common import get_back_menu_keyboard, back_menu


class ShowGradesState(StatesGroup):
    wait_for_choice_subject = State()


cb_subjects = CallbackData("subjects", "name", "id")


def get_keyboard(object_list: list, call_back: CallbackData):
    buttons = [
        types.InlineKeyboardButton(text=f"{obj.name}", callback_data=call_back.new(id=obj.id, name=obj.name))
        for obj in object_list
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def update_message_keyboard(message: types.Message, new_text: str, object_list: list, call_back: CallbackData):
    with suppress(MessageNotModified):
        await message.edit_text(f"Выберите {new_text}", reply_markup=get_keyboard(object_list, call_back))


async def show_subjects(message: types.Message):
    student = await get_student_from_db(message.from_user.id)
    subjects = await get_subjects_from_db(group_id=student.group_id)
    await message.answer(message.text, reply_markup=get_back_menu_keyboard())
    await message.answer("Выберите предмет:", reply_markup=get_keyboard(subjects, cb_subjects))
    await ShowGradesState.wait_for_choice_subject.set()


async def choice_subject(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    if call.message.text == "Назад":
        await call.answer()
        await back_menu(call.message, state)
        return

    subject_name = callback_data["name"]
    await state.update_data(subject_name=subject_name)

    grades = await get_my_grades_from_db(student_id=call.from_user.id, subject_id=int(callback_data.get("id")))

    await call.message.edit_text(f"Предмет: {subject_name}", reply_markup=types.InlineKeyboardMarkup())

    grades_text = ""
    for g in grades:
        grades_text += f"Работа: {g.work_name}, оценка: {g.grade}\n"
    await call.message.answer(f"Ваши оценки:\n{grades_text}")

    await call.answer()
    await back_menu(call.message, state)


def show_grades_handlers(dp: Dispatcher):
    dp.register_message_handler(show_subjects, commands="show_grades")
    dp.register_message_handler(show_subjects, Text(equals="Отправленные оценки", ignore_case=True), state="*")

    dp.register_message_handler(back_menu, Text(equals="Назад", ignore_case=True), state=ShowGradesState)

    dp.register_callback_query_handler(
        choice_subject,
        cb_subjects.filter(),
        state=ShowGradesState.wait_for_choice_subject
    )

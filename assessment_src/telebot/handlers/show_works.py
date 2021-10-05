import os
from contextlib import suppress

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from assessment_src.telebot.logic.query_db import (
    get_works_from_db, get_student_from_db, get_subjects_from_db, get_students_grades_from_db
)


class ShowWorksState(StatesGroup):
    wait_for_choice_subject = State()
    wait_for_choice_work = State()
    wait_for_choice_load = State()


cb_subjects = CallbackData("subjects", "name", "id")
cb_works = CallbackData("works", "name", "id")


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
    await message.answer("Выберите предмет:", reply_markup=get_keyboard(subjects, cb_subjects))
    await ShowWorksState.wait_for_choice_subject.set()


async def choice_subject(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(subject_name=callback_data["name"])

    works = await get_works_from_db(subject_id=int(callback_data["id"]), user_id=call.from_user.id)
    await call.message.edit_text("Выберите работу:", reply_markup=get_keyboard(works, cb_works))
    await call.answer()
    await ShowWorksState.next()


async def choice_work(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    work_id = int(callback_data["id"])
    students_grades = await get_students_grades_from_db(work_id)
    message = ""
    for sg in students_grades:
        message += f"{sg.fio} - {sg.grade.grade}\n"
    await call.message.answer(message)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for answer in ["Да", "Нет"]:
        keyboard.add(answer)
    await state.update_data(grades_students=message, work_name=callback_data["name"])
    await call.message.answer("Загрузить?", reply_markup=keyboard)
    await call.answer()

    await ShowWorksState.next()


async def choice_load(message: types.Message, state: FSMContext):

    if message.text not in ("Да", "Нет"):
        await message.answer("Нажмите на кнопку ниже.")
        return
    if message.text == "Нет":
        await state.finish()
        return

    data = await state.get_data()
    subject_name = "".join(data.get("subject_name").split())
    work_name = "".join(data.get("work_name").split())
    with open(f"{subject_name}-{work_name}.txt", "w") as file:
        file.write(data.get("grades_students"))
    await message.answer_document(
        types.input_file.InputFile(file.name),
        reply_markup=types.ReplyKeyboardRemove()
    )
    path = os.path.join(file.name)
    os.remove(path)
    await state.finish()


def show_works_handlers(dp: Dispatcher):
    dp.register_message_handler(show_subjects, commands="show_works")
    dp.register_callback_query_handler(
        choice_subject,
        cb_subjects.filter(),
        state=ShowWorksState.wait_for_choice_subject
    )
    dp.register_callback_query_handler(
        choice_work,
        cb_works.filter(),
        state=ShowWorksState.wait_for_choice_work
    )
    dp.register_message_handler(choice_load, state=ShowWorksState.wait_for_choice_load)


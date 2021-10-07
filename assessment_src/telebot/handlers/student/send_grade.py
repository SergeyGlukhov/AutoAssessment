from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from assessment_src.telebot.logic.query_db import (
    get_student_from_db,
    get_work_from_db,
    set_grade_to_db, create_student, get_grade_from_db,
)
from assessment_src.telebot.handlers.common import back_menu


def get_send_grade_keyboard():
    buttons = ["В меню"]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


class SendGradeState(StatesGroup):
    wait_for_token = State()
    wait_for_verify_student = State()
    wait_for_fio = State()
    wait_for_grade = State()


async def start_send_grade(message: types.Message):
    await message.answer("Введите токен работы:", reply_markup=get_send_grade_keyboard())
    await SendGradeState.wait_for_token.set()


async def token_input(message: types.Message, state: FSMContext):

    if message.text == "В меню":
        await back_menu(message, state)
        return

    token = message.text
    work = await get_work_from_db(token=token)
    if not work:
        await message.answer(f"Такой работы нет. Попробуй еще раз.", reply_markup=get_send_grade_keyboard())
        return

    await state.update_data(admin_id=work.admin_id)

    grade = await get_grade_from_db(work_id=work.id, user_id=message.from_user.id)
    if grade:
        await message.answer(f"Ваша оценка: {grade.grade} уже выставлена.\n", reply_markup=get_send_grade_keyboard())
        await back_menu(message, state)
        return

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
    keyboard.add("Продолжить", "В меню")
    await message.answer("Нажмите кнопку ниже.", reply_markup=keyboard)

    await state.update_data(
        id=message.from_user.id,
        admin_id=work.admin_id,
        group_id=work.group_id,
        work_id=work.id
    )
    await SendGradeState.wait_for_verify_student.set()


async def verify_student(message: types.Message, state: FSMContext):

    if message.text == "В меню":
        await back_menu(message, state)
        return

    if message.text != "Продолжить":
        await message.answer("Нажмите кнопку ниже.")
        return

    data = await state.get_data()

    student = await get_student_from_db(user_id=data.get("id"))
    if not student:
        await message.answer(f"Введите ФИО:", reply_markup=get_send_grade_keyboard())
        await SendGradeState.wait_for_fio.set()
        return

    await message.answer(f"Введите оценку:", reply_markup=get_send_grade_keyboard())
    await SendGradeState.wait_for_grade.set()


async def fio_input(message: types.Message, state: FSMContext):

    if message.text == "В меню":
        await back_menu(message, state)
        return

    await state.update_data(fio=message.text)

    await message.answer("Введите оценку:", reply_markup=get_send_grade_keyboard())
    await SendGradeState.next()


# @dp.message_handler(state=SendGradeState.wait_for_grade)
async def grade_input(message: types.Message, state: FSMContext):
    await state.update_data(grade=message.text)
    data = await state.get_data()
    await set_grade_to_db(data)
    await message.answer(f"Оценка занесена в систему.")
    # await
    await back_menu(message, state)


def send_grade_handlers(dp: Dispatcher):
    dp.register_message_handler(start_send_grade, commands="send_grade", state="*")
    dp.register_message_handler(start_send_grade, Text(equals="Отправить оценку", ignore_case=True), state="*")
    dp.register_message_handler(token_input, state=SendGradeState.wait_for_token)
    dp.register_message_handler(verify_student, state=SendGradeState.wait_for_verify_student)
    dp.register_message_handler(fio_input, state=SendGradeState.wait_for_fio)
    dp.register_message_handler(grade_input, state=SendGradeState.wait_for_grade)

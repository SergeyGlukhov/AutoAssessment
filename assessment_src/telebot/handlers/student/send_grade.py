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
from assessment_src.telebot.handlers.common import get_back_menu_keyboard


class SendGradeState(StatesGroup):
    wait_for_token = State()
    wait_for_verify_student = State()
    wait_for_fio = State()
    wait_for_grade = State()


async def start_send_grade(message: types.Message):
    await message.answer("Введите токен работы:", reply_markup=get_back_menu_keyboard())
    await SendGradeState.wait_for_token.set()


async def token_input(message: types.Message, state: FSMContext):

    token = message.text
    work = await get_work_from_db(token=token)
    if not work:
        await message.answer(f"Такой работы нет. Попробуй еще раз.")
        return

    # await state.update_data(admin_id=work.admin_id, work_name=work.name)

    grade = await get_grade_from_db(work_id=work.id, user_id=message.from_user.id)
    if grade:
        await message.answer(f"Ваша оценка: {grade.grade} уже выставлена.\n")
        await back_menu(message, state)
        return

    await message.answer("Нажмите кнопку ниже.", reply_markup=get_back_menu_keyboard(["Продолжить"]))

    await state.update_data(
        id=message.from_user.id,
        admin_id=work.admin_id,
        group_id=work.group_id,
        work_id=work.id,
        work_name=work.name
    )
    await SendGradeState.wait_for_verify_student.set()


async def verify_student(message: types.Message, state: FSMContext):

    if message.text != "Продолжить":
        await message.answer("Нажмите кнопку ниже.")
        return

    data = await state.get_data()

    student = await get_student_from_db(user_id=data.get("id"))
    if not student:
        await message.answer(f"Введите ФИО:")
        await SendGradeState.wait_for_fio.set()
        return
    await state.update_data(fio=student.fio)
    await message.answer(f"Введите оценку:")
    await SendGradeState.wait_for_grade.set()


async def fio_input(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите оценку:")
    data = await state.get_data()
    await create_student(data)
    await SendGradeState.next()


async def grade_input(message: types.Message, state: FSMContext):
    await state.update_data(grade=message.text)
    data = await state.get_data()
    await set_grade_to_db(data)
    fio = data.get("fio")
    grade = message.text
    work_name = data.get("work_name")

    await message.from_user.bot.send_message(data.get("admin_id"), f"Работа {work_name}: {fio} - {grade}")

    await message.answer(f"Оценка занесена в систему.")

    await back_menu(message, state)


def send_grade_handlers(dp: Dispatcher):
    dp.register_message_handler(start_send_grade, commands="send_grade", state="*")
    dp.register_message_handler(start_send_grade, Text(equals="Отправить оценку", ignore_case=True), state="*")

    dp.register_message_handler(back_menu, Text(equals="Назад", ignore_case=True), state=SendGradeState)

    dp.register_message_handler(token_input, state=SendGradeState.wait_for_token)
    dp.register_message_handler(verify_student, state=SendGradeState.wait_for_verify_student)
    dp.register_message_handler(fio_input, state=SendGradeState.wait_for_fio)
    dp.register_message_handler(grade_input, state=SendGradeState.wait_for_grade)

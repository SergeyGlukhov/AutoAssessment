from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from assessment_src.telebot.logic.query_db import (
    get_student_from_db,
    get_work_from_db,
    set_grade_to_db, create_student, get_grade_from_db,
)


class EstimateState(StatesGroup):
    wait_for_token = State()
    wait_for_verify_student = State()
    wait_for_fio = State()
    wait_for_email = State()
    wait_for_grade = State()


async def start_estimate_work(message: types.Message):
    await message.answer("Введите токен работы:")
    await EstimateState.wait_for_token.set()


async def token_input(message: types.Message, state: FSMContext):
    token = message.text
    work = await get_work_from_db(token=token)
    if not work:
        await message.answer(f"Такой работы нет. Попробуй еще раз.")
        return

    grade = await get_grade_from_db(work_id=work.id, user_id=message.from_user.id)
    if grade:
        await message.answer(f"Ваша оценка: {grade.grade} уже выставлена.\n")
        await state.finish()
        return

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
    keyboard.add("Продолжить")
    await message.answer("Нажмите кнопку ниже.", reply_markup=keyboard)

    await state.update_data(
        id=message.from_user.id,
        admin_id=work.admin_id,
        group_id=work.group_id,
        work_id=work.id
    )
    await EstimateState.wait_for_verify_student.set()


async def verify_student(message: types.Message, state: FSMContext):
    if message.text != "Продолжить":
        await message.answer("Нажмите кнопку ниже.")
        return

    data = await state.get_data()

    student = await get_student_from_db(user_id=data.get("id"))
    if not student:
        await message.answer(f"Введите ФИО:")
        await EstimateState.wait_for_fio.set()
        return

    await message.answer(f"Введите оценку:")
    await EstimateState.wait_for_grade.set()


async def fio_input(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите email:")
    await EstimateState.next()


async def email_input(message: types.Message, state: FSMContext):
    email = message.text
    if not message.text.find('@') or not message.text.find('.'):
        await message.answer("Вы ввели не коректный email.")
        email = None
    await state.update_data(email=email)
    data = await state.get_data()
    student = await create_student(data)
    await message.answer("Ваше ФИО и email занесены в систему.")
    await message.answer("Введите оценку:")
    await EstimateState.next()


async def grade_input(message: types.Message, state: FSMContext):
    await state.update_data(grade=message.text)
    data = await state.get_data()
    await set_grade_to_db(data)
    await message.answer(f"Оценка занесена в систему.")
    await state.finish()


def estimate_work_handlers(dp: Dispatcher):
    dp.register_message_handler(start_estimate_work, commands="estimate_work", state="*")
    dp.register_message_handler(token_input, state=EstimateState.wait_for_token)
    dp.register_message_handler(verify_student, state=EstimateState.wait_for_verify_student)
    dp.register_message_handler(fio_input, state=EstimateState.wait_for_fio)
    dp.register_message_handler(email_input, state=EstimateState.wait_for_email)
    dp.register_message_handler(grade_input, state=EstimateState.wait_for_grade)

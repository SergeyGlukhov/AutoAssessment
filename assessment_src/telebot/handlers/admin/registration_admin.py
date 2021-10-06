from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from assessment_src.telebot.logic.query_db import (
    set_registration_admin_to_db,
    get_student_from_db,
    update_student_admin,
)


class AdminRegistrationState(StatesGroup):
    wait_for_start = State()
    wait_for_city = State()
    wait_for_university = State()
    wait_for_faculty = State()
    wait_for_group = State()
    wait_for_fio = State()
    wait_for_email = State()


async def verify_new_student_for_registration(message: types.Message):

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
    keyboard.add("Старт")
    await message.answer("Нажмите кнопку ниже.", reply_markup=keyboard)
    await AdminRegistrationState.wait_for_start.set()


async def start_registration(message: types.Message, state: FSMContext):

    student = await get_student_from_db(message.from_user.id)
    if student:
        if student.is_admin:
            await message.answer("Повторно регистрироваться запрещено")
            await state.finish()
            return
        else:
            await update_student_admin(student)
            await message.answer("Вам присвоен статус админа.")
            await state.finish()
            return

    await state.update_data(id=message.from_user.id)
    await message.answer("Введите город:")
    await AdminRegistrationState.next()
    # await RegistrationState.wait_for_city.set()


async def city_input(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer("Некорректный город:")
        return
    await state.update_data(city=message.text)

    await message.answer("Введите учебное заведение:")
    await AdminRegistrationState.next()


async def university_input(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer("Некорректное учебное заведение, повторите попытку:")
        return

    await state.update_data(university=message.text)
    await message.answer("Введите факультет:")
    await AdminRegistrationState.next()


async def faculty_input(message: types.Message, state: FSMContext):

    await state.update_data(faculty=message.text)

    await message.answer("Введите группу:")
    await AdminRegistrationState.next()


async def group_input(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text)

    await AdminRegistrationState.next()
    await message.answer("Введите ФИО:")


async def fio_input(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите email:")
    await AdminRegistrationState.next()


async def email_input(message: types.Message, state: FSMContext):
    email = message.text
    if not message.text.find('@') or not message.text.find('.'):
        await message.answer("Вы ввели не коректный email.")
        email = None
    await state.update_data(email=email)
    data = await state.get_data()
    await set_registration_admin_to_db(data)
    await message.answer("Вы зарегистрировались.")
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(
        verify_new_student_for_registration,
        commands="registration_admin",
        state="*"
    )
    dp.register_message_handler(
        verify_new_student_for_registration,
        Text(equals="Регитрация", ignore_case=True),
        state="*"
    )
    dp.register_message_handler(start_registration, state=AdminRegistrationState.wait_for_start)
    dp.register_message_handler(city_input, state=AdminRegistrationState.wait_for_city)
    dp.register_message_handler(university_input, state=AdminRegistrationState.wait_for_university)
    dp.register_message_handler(faculty_input, state=AdminRegistrationState.wait_for_faculty)
    dp.register_message_handler(group_input, state=AdminRegistrationState.wait_for_group)
    dp.register_message_handler(fio_input, state=AdminRegistrationState.wait_for_fio)
    dp.register_message_handler(email_input, state=AdminRegistrationState.wait_for_email)


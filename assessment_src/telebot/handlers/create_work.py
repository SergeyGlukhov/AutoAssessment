from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from assessment_src.telebot.logic.query_db import set_work_to_db, get_student_from_db


class CreateWorkState(StatesGroup):
    wait_for_start = State()
    wait_for_subject = State()
    wait_for_fio = State()
    wait_for_email = State()
    wait_for_work = State()


async def verify_new_student(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )
    keyboard.add("Старт")
    await message.answer("Нажмите кнопку ниже.", reply_markup=keyboard)
    await CreateWorkState.wait_for_start.set()


async def start_create_work(message: types.Message, state: FSMContext):
    if message.text != "Старт":
        await message.answer("Нажмите кнопку ниже.")
        return

    student = await get_student_from_db(message.from_user.id)
    if not student or not student.is_admin:
        await message.answer(f"Для начала необходимо зарегестрироваться - /registration_admin")
        await state.finish()
        return

    await state.update_data(id=message.from_user.id, group_id=student.group_id)
    await message.answer("Введите название предмета:")
    await CreateWorkState.next()
    # await RegistrationState.wait_for_city.set()


async def subject_input(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)

    await message.answer("Введите ФИО преподавателя:")
    await CreateWorkState.next()


async def fio_input(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите email преподавателя:")
    await CreateWorkState.next()


async def email_input(message: types.Message, state: FSMContext):
    email = message.text
    if not message.text.find('@') or not message.text.find('.'):
        await message.answer("Вы ввели не коректный email.")
        email = None
    await state.update_data(email=email)
    await message.answer("Введите назыание работы:")
    await CreateWorkState.next()


async def work_input(message: types.Message, state: FSMContext):
    await state.update_data(work=message.text)
    data = await state.get_data()
    token = await set_work_to_db(data)
    await message.answer(f"Работа создана.\n /estimate_work доступна по токену:")
    await message.answer(token)
    await state.finish()


def create_work_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(verify_new_student, commands="create_work", state="*")
    dp.register_message_handler(start_create_work, state=CreateWorkState.wait_for_start)
    dp.register_message_handler(subject_input, state=CreateWorkState.wait_for_subject)
    dp.register_message_handler(fio_input, state=CreateWorkState.wait_for_fio)
    dp.register_message_handler(email_input, state=CreateWorkState.wait_for_email)
    dp.register_message_handler(work_input, state=CreateWorkState.wait_for_work)

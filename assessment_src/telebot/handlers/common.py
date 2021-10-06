from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


def get_menu_keyboard():
    buttons = [
        "Админ", "Отправить оценку",
        "Отправленные оценки", "Настройки",
        "Помощь"
    ]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


def get_back_menu_keyboard(buttons_add: list = None):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if buttons_add:
        keyboard.add(*buttons_add)

    keyboard.add("Назад")
    return keyboard


def get_help_cmd():
    text_help = """
    Список команд:\n
    /start - Главное меню\n
    /admin - Действия для админа\n
    /registration_admin - Регистрация админа\n
    /create_work - [Админ] Создать работу\n
    /show_works - [Админ] Посмотреть созданные работы\n
    /send_grade - Отправить оценку\n
    /settings - Настройки\n
    /help - Справка\n
    /cancel - Отменить, в главное меню\n
    """
    return text_help


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Добро пожаловать в меню!",
        reply_markup=get_menu_keyboard()
    )


async def back_menu(message: types.Message, state: FSMContext):
    await cmd_start(message, state)


async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(get_help_cmd())


def menu_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")

    dp.register_message_handler(back_menu, commands="cancel", state="*")
    dp.register_message_handler(back_menu, Text(equals="В меню", ignore_case=True), state="*")

    dp.register_message_handler(cmd_help, commands="help", state="*")
    dp.register_message_handler(cmd_help, Text(equals="Помощь", ignore_case=True), state="*")
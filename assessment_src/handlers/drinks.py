from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Эти значения далее будут подставляться в итоговый текст, отсюда
# такая на первый взгляд странная форма прилагательных
available_drink_names = ["кола", "пепси", "фанта"]
available_drink_sizes = ["0.2l", "0.35l", "0.5l"]


class OrderDrink(StatesGroup):
    waiting_for_drink_name = State()
    waiting_for_drink_size = State()


async def drink_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for name in available_drink_names:
        keyboard.add(name)
    await message.answer("Выберите напиток:", reply_markup=keyboard)
    await OrderDrink.waiting_for_drink_name.set()


# Обратите внимание: есть второй аргумент
async def drink_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drink_names:
        await message.answer("Пожалуйста, выберите питок, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_drink=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in available_drink_sizes:
        keyboard.add(size)
    # Для последовательных шагов можно не указывать название состояния, обходясь next()
    await OrderDrink.next()
    await message.answer("Теперь выберите объем:", reply_markup=keyboard)


async def drink_size_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_drink_sizes:
        await message.answer("Пожалуйста, выберите объем, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await message.answer(f"Вы заказали {message.text.lower()} объемом {user_data['chosen_drink']}.\n"
                         f"Попробуйте теперь заказать еду: /food", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_drink(dp: Dispatcher):
    dp.register_message_handler(drink_start, commands="drink", state="*")
    dp.register_message_handler(drink_chosen, state=OrderDrink.waiting_for_drink_name)
    dp.register_message_handler(drink_size_chosen, state=OrderDrink.waiting_for_drink_size)


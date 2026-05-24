import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8884454862:AAG4LZHahU-2Gbh4H95U3MSIil9sTmbBjIg"
ADMIN_ID = 5212719988

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ---------------- STATES ----------------

class Form(StatesGroup):
    school_class = State()
    fullname = State()
    reason = State()
    hobby = State()
    text = State()


# ---------------- MENU ----------------

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🟡🔵 Вступити до ради")],
        [KeyboardButton(text="💡 Питання / Порада")],
        [KeyboardButton(text="⚠️ Скарга")]
    ],
    resize_keyboard=True
)


# ---------------- START ----------------

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Вітаємо!\n\n"
        "Це офіційна приймальня "
        "Президентської ради ліцею №89 "
        "ім. Григорія Цихмістренка.\n\n"
        "Тут ви можете подати заявку "
        "до ради або залишити звернення.",
        reply_markup=keyboard
    )


# ---------------- JOIN ----------------

@dp.message(F.text == "🟡🔵 Вступити до ради")
async def join(message: Message, state: FSMContext):

    await state.update_data(category="Вступ до ради")

    await message.answer("📚 Введіть ваш клас:")
    await state.set_state(Form.school_class)


# ---------------- OTHER ----------------

@dp.message(F.text.in_(["💡 Питання / Порада", "⚠️ Скарга"]))
async def other(message: Message, state: FSMContext):

    await state.update_data(category=message.text)

    await message.answer("📚 Введіть ваш клас:")
    await state.set_state(Form.school_class)


# ---------------- CLASS ----------------

@dp.message(Form.school_class)
async def school_class(message: Message, state: FSMContext):

    await state.update_data(school_class=message.text)

    await message.answer("👤 Введіть ім'я та прізвище:")
    await state.set_state(Form.fullname)


# ---------------- FULLNAME ----------------

@dp.message(Form.fullname)
async def fullname(message: Message, state: FSMContext):

    await state.update_data(fullname=message.text)

    data = await state.get_data()

    if data["category"] == "Вступ до ради":

        await message.answer(
            "❓ Чому ви хочете вступити до ради?"
        )

        await state.set_state(Form.reason)

    else:

        await message.answer(
            "✍️ Напишіть ваше звернення:"
        )

        await state.set_state(Form.text)


# ---------------- REASON ----------------

@dp.message(Form.reason)
async def reason(message: Message, state: FSMContext):

    await state.update_data(reason=message.text)

    await message.answer(
        "🎯 Чим би ви хотіли займатися у раді?"
    )

    await state.set_state(Form.hobby)


# ---------------- FINAL JOIN ----------------

@dp.message(Form.hobby)
async def hobby(message: Message, state: FSMContext):

    await state.update_data(hobby=message.text)

    data = await state.get_data()
    user = message.from_user

    msg = f"""
📩 НОВА ЗАЯВКА ДО ПРЕЗИДЕНТСЬКОЇ РАДИ

👤 Ім'я: {data['fullname']}
📚 Клас: {data['school_class']}
❓ Чому хоче вступити:
{data['reason']}

🎯 Чим хоче займатися:
{data['hobby']}

🆔 ID: {user.id}
"""

    await bot.send_message(ADMIN_ID, msg)

    await message.answer(
        "Дякуємо за заявку!\n\n"
        "Президентська рада перегляне її "
        "найближчим часом і, "
        "за потреби, зв’яжеться з вами."
    )

    await state.clear()


# ---------------- FINAL OTHER ----------------

@dp.message(Form.text)
async def text(message: Message, state: FSMContext):

    await state.update_data(text=message.text)

    data = await state.get_data()
    user = message.from_user

    msg = f"""
📩 НОВЕ ЗВЕРНЕННЯ

📌 Тип: {data['category']}
👤 Ім'я: {data['fullname']}
📚 Клас: {data['school_class']}

✍️ Текст:
{data['text']}

🆔 ID: {user.id}
"""

    await bot.send_message(ADMIN_ID, msg)

    await message.answer(
        "Дякуємо за звернення!\n\n"
        "За потреби представники ради "
        "зв’яжуться з вами."
    )

    await state.clear()


# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, GBt_key
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.dispatcher.router import Router

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Словарь для хранения городов пользователей
user_cities = {}

# Определение состояний для ввода города
class SetCityState(StatesGroup):
    waiting_for_city = State()

# Функция для получения данных о погоде
def get_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={GBt_key}&units=metric&lang=ru'
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            city_name = data['name']
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            wind_speed_kmh = round(wind_speed * 3.6, 1)
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            pressure_mmHg = round(pressure * 0.75006)
            sunrise = data['sys']['sunrise']
            sunset = data['sys']['sunset']

            from datetime import datetime
            sunrise_time = datetime.fromtimestamp(sunrise).strftime('%H:%M:%S')
            sunset_time = datetime.fromtimestamp(sunset).strftime('%H:%M:%S')

            return {
                "city_name": city_name,
                "temperature": temperature,
                "feels_like": feels_like,
                "description": description,
                "wind_speed": wind_speed,
                "wind_speed_kmh": wind_speed_kmh,
                "humidity": humidity,
                "pressure": pressure_mmHg,
                "sunrise": sunrise_time,
                "sunset": sunset_time
            }
        else:
            return f"Ошибка: не удалось получить данные о погоде для {city} (код {response.status_code})"
    except requests.exceptions.ReadTimeout:
        return "Превышено время ожидания ответа от сервера. Попробуйте позже."
    except requests.exceptions.RequestException as e:
        return f"Произошла ошибка при запросе данных: {e}"

# Создаем инлайн-клавиатуру с кнопками
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Погода", callback_data="weather"), InlineKeyboardButton(text="Установить город", callback_data="set_city")],
    
])

# Создаем нижнее меню с кнопками
reply_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/help")]
    ]
)

# Обработчик команд /start и /help
@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(f"Доброго дня, {message.from_user.full_name}! Хорошей погоды! ☀️", reply_markup=inline_keyboard)

@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer("Этот бот предоставляет следующие команды:\n"
                         "/start - запуск бота\n"
                         "/help - помощь\n"
                         "Нажмите кнопки ниже для взаимодействия.", reply_markup=inline_keyboard)

# Обработчик для callback-запросов
@router.callback_query()
async def handle_callback(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == 'start':
        await callback_query.message.answer(f"Доброго дня, {callback_query.from_user.full_name}! Хорошей погоды! ☀️", reply_markup=inline_keyboard)
    elif data == 'help':
        await callback_query.message.answer("Этот бот предоставляет следующие команды:\n"
                                            "/start - запуск бота\n"
                                            "/help - помощь\n"
                                            "Нажмите кнопки ниже для взаимодействия.", reply_markup=inline_keyboard)
    elif data == 'weather':
        city = user_cities.get(user_id, 'Smolensk')
        weather_data = get_weather(city)
        if isinstance(weather_data, dict):
            await callback_query.message.answer(f"🌆 Город: {weather_data['city_name']}\n"
                                                f"🌡️ Температура: {weather_data['temperature']}°C\n"
                                                f"🤗 Ощущается как: {weather_data['feels_like']}°C\n"
                                                f"☁️ Погодные условия: {weather_data['description']}\n"
                                                f"💨 Скорость ветра: {weather_data['wind_speed']} м/с ({weather_data['wind_speed_kmh']} км/ч)\n"
                                                f"💧 Влажность: {weather_data['humidity']}%\n"
                                                f"🔽 Давление: {weather_data['pressure']} мм рт. ст.\n"
                                                f"🌅 Восход солнца: {weather_data['sunrise']}\n"
                                                f"🌇 Закат солнца: {weather_data['sunset']}", reply_markup=inline_keyboard)
        else:
            await callback_query.message.answer(weather_data, reply_markup=inline_keyboard)
    elif data == 'set_city':
        await callback_query.message.answer("Пожалуйста, введите название города для установки:", reply_markup=inline_keyboard)
        await state.set_state(SetCityState.waiting_for_city)

    await callback_query.answer()

@router.message(SetCityState.waiting_for_city)
async def city_received(message: Message, state: FSMContext):
    city = message.text
    user_id = message.from_user.id
    user_cities[user_id] = city
    await message.answer(f"Город успешно установлен: {city} 🌍", reply_markup=inline_keyboard)
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

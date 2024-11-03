import asyncio
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN, GBt_key

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь для хранения городов пользователей
user_cities = {}

# Функция для получения данных о погоде
def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={GBt_key}&units=metric&lang=ru'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        humidity = data['main']['humidity']
        return {
            "temperature": temperature,
            "feels_like": feels_like,
            "description": description,
            "wind_speed": wind_speed,
            "humidity": humidity
        }
    else:
        return None

# Обработчики команд
@dp.message(Command('help'))
async def help(message: Message):
    await message.answer('Этот бот умеет выполнять команды:\n'
                         '/start - запуск бота\n'
                         '/help - помощь\n'
                         '/setcity <город> - установить город для прогноза\n'
                         '/weather - текущая погода\n'
                         '/wind - информация о ветре\n'
                         '/humidity - информация о влажности\n'
                         '/temperature - температура и ощущаемая температура')

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Доброго дня, {message.from_user.full_name}! Хорошей погоды!")

@dp.message(Command('setcity'))
async def set_city(message: Message):
    if message.text and len(message.text.split()) > 1:
        city = message.text.split(maxsplit=1)[1]
        user_id = message.from_user.id
        user_cities[user_id] = city  # Сохраняем город для пользователя
        await message.answer(f"Город успешно установлен: {city}")
    else:
        await message.answer("Пожалуйста, укажите город после команды. Пример: /setcity Москва")

@dp.message(Command('weather'))
async def weather(message: Message):
    user_id = message.from_user.id
    city = user_cities.get(user_id, 'Smolensk')  # Используем город пользователя или по умолчанию Смоленск
    weather_data = get_weather(city)
    if weather_data:
        await message.answer(f"Город: {city}\n"
                             f"Температура: {weather_data['temperature']}°C\n"
                             f"Ощущается как: {weather_data['feels_like']}°C\n"
                             f"Погодные условия: {weather_data['description']}\n"
                             f"Скорость ветра: {weather_data['wind_speed']} м/с\n"
                             f"Влажность: {weather_data['humidity']}%")
    else:
        await message.answer(f"Не удалось получить данные о погоде для {city}. Проверьте правильность запроса или доступность API.")

@dp.message(Command('wind'))
async def wind(message: Message):
    user_id = message.from_user.id
    city = user_cities.get(user_id, 'Smolensk')
    weather_data = get_weather(city)
    if weather_data:
        await message.answer(f"Город: {city}\nСкорость ветра: {weather_data['wind_speed']} м/с")
    else:
        await message.answer(f"Не удалось получить данные о погоде для {city}.")

@dp.message(Command('humidity'))
async def humidity(message: Message):
    user_id = message.from_user.id
    city = user_cities.get(user_id, 'Smolensk')
    weather_data = get_weather(city)
    if weather_data:
        await message.answer(f"Город: {city}\nВлажность: {weather_data['humidity']}%")
    else:
        await message.answer(f"Не удалось получить данные о погоде для {city}.")

@dp.message(Command('temperature'))
async def temperature(message: Message):
    user_id = message.from_user.id
    city = user_cities.get(user_id, 'Smolensk')
    weather_data = get_weather(city)
    if weather_data:
        await message.answer(f"Город: {city}\nТемпература: {weather_data['temperature']}°C\nОщущается как: {weather_data['feels_like']}°C")
    else:
        await message.answer(f"Не удалось получить данные о погоде для {city}.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

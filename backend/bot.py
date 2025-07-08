import json
import logging
import asyncio
import sys
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Добавляем текущую папку в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорты локальных модулей
from config import Config
from database import DatabaseManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=Config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db_manager = DatabaseManager()

# Состояния для FSM
class FeedbackStates(StatesGroup):
    waiting_for_feedback = State()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Приветственное сообщение с дружелюбным тоном"""
    user = message.from_user
    
    # Регистрация пользователя
    if user:
        db_user = db_manager.get_user_by_telegram_id(user.id)
        if not db_user:
            db_manager.register_user(
                user.id, 
                user.username or '', 
                user.first_name or '', 
                user.last_name or ''
            )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🏫 Открыть школьное приложение", 
            web_app=WebAppInfo(url=Config.WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        f"Привет, {user.first_name if user else 'друг'}! 👋\n\n"
        f"🎓 **Добро пожаловать в {Config.SCHOOL_NAME}!**\n\n"
        "Рады видеть тебя в нашей школьной семье! Здесь ты можешь:\n\n"
        "• 📅 Посмотреть расписание уроков\n"
        "• 📝 Узнать домашние задания\n"
        "• 📊 Проверить свои оценки\n"
        "• 📢 Читать школьные объявления\n"
        "• 💬 Связаться с администрацией\n\n"
        "Нажми кнопку ниже, чтобы открыть приложение! ⬇️",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    """Обработка данных от Mini App с дружелюбными ответами"""
    try:
        if message.web_app_data and message.web_app_data.data:
            data = json.loads(message.web_app_data.data)
            action = data.get('action')
            role = data.get('role', 'student')
            
            logger.info(f"Получены данные от Mini App: {action}, роль: {role}")
            
            if action == 'open_section':
                await handle_section_request(message, data.get('section'), role)
            elif action == 'feedback':
                await handle_feedback_request(message, data)
            elif action == 'main_menu':
                await start_command(message)
            else:
                await message.answer("Неизвестное действие 🤔\nПопробуй выбрать что-то другое!")
        else:
            await message.answer("Не удалось получить данные от приложения 😅")
                
    except json.JSONDecodeError:
        await message.answer("Упс! Что-то пошло не так 😅\nПопробуй еще раз!")
    except Exception as e:
        logger.error(f"Ошибка обработки данных веб-приложения: {e}")
        await message.answer("Произошла ошибка при обработке запроса 🔧")



async def handle_section_request(message: types.Message, section: str, role: str):
    """Обработка запросов к разделам с дружелюбным тоном"""
    responses = {
        'schedule': "📅 **Держи актуальное расписание на сегодня!**\n\n"
                   "**10А класс:**\n"
                   "1. 8:00-8:45 - Математика (каб. 201) 👨‍🏫\n"
                   "2. 8:55-9:40 - Русский язык (каб. 105) 👩‍🏫\n"
                   "3. 9:50-10:35 - История (каб. 301) 👨‍🏫\n"
                   "4. 10:55-11:40 - Физика (каб. 205) 👩‍🏫\n"
                   "5. 11:50-12:35 - Английский (каб. 102) 👩‍🏫\n\n"
                   "Удачного дня! 🌟",
        
        'homework': "📝 **У тебя есть новые домашние задания!**\n\n"
                   "**Математика** (до 09.12):\n"
                   "• Стр. 127, №№ 15-20\n"
                   "• Подготовься к контрольной! 📊\n\n"
                   "**Русский язык** (до 08.12):\n"
                   "• Сочинение 200-250 слов ✍️\n\n"
                   "**История** (до 10.12):\n"
                   "• Параграф 12, вопросы 1-7 📚\n\n"
                   "Не забудь выполнить все задания! 💪",
        
        'grades': "📊 **Твои последние оценки:**\n\n"
                 "**Математика:** 4, 5, 4 (средний: 4.3) 📈\n"
                 "**Русский язык:** 5, 4, 5 (средний: 4.7) 🌟\n"
                 "**История:** 4, 4, 3 (средний: 3.7) 📖\n"
                 "**Физика:** 5, 5, 4 (средний: 4.7) ⚡\n\n"
                 "**Общий средний балл: 4.4** 🎯\n\n"
                 "Отличная работа! Так держать! 👏",
        
        'announcements': "📢 **Школьные новости и объявления:**\n\n"
                        "🔴 **ВАЖНО!** Изменения в расписании\n"
                        "8 декабря физика переносится на 6 урок\n\n"
                        "🎉 **День открытых дверей**\n"
                        "15 декабря в 15:00 - приглашаем всех!\n\n"
                        "👨‍👩‍👧‍👦 **Родительское собрание**\n"
                        "20 декабря в 18:00\n\n"
                        "Следи за обновлениями! 📱"
    }
    
    response = responses.get(section, "Не могу найти эту информацию 🔍\nПопробуй выбрать другой раздел!")
    await message.answer(response, parse_mode='Markdown')

async def handle_feedback_request(message: types.Message,  dict):
    """Обработка запросов обратной связи"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Предложение", callback_data="feedback_suggestion"),
            InlineKeyboardButton(text="❗ Жалоба", callback_data="feedback_complaint")
        ],
        [
            InlineKeyboardButton(text="❓ Вопрос", callback_data="feedback_question"),
            InlineKeyboardButton(text="👏 Благодарность", callback_data="feedback_compliment")
        ]
    ])
    
    await message.answer(
        "💬 **Обратная связь**\n\n"
        "Выберите тип обращения:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def main():
    """Главная функция для запуска бота"""
    logger.info(f"🚀 Запуск бота {Config.SCHOOL_NAME}...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())

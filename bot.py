import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

# -------------------- КОНФИГУРАЦИЯ --------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]          # Токен задаётся в переменных окружения Render
PORT = int(os.getenv("PORT", "10000"))       # Порт для health-check (Render подставит свой)

# -------------------- НАСТРОЙКА ЛОГИРОВАНИЯ --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("ascend_ai_bot")

# -------------------- ИНИЦИАЛИЗАЦИЯ БОТА --------------------
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# -------------------- КЛАВИАТУРА --------------------
def main_keyboard():
    """Клавиатура с кнопкой для открытия мини-приложения"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть приложение",
                    web_app=WebAppInfo(url="https://ai-w28s.onrender.com"),
                )
            ]
        ]
    )

# -------------------- ОБРАБОТЧИК КОМАНДЫ /start --------------------
@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Ascend AI твой личный помощник по улучшению внешности!\n"
        "Нажми на кнопку ниже чтобы начать👇",
        reply_markup=main_keyboard(),
    )

# -------------------- HEALTH-CHECK СЕРВЕР (для Render) --------------------
async def health_handler(request):
    return web.Response(text="OK")

async def start_health_server():
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Health server started on port {PORT}")
    return runner

# -------------------- ГЛАВНАЯ ФУНКЦИЯ --------------------
async def main():
    health_runner = await start_health_server()
    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    finally:
        await health_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

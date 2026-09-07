import os
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# =========================
# Настройки
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

WEB_APP_URL = "https://ai-w28s.onrender.com"

if not BOT_TOKEN:
    raise RuntimeError("Не задана переменная окружения BOT_TOKEN")

if not RENDER_EXTERNAL_URL:
    raise RuntimeError("Не задана переменная окружения RENDER_EXTERNAL_URL")


# =========================
# Логирование
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =========================
# Telegram
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

dp.include_router(router)


# =========================
# Кнопка Mini App
# =========================

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Начать",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )


# =========================
# /start
# =========================

@router.message(CommandStart())
async def start_handler(message: Message):
    text = (
        "Ascend AI твой личный помощник по улучшению внешности! \n\n"
        "Нажми на кнопку ниже чтобы начать👇"
    )

    await message.answer(
        text,
        reply_markup=get_main_keyboard()
    )


# =========================
# Webhook
# =========================

async def health_check(request: web.Request):
    return web.Response(text="Ascend AI Bot is running!")


async def webhook_handler(request: web.Request):
    try:
        update_data = await request.json()

        from aiogram.types import Update

        update = Update.model_validate(update_data)

        await dp.feed_update(
            bot,
            update
        )

        return web.Response(text="OK")

    except Exception:
        logger.exception("Ошибка обработки webhook")
        return web.Response(
            text="Internal Server Error",
            status=500
        )


# =========================
# Запуск
# =========================

async def on_startup(app: web.Application):
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"

    logger.info(f"Устанавливаем webhook: {webhook_url}")

    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )

    logger.info("Webhook установлен")


async def on_shutdown(app: web.Application):
    logger.info("Удаляем webhook")

    await bot.delete_webhook()

    await bot.session.close()


# =========================
# Aiohttp server
# =========================

app = web.Application()

app.router.add_get("/", health_check)
app.router.add_post("/webhook", webhook_handler)

app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))

    web.run_app(
        app,
        host="0.0.0.0",
        port=port
    )

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не задана!")

PORT = int(os.environ.get("PORT", 8443))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    message_text = (
        "Ascend AI твой личный помощник по улучшению внешности! \n"
        "Нажми на кнопку ниже чтобы начать👇"
    )
    web_app_url = "https://ai-w28s.onrender.com"
    keyboard = [[InlineKeyboardButton("Открыть приложение", web_app=web_app_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message_text, reply_markup=reply_markup)

def main():
    """Запуск бота с вебхуком"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # URL для вебхука (Render предоставляет RENDER_EXTERNAL_URL)
    render_external_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_external_url:
        webhook_url = f"{render_external_url}/webhook"
    else:
        # Для локального тестирования – укажите свой URL после деплоя
        webhook_url = "https://your-app-name.onrender.com/webhook"
        logging.warning("RENDER_EXTERNAL_URL не задан, используется значение по умолчанию")

    logging.info(f"Установка вебхука: {webhook_url}")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()

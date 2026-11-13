"""7/24 Jarvis Telegram Botu giris noktasi."""

from __future__ import annotations

import logging

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from jarvis_bot.config import load_config
from jarvis_bot.jarvis_agent import JarvisAgent
from jarvis_bot.telegram_handlers import JarvisTelegramHandlers


def build_application() -> Application:
    """Yapilandirmayi yukler ve Telegram Application nesnesini olusturur."""
    load_dotenv()
    config = load_config()
    agent = JarvisAgent(api_key=config.gemini_api_key, model=config.gemini_model)
    handlers = JarvisTelegramHandlers(agent=agent, allowed_user_ids=config.allowed_user_ids)

    app = Application.builder().token(config.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("reset", handlers.reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handlers.handle_voice))
    return app


def main() -> None:
    """Botu baslatir."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    app = build_application()
    logging.getLogger(__name__).info("7/24 Jarvis Telegram Botu baslatiliyor...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

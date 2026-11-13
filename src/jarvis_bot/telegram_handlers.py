"""Telegram mesaj, sesli mesaj ve komut isleyicileri."""

from __future__ import annotations

import logging
from typing import Protocol

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from jarvis_bot.tts import text_to_speech

logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE_LENGTH = 4096
UNAUTHORIZED_MESSAGE = "Erisim reddedildi. Bu bot yalnizca yetkili kullanicilara aciktir."


class AgentBackend(Protocol):
    """Test edilebilirlik icin Jarvis ajan arayuzu."""

    def reset_chat(self, chat_id: int) -> None: ...

    async def generate_text_reply(self, chat_id: int, user_text: str) -> str: ...

    async def generate_audio_reply(
        self,
        chat_id: int,
        audio_bytes: bytes,
        mime_type: str = "audio/ogg",
    ) -> str: ...


def is_authorized_user(user_id: int | None, allowed_user_ids: frozenset[int]) -> bool:
    """Kullanicinin beyaz listede olup olmadigini kontrol eder."""
    if user_id is None:
        return False
    return user_id in allowed_user_ids


def chunk_message(text: str, max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    """Uzun yanitlari Telegram'in 4096 karakter sinirina uygun parcalara boler."""
    if not text:
        return []
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > max_length:
        split_at = remaining.rfind("\n", 0, max_length)
        if split_at <= 0:
            split_at = remaining.rfind(" ", 0, max_length)
        if split_at <= 0:
            split_at = max_length
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


class JarvisTelegramHandlers:
    """Telegram guncellemelerini Jarvis ajanina yonlendiren sinif."""

    def __init__(self, agent: AgentBackend, allowed_user_ids: frozenset[int]) -> None:
        self._agent = agent
        self._allowed_user_ids = allowed_user_ids

    async def _guard_authorized(self, update: Update) -> bool:
        user = update.effective_user
        user_id = user.id if user else None
        if is_authorized_user(user_id, self._allowed_user_ids):
            return True
        if update.effective_message:
            await update.effective_message.reply_text(UNAUTHORIZED_MESSAGE)
        return False

    async def _send_reply(self, update: Update, text: str) -> None:
        if not update.effective_message:
            return
        for part in chunk_message(text):
            await update.effective_message.reply_text(part)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/start komutu."""
        if not await self._guard_authorized(update):
            return
        await self._send_reply(
            update,
            "Emrinizdeyim efendim. 7/24 Jarvis modu aktif.\n"
            "Yazili veya sesli mesaj gonderebilirsiniz. Sohbeti sifirlamak icin /reset yazin.",
        )

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/reset komutu."""
        if not await self._guard_authorized(update):
            return
        if update.effective_chat:
            self._agent.reset_chat(update.effective_chat.id)
        await self._send_reply(update, "Sohbet hafizasi sifirlandi efendim. Yeni konuya hazirim.")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gelen metin mesajlarini isler."""
        if not await self._guard_authorized(update):
            return
        if not update.effective_message or not update.effective_chat:
            return

        text = update.effective_message.text or ""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        try:
            reply = await self._agent.generate_text_reply(update.effective_chat.id, text)
        except Exception:
            logger.exception("Metin yaniti uretilirken hata olustu")
            reply = "Bir teknik aksaklik olustu efendim, lutfen biraz sonra tekrar deneyin."
        await self._send_reply(update, reply)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Gelen sesli mesajlari (OGG/audio) isler."""
        if not await self._guard_authorized(update):
            return
        if not update.effective_message or not update.effective_chat:
            return

        media = update.effective_message.voice or update.effective_message.audio
        if not media:
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        try:
            tg_file = await context.bot.get_file(media.file_id)
            raw_bytes = bytes(await tg_file.download_as_bytearray())
            mime_type = getattr(media, "mime_type", None) or "audio/ogg"
            reply = await self._agent.generate_audio_reply(
                update.effective_chat.id,
                raw_bytes,
                mime_type=mime_type,
            )
        except Exception:
            logger.exception("Sesli mesaj islenirken hata olustu")
            reply = "Sesli mesaji islerken bir sorun olustu efendim, lutfen tekrar deneyin."
        await self._send_reply(update, reply)

        # Sesli mesaja karsilik sesli yanit gonder (TTS)
        voice_bytes = await text_to_speech(reply, lang="tr")
        if voice_bytes and update.effective_message and hasattr(update.effective_message, "reply_voice"):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)
            await update.effective_message.reply_voice(voice=voice_bytes)

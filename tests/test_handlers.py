from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from jarvis_bot.telegram_handlers import (
    UNAUTHORIZED_MESSAGE,
    JarvisTelegramHandlers,
    chunk_message,
    is_authorized_user,
)


class FakeAgent:
    def __init__(self) -> None:
        self.reset_calls: list[int] = []
        self.text_calls: list[tuple[int, str]] = []
        self.audio_calls: list[tuple[int, bytes, str]] = []

    def reset_chat(self, chat_id: int) -> None:
        self.reset_calls.append(chat_id)

    async def generate_text_reply(self, chat_id: int, user_text: str) -> str:
        self.text_calls.append((chat_id, user_text))
        return f"Yanit: {user_text}"

    async def generate_audio_reply(
        self,
        chat_id: int,
        audio_bytes: bytes,
        mime_type: str = "audio/ogg",
    ) -> str:
        self.audio_calls.append((chat_id, audio_bytes, mime_type))
        return "Ses yaniti efendim."


def _make_update(user_id: int, chat_id: int = 999, text: str = "Merhaba", voice=None):
    message = SimpleNamespace(
        text=text,
        voice=voice,
        audio=None,
        reply_text=AsyncMock(),
        reply_voice=AsyncMock(),
    )
    return SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        effective_chat=SimpleNamespace(id=chat_id),
        effective_message=message,
    )


def test_is_authorized_user():
    allowed = frozenset({111, 222})
    assert is_authorized_user(111, allowed) is True
    assert is_authorized_user(333, allowed) is False
    assert is_authorized_user(None, allowed) is False


def test_chunk_message_splits_long_text():
    text = ("A" * 3000) + "\n" + ("B" * 3000)
    parts = chunk_message(text, max_length=4096)
    assert len(parts) == 2
    assert all(len(p) <= 4096 for p in parts)


@pytest.mark.asyncio
async def test_unauthorized_user_is_blocked():
    agent = FakeAgent()
    handlers = JarvisTelegramHandlers(agent=agent, allowed_user_ids=frozenset({111}))
    update = _make_update(user_id=999, text="Gizli bilgi")
    context = SimpleNamespace(bot=SimpleNamespace(send_chat_action=AsyncMock()))

    await handlers.handle_text(update, context)

    assert agent.text_calls == []
    update.effective_message.reply_text.assert_awaited_once_with(UNAUTHORIZED_MESSAGE)


@pytest.mark.asyncio
async def test_authorized_text_calls_agent():
    agent = FakeAgent()
    handlers = JarvisTelegramHandlers(agent=agent, allowed_user_ids=frozenset({111}))
    update = _make_update(user_id=111, chat_id=555, text="Durum nedir?")
    context = SimpleNamespace(bot=SimpleNamespace(send_chat_action=AsyncMock()))

    await handlers.handle_text(update, context)

    assert agent.text_calls == [(555, "Durum nedir?")]
    update.effective_message.reply_text.assert_awaited_once_with("Yanit: Durum nedir?")


@pytest.mark.asyncio
async def test_authorized_voice_downloads_and_calls_agent():
    agent = FakeAgent()
    handlers = JarvisTelegramHandlers(agent=agent, allowed_user_ids=frozenset({111}))
    voice = SimpleNamespace(file_id="file-1", mime_type="audio/ogg")
    update = _make_update(user_id=111, chat_id=555, voice=voice)

    tg_file = SimpleNamespace(download_as_bytearray=AsyncMock(return_value=bytearray(b"audio-data")))
    bot = SimpleNamespace(
        send_chat_action=AsyncMock(),
        get_file=AsyncMock(return_value=tg_file),
    )
    context = SimpleNamespace(bot=bot)

    await handlers.handle_voice(update, context)

    assert agent.audio_calls == [(555, b"audio-data", "audio/ogg")]
    update.effective_message.reply_text.assert_awaited_once_with("Ses yaniti efendim.")

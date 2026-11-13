from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from jarvis_bot.jarvis_agent import EMPTY_RESPONSE_FALLBACK, JarvisAgent


class FakeChat:
    def __init__(self, reply_text: str) -> None:
        self.reply_text = reply_text
        self.calls: list[object] = []

    def send_message(self, payload: object) -> SimpleNamespace:
        self.calls.append(payload)
        return SimpleNamespace(text=self.reply_text)


@pytest.mark.asyncio
async def test_generate_text_reply_uses_chat_and_returns_response():
    fake_chat = FakeChat("Emrinizdeyim efendim.")
    fake_client = MagicMock()
    fake_client.chats.create.return_value = fake_chat

    agent = JarvisAgent(api_key="test-key", client=fake_client)
    reply = await agent.generate_text_reply(chat_id=100, user_text="Merhaba")

    assert reply == "Emrinizdeyim efendim."
    assert fake_chat.calls == ["Merhaba"]
    fake_client.chats.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_text_reply_empty_input_returns_fallback():
    fake_client = MagicMock()
    agent = JarvisAgent(api_key="test-key", client=fake_client)

    reply = await agent.generate_text_reply(chat_id=100, user_text="   ")

    assert reply == EMPTY_RESPONSE_FALLBACK
    fake_client.chats.create.assert_not_called()


@pytest.mark.asyncio
async def test_reset_chat_clears_existing_session():
    fake_client = MagicMock()
    fake_client.chats.create.side_effect = [FakeChat("Birinci"), FakeChat("Ikinci")]

    agent = JarvisAgent(api_key="test-key", client=fake_client)
    assert await agent.generate_text_reply(chat_id=100, user_text="Selam") == "Birinci"
    agent.reset_chat(100)
    assert await agent.generate_text_reply(chat_id=100, user_text="Selam") == "Ikinci"
    assert fake_client.chats.create.call_count == 2


@pytest.mark.asyncio
async def test_generate_audio_reply_sends_audio_part():
    fake_chat = FakeChat("Sesinizi aldim efendim.")
    fake_client = MagicMock()
    fake_client.chats.create.return_value = fake_chat

    agent = JarvisAgent(api_key="test-key", client=fake_client)
    reply = await agent.generate_audio_reply(chat_id=100, audio_bytes=b"OggS-fake", mime_type="audio/ogg")

    assert reply == "Sesinizi aldim efendim."
    assert len(fake_chat.calls) == 1

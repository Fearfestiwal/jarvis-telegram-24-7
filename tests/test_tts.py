import pytest

from jarvis_bot.tts import text_to_speech, text_to_speech_sync


def test_text_to_speech_sync_empty_returns_empty():
    assert text_to_speech_sync("") == b""
    assert text_to_speech_sync("   ") == b""


def test_text_to_speech_sync_generates_mp3():
    data = text_to_speech_sync("Merhaba efendim", lang="tr")
    assert isinstance(data, bytes)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_text_to_speech_async_wrapper():
    data = await text_to_speech("Test", lang="tr")
    assert isinstance(data, bytes)
    assert len(data) > 0

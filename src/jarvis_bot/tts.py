"""Turkce metinleri ses dosyalarina (MP3/OGG) donusturur."""

from __future__ import annotations

import asyncio
import io
import logging

from gtts import gTTS

logger = logging.getLogger(__name__)


def text_to_speech_sync(text: str, lang: str = "tr") -> bytes:
    """Senkron gTTS cagrisi ile MP3 ses bayt dizisi olusturur."""
    cleaned = (text or "").strip()
    if not cleaned:
        return b""
    # gTTS cok uzun metinlerde yavaslayabilir; ilk 500 karaktere odaklan
    truncated = cleaned[:500]
    buffer = io.BytesIO()
    tts = gTTS(text=truncated, lang=lang)
    tts.write_to_fp(buffer)
    return buffer.getvalue()


async def text_to_speech(text: str, lang: str = "tr") -> bytes:
    """gTTS ses olusturma islemini olay dongusunu tikamadan asenkron calistirir."""
    try:
        return await asyncio.to_thread(text_to_speech_sync, text, lang)
    except Exception:
        logger.exception("Ses uretimi sirasinda hata olustu")
        return b""

"""Jarvis kisiligi ve Gemini API sohbet yoneticisi."""

from __future__ import annotations

import asyncio
from typing import Any

from google import genai
from google.genai import types

JARVIS_SYSTEM_PROMPT = """Sen kullanicinin kisisel Turkce Jarvis asistanisin.

Kimlik ve Uslup:
- Kullaniciya kisa, saygili ve samimi bicimde "efendim" diye hitap et.
- Gereksiz uzun girisler yapma; dogrudan sonuca, cozume ve somut aksiyona odaklan.
- %100 Turkce yanit ver; Turkce karakterleri (c, g, i, o, s, u, C, G, I, O, S, U) dogru kullan.
- Hisse/yatirim sorularinda yalnizca faizsiz/helal (Katilim Endeksi / AAOIFI uyumlu, kaldiracsiz spot) cercevesinde degerlendir.
- Bilmedigin veya emin olmadigin guncel konularda Google Search aracini kullan; uydurma bilgi verme.
"""

EMPTY_RESPONSE_FALLBACK = "Anlayamadim efendim, lutfen tekrar iletir misiniz?"


class JarvisAgent:
    """Her sohbet icin baglam koruyan 7/24 Jarvis ajan istemcisi."""

    def __init__(self, api_key: str, model: str = "gemini-3.5-flash-lite", client: Any | None = None) -> None:
        self._model = model
        self._client = client if client is not None else genai.Client(api_key=api_key)
        self._chats: dict[int, Any] = {}
        self._locks: dict[int, asyncio.Lock] = {}

    def _get_lock(self, chat_id: int) -> asyncio.Lock:
        lock = self._locks.get(chat_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[chat_id] = lock
        return lock

    def _get_or_create_chat(self, chat_id: int) -> Any:
        chat = self._chats.get(chat_id)
        if chat is None:
            config = types.GenerateContentConfig(
                system_instruction=JARVIS_SYSTEM_PROMPT,
            )
            chat = self._client.chats.create(model=self._model, config=config)
            self._chats[chat_id] = chat
        return chat

    def reset_chat(self, chat_id: int) -> None:
        """Belirtilen sohbetin gecmisini sifirlar."""
        self._chats.pop(chat_id, None)

    async def generate_text_reply(self, chat_id: int, user_text: str) -> str:
        """Metin mesajina baglamli Jarvis yaniti uretir."""
        cleaned = user_text.strip()
        if not cleaned:
            return EMPTY_RESPONSE_FALLBACK

        async with self._get_lock(chat_id):
            chat = self._get_or_create_chat(chat_id)
            response = await asyncio.to_thread(chat.send_message, cleaned)
            return (response.text or "").strip() or EMPTY_RESPONSE_FALLBACK

    async def generate_audio_reply(
        self,
        chat_id: int,
        audio_bytes: bytes,
        mime_type: str = "audio/ogg",
    ) -> str:
        """Telegram sesli mesajini dogrudan dinleyip yanit uretir."""
        if not audio_bytes:
            return EMPTY_RESPONSE_FALLBACK

        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        prompt = "Kullanicinin gonderdigi bu sesli mesaji dinle ve Jarvis olarak dogrudan yanitla."

        async with self._get_lock(chat_id):
            chat = self._get_or_create_chat(chat_id)
            response = await asyncio.to_thread(chat.send_message, [prompt, audio_part])
            return (response.text or "").strip() or EMPTY_RESPONSE_FALLBACK

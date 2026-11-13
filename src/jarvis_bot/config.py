"""Ortam degiskenleri ve yapilandirma dogrulamasi."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"


@dataclass(frozen=True)
class BotConfig:
    """Botun calismasi icin dogrulanmis, degistirilemez yapilandirma."""

    telegram_bot_token: str
    gemini_api_key: str
    allowed_user_ids: frozenset[int]
    gemini_model: str = DEFAULT_GEMINI_MODEL


def parse_allowed_user_ids(raw_ids: str) -> frozenset[int]:
    """Virgulle ayrilmis Telegram kullanici ID dizisini dogrular ve donusturur."""
    if not raw_ids or not raw_ids.strip():
        raise ValueError(
            "ALLOWED_TELEGRAM_USER_IDS bos olamaz. Guvenlik geregi en az bir Telegram ID girilmelidir."
        )

    parsed: list[int] = []
    for part in raw_ids.split(","):
        cleaned = part.strip()
        if not cleaned:
            continue
        try:
            user_id = int(cleaned)
        except ValueError as exc:
            raise ValueError(f"Gecersiz Telegram kullanici ID: {cleaned!r}") from exc
        if user_id <= 0:
            raise ValueError(f"Telegram kullanici ID pozitif tam sayi olmalidir: {user_id}")
        parsed.append(user_id)

    if not parsed:
        raise ValueError("ALLOWED_TELEGRAM_USER_IDS en az bir gecerli ID icermelidir.")

    return frozenset(parsed)


def load_config(env: dict[str, str] | None = None) -> BotConfig:
    """Ortam degiskenlerinden yapilandirmayi yukler ve sinir dogrulamasi yapar."""
    source = env if env is not None else os.environ

    telegram_token = source.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN eksik.")

    gemini_api_key = source.get("GEMINI_API_KEY", "").strip()
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY eksik.")

    allowed_ids = parse_allowed_user_ids(source.get("ALLOWED_TELEGRAM_USER_IDS", ""))
    model = source.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL

    return BotConfig(
        telegram_bot_token=telegram_token,
        gemini_api_key=gemini_api_key,
        allowed_user_ids=allowed_ids,
        gemini_model=model,
    )

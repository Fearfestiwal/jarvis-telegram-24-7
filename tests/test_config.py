import pytest

from jarvis_bot.config import DEFAULT_GEMINI_MODEL, load_config, parse_allowed_user_ids


def test_parse_allowed_user_ids_valid():
    result = parse_allowed_user_ids("123456, 789012 , ")
    assert result == frozenset({123456, 789012})


@pytest.mark.parametrize("raw", ["", "   ", ",", "abc", "123,-5", "0"])
def test_parse_allowed_user_ids_invalid(raw: str):
    with pytest.raises(ValueError):
        parse_allowed_user_ids(raw)


def test_load_config_valid():
    cfg = load_config(
        {
            "TELEGRAM_BOT_TOKEN": "123:ABC",
            "GEMINI_API_KEY": "AIza-test",
            "ALLOWED_TELEGRAM_USER_IDS": "42",
        }
    )
    assert cfg.telegram_bot_token == "123:ABC"
    assert cfg.gemini_api_key == "AIza-test"
    assert cfg.allowed_user_ids == frozenset({42})
    assert cfg.gemini_model == DEFAULT_GEMINI_MODEL


def test_load_config_missing_token_raises():
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        load_config(
            {
                "GEMINI_API_KEY": "AIza-test",
                "ALLOWED_TELEGRAM_USER_IDS": "42",
            }
        )

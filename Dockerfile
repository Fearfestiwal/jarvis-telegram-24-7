FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./
COPY src ./src

ENV PYTHONPATH=/app/src

RUN uv sync --no-dev

CMD ["uv", "run", "python", "-m", "jarvis_bot.main"]

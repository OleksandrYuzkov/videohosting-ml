FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Копируем метаданные проекта и локфайлы
COPY pyproject.toml uv.lock README.md ./

# Устанавливаем зависимости (без сборки самого проекта)
RUN uv sync --frozen --no-dev --no-install-project

# Копируем исходный код
COPY src/ ./src/

# Устанавливаем сам проект
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
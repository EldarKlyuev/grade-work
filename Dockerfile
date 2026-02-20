FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry lock && poetry install

COPY src ./src
COPY config ./config
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

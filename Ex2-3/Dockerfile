#checkov:skip=CKV_DOCKER_2
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --no-dev


FROM python:3.12-slim

RUN useradd -r -u 1000 appuser

WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY app/ ./app/
COPY models/ ./models/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

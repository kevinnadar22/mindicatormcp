# Build deps into a venv, then copy only the runtime bits.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /build
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project --no-editable

COPY app ./app
RUN uv sync --frozen --no-dev --no-editable


FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

RUN useradd --create-home --uid 1000 appuser

COPY --from=builder /build/.venv /app/.venv
COPY mumbai_mindicator.sqlite ./mumbai_mindicator.sqlite

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    DB_PATH=/app/mumbai_mindicator.sqlite

USER appuser
EXPOSE 8000

CMD ["mindicator-mcp"]

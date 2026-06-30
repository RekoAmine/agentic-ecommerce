FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /usr/local/bin/uv
COPY pyproject.toml README.md ./
COPY backend ./backend
COPY mcp-server ./mcp-server

RUN uv sync --frozen --no-dev || uv sync --no-dev

CMD ["python", "-c", "import fba_advisor, fba_mcp_server; print('agentic-ecommerce base image ready')"]

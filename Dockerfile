FROM python:3.12-slim

ARG PORT=4001
ENV PORT=${PORT}

COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY main.py ./
COPY app ./app

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=9 \
  CMD python -c "import socket, os; socket.create_connection(('localhost', int(os.environ['PORT'])), 2)"

EXPOSE ${PORT}

CMD ["sh", "-c", "/app/.venv/bin/uvicorn app.app:app --host 0.0.0.0 --port $PORT"]

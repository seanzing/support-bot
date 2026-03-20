FROM python:3.11-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Railway builds from repo root, so copy backend/ contents into /app
COPY backend/ .

RUN uv sync --frozen --no-dev

# Railway uses dynamic PORT, Docker Compose uses 8001
ENV PORT=8001
EXPOSE 8001

# Use shell form to expand $PORT variable
CMD uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
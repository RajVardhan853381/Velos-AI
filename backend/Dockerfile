# Multi-stage Dockerfile for minimal production size
FROM python:3.10-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir poetry==1.8.2

COPY backend/pyproject.toml backend/poetry.lock* ./backend/
WORKDIR /app/backend
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Runtime stage
FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY backend /app/backend
# Copy legacy components needed for backward compatibility
COPY agents /app/agents
COPY utils /app/utils
COPY zynd /app/zynd
COPY server.py /app/server.py

ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

EXPOSE 8000

# Run via Uvicorn explicitly.
CMD ["uvicorn", "backend.app.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]

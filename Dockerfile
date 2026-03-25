FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt

RUN uv pip install --system -r requirements.txt

COPY . .

RUN echo "✅ Dependencies installed. Application is ready to run."

EXPOSE 8000

WORKDIR /app

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

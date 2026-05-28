FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling certain packages or postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Set python path to allow imports from packages/ and apps/
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "apps.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

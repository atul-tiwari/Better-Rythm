# Use Python 3.11 slim image as base
FROM python:3.13.12

WORKDIR /app

# Install system dependencies (ffmpeg for audio streaming)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run as non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Health check (Discord gateway reachable)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('https://discord.com/api/v10/gateway', timeout=5)" || exit 1

CMD ["python", "main.py"]

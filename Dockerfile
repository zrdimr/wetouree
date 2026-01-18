# Use Python 3.10 slim as base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies (including supervisor to run multiple processes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for SQLite data
RUN mkdir -p /app/data && chown -R 1000:1000 /app/data
ENV DATABASE_PATH=/app/data/tourism.db

# Configure Supervisor to run both FastAPI and Flask
RUN printf "[supervisord]\nnodaemon=true\n\n[program:backend]\ncommand=uvicorn backend.main:app --host 0.0.0.0 --port 8000\nautostart=true\nautorestart=true\n\n[program:frontend]\ncommand=python frontend/app.py\nautostart=true\nautorestart=true\n" > /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 8000 6004

# Run supervisord
CMD ["/usr/bin/supervisord"]

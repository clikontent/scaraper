# Use Python 3.12 slim image (pre-built lxml wheels available)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for lxml / aiohttp
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libxml2-dev \
        libxslt1-dev \
        python3-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel before installing packages
RUN pip install --upgrade pip setuptools wheel

# Copy project files
COPY . .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Environment variables will be provided via Render dashboard
# SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

# Default command to run all scrapers
CMD ["python", "cron.py"]

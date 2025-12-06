# Use Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

# System dependencies for lxml, aiohttp, and Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libxml2-dev libxslt1-dev python3-dev build-essential \
        curl gnupg ca-certificates wget unzip xvfb libnss3 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpangocairo-1.0-0 \
        libpango-1.0-0 libgtk-3-0 libdrm2 libxshmfence1 libasound2 libexpat1 libfontconfig1 \
        libglib2.0-0 libx11-xcb1 libxcb1 libx11-6 libxext6 libxfixes3 libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium

# Run the cron scraper
CMD ["python", "cron.py"]

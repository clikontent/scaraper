# Use official Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Environment variables will be passed via Railway, Docker, or local .env
# Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set

# Run scraper cron on container start
CMD ["python", "cron.py"]

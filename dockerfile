# ---------------------------------------------
# Base: Playwright image with all browser deps
# ---------------------------------------------
FROM mcr.microsoft.com/playwright:focal

# Install Node.js (LTS)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app

# ---------------------------------------------
# Install Python dependencies
# ---------------------------------------------
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------
# Install Node dependencies
# ---------------------------------------------
COPY package.json package-lock.json* ./
RUN npm install || true

# ---------------------------------------------
# Copy project files
# ---------------------------------------------
COPY . .

# ---------------------------------------------
# Install Playwright browsers inside container
# ---------------------------------------------
RUN npx playwright install --with-deps

# ---------------------------------------------
# Default command (change if needed)
# ---------------------------------------------
CMD ["python", "main.py"]

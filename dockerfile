# -------------------------------
# Base image with Python + Node
# -------------------------------
FROM mcr.microsoft.com/playwright:focal

# Install Node.js (latest LTS)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    node -v && npm -v

# Set working directory
WORKDIR /app

# -------------------------------
# Install Python dependencies
# -------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Install Node dependencies
# -------------------------------
COPY package.json package-lock.json* ./
RUN npm install || true

# -------------------------------
# Copy the full project
# -------------------------------
COPY . .

# -------------------------------
# Install Playwright Browsers
# -------------------------------
RUN npx playwright install --with-deps

# -------------------------------
# Default command (You can change this)
# Run BOTH scrapers sequentially if needed
# -------------------------------
CMD ["bash", "-c", "python main.py && node scrapers/playwright_scraper.js"]

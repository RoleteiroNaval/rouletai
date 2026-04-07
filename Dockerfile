FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser dependencies (Chromium)
RUN playwright install chromium

# Copy the rest of the application
COPY . .

# Create persistent directories
RUN mkdir -p data logs playwright_profile

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_HEADLESS=true

# Entry point
CMD ["python", "main.py"]

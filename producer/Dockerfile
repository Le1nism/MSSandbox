FROM python:3.11-slim

WORKDIR /app

# Copy requirements (will be created later)
COPY requirements.txt .

# Install dependencies (only if requirements.txt is not empty)
RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application code (will be created later)
COPY . .

# Expose port
EXPOSE 8001

# Placeholder command - will be replaced with actual application logic
CMD ["python", "-c", "import time; print('Producer service starting...'); time.sleep(3600)"]

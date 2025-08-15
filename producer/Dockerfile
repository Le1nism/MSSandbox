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

# Run with unbuffered output to ensure logs are visible
CMD ["python", "-u", "app.py"]

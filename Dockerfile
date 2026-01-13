FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .
COPY web_main.py .
COPY web_app.py .
COPY config/ ./config/
COPY web/ ./web/

# Create directory for logs
RUN mkdir -p /app/logs

# Expose port for web interface (if running in web mode)
EXPOSE 5000

# Default to running main scrobbler, but can override with web_main.py
CMD ["python", "main.py"]

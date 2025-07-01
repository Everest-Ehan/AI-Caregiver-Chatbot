# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        python3.11-venv \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.11 -m venv $VIRTUAL_ENV

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app \
    && chown -R appuser:appuser $VIRTUAL_ENV
USER appuser

# Activate virtual environment and verify Python version
RUN python --version && which python

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with virtual environment activated
CMD ["./start.sh"] 
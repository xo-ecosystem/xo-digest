# 🔐 Vault Keeper: Dockerfile for XO Agent webhook system
# Preserving digital essence with containerized deployment

FROM python:3.10-slim

# 🔐 Vault Keeper: Set working directory for digital essence operations
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# 🔐 Vault Keeper: Create necessary directories for digital essence preservation
RUN mkdir -p logs public vault shared

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# 🔐 Vault Keeper: Expose port for webhook operations
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/agent/health || exit 1

# 🔐 Vault Keeper: Start the webhook system with precision
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
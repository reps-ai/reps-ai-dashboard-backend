FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    redis-server \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir retell-sdk \
    && pip install --no-cache-dir pydantic-settings==2.2.1

# Copy the entire project
COPY . .

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Copy the entrypoint script and make it executable
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose the port FastAPI will run on
EXPOSE 8000 6379

# Use the entrypoint script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"] 
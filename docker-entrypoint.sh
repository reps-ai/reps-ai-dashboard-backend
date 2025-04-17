#!/usr/bin/env bash
set -e

# Function to log messages with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a process is running
check_process() {
    local pid=$1
    local name=$2
    if ! kill -0 "$pid" 2>/dev/null; then
        log "[ERROR] $name process (PID: $pid) is not running"
        return 1
    fi
    return 0
}

# Function to check Redis connection
check_redis() {
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if redis-cli ping >/dev/null 2>&1; then
            log "[INFO] Redis is accepting connections"
            return 0
        fi
        log "[WARN] Redis connection attempt $attempt/$max_attempts failed, retrying..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log "[ERROR] Redis failed to accept connections after $max_attempts attempts"
    return 1
}

# Start Redis
log "[INFO] Starting Redis server..."
redis-server > /tmp/redis.log 2>&1 &
REDIS_PID=$!

# Wait for Redis to be ready
sleep 2
if ! check_process "$REDIS_PID" "Redis"; then
    log "[ERROR] Redis failed to start. Log output:"
    cat /tmp/redis.log
    exit 1
fi

# Check Redis connectivity
if ! check_redis; then
    log "[ERROR] Redis is not responding. Log output:"
    cat /tmp/redis.log
    exit 1
fi

log "[INFO] Redis started successfully with PID $REDIS_PID"

# Start FastAPI (uvicorn)
log "[INFO] Starting FastAPI application with uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info > /tmp/uvicorn.log 2>&1 &
UVICORN_PID=$!

# Wait for uvicorn to start
sleep 3
if ! check_process "$UVICORN_PID" "Uvicorn"; then
    log "[ERROR] Uvicorn failed to start. Log output:"
    cat /tmp/uvicorn.log
    exit 1
fi

# Check if FastAPI is responding
log "[INFO] Checking FastAPI health..."
for i in {1..5}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        log "[INFO] FastAPI is responding to health checks"
        break
    fi
    if [ $i -eq 5 ]; then
        log "[ERROR] FastAPI failed to respond to health checks. Uvicorn log output:"
        cat /tmp/uvicorn.log
        exit 1
    fi
    log "[WARN] Waiting for FastAPI to become ready... (attempt $i/5)"
    sleep 2
done

log "[INFO] Application startup completed successfully"
log "[INFO] FastAPI is running on http://0.0.0.0:8000"
log "[INFO] Redis is running on port 6379"

# Monitor both processes and exit if either fails
log "[INFO] Starting process monitor..."
while true; do
    if ! check_process "$REDIS_PID" "Redis" || ! check_process "$UVICORN_PID" "Uvicorn"; then
        log "[ERROR] One or more required processes have died"
        exit 1
    fi
    sleep 10
done 
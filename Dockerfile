# FitAgent uAgent Dockerfile for Akash Network Deployment
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for user data persistence
RUN mkdir -p /app/data

# Set environment variables for the agent
ENV USER_MEMORY_FILE=/app/data/user_memory.json
ENV AGENT_PORT=8081

# Expose both agent and HTTP wrapper ports
EXPOSE 8081 8082

# Health check - check HTTP wrapper instead
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8082/health || exit 1

# Install Flask and CORS for HTTP wrapper
RUN pip install flask flask-cors

# Copy HTTP wrapper
COPY http_wrapper.py .

# Create startup script with better logging
RUN echo '#!/bin/bash\necho "Starting FitAgent services..."\necho "Starting uAgent on port 8081..."\npython fitagent_coach.py &\necho "Starting HTTP wrapper on port 8082..."\npython http_wrapper.py &\necho "Both services started, waiting..."\nwait' > start.sh && chmod +x start.sh

# Run both the uAgent and HTTP wrapper
CMD ["./start.sh"]

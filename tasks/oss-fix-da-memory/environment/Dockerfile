# DeepAgents environment for oss-fix-da-memory task
FROM python:3.13-slim

# Install system dependencies including Node.js for Claude Code
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create non-root user for security
RUN useradd -m -s /bin/bash benchuser
USER benchuser

# Set working directory
WORKDIR /workspace

# Default command
CMD ["python"]

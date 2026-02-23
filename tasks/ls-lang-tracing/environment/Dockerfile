# Polyglot Python + TypeScript environment for LangSmith skill benchmarks
FROM python:3.13-slim

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    uuid-runtime \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI and tsx globally
RUN npm install -g @anthropic-ai/claude-code tsx

# Create workspace and install Python deps
WORKDIR /workspace
COPY backend/requirements.txt /workspace/backend/requirements.txt
RUN pip install --no-cache-dir -r /workspace/backend/requirements.txt

# Install Node.js deps in frontend
COPY frontend/package.json frontend/package-lock.json* /workspace/frontend/
RUN cd /workspace/frontend && npm install && npm cache clean --force

# Copy source files
COPY backend/ /workspace/backend/
COPY frontend/ /workspace/frontend/

# Create non-root user for security
RUN useradd -m -s /bin/bash benchuser && chown -R benchuser:benchuser /workspace
USER benchuser

WORKDIR /workspace

CMD ["python"]

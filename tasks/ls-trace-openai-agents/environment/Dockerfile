FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    uuid-runtime \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ARG CLAUDE_CODE_VERSION=latest
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

COPY agent.py /workspace/agent.py

RUN useradd -m -s /bin/bash benchuser && chown -R benchuser:benchuser /workspace
USER benchuser

WORKDIR /workspace

CMD ["python"]

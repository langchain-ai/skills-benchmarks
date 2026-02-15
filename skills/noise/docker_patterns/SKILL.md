---
name: docker-patterns
description: Best practices for Docker containerization and multi-stage builds
---

# Docker Containerization Patterns

Build efficient, secure Docker images using modern patterns.

## Multi-Stage Builds

Always use multi-stage builds to minimize image size:

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
USER node
CMD ["node", "server.js"]
```

## Security Best Practices

1. Never run as root - use `USER` directive
2. Use specific version tags, not `latest`
3. Scan images with `docker scout` or Trivy
4. Use `.dockerignore` to exclude sensitive files

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

## Compose Patterns

```yaml
services:
  app:
    build:
      context: .
      target: production
    environment:
      - NODE_ENV=production
    deploy:
      resources:
        limits:
          memory: 512M
```

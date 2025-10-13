# ===== STAGE 1: Builder ===== #
FROM python:3.13-alpine@sha256:3a77fbbb5bc88c0f63cc2692a13b011547f25ee93536e991544c452801856226 AS builder

# Prevent Python from writing .pyc files and buffer output.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build argument for environment-specific dependencies.
ARG ENVIRONMENT=local

# Install build dependencies for python packages with security updates.
RUN set -eux && \
    apk update && \
    apk add --no-cache \
        build-base \
        postgresql-dev && \
    apk upgrade --no-cache -U && \
    rm -rf /var/cache/apk/*

WORKDIR /app

# Copy only requirements first (for better layer caching).
COPY requirements/ ./requirements/

# Create venv and install base + env-specific deps.
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip wheel setuptools && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements/base.txt && \
    if [ "$ENVIRONMENT" = "local" ] && [ -f "requirements/local.txt" ]; then \
        /opt/venv/bin/pip install --no-cache-dir -r requirements/local.txt; \
    elif [ "$ENVIRONMENT" = "production" ] && [ -f "requirements/production.txt" ]; then \
        /opt/venv/bin/pip install --no-cache-dir -r requirements/production.txt; \
    fi

# ===== STAGE 2: Runtime ===== #
FROM python:3.13-alpine@sha256:3a77fbbb5bc88c0f63cc2692a13b011547f25ee93536e991544c452801856226

# Install only runtime dependencies with security updates.
RUN set -eux && \
    apk update && \
    apk add --no-cache libpq && \
    apk upgrade --no-cache -U && \
    rm -rf /var/cache/apk/*

# Create non-root user with explicit UID/GID (security best practice).
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup -s /bin/sh -D

WORKDIR /app

# Copy virtual environment from builder.
COPY --from=builder /opt/venv /opt/venv

# Ensure appuser owns the app directory and venv.
RUN chown -R appuser:appgroup /app /opt/venv

# Activate venv by adding to PATH.
ENV PATH="/opt/venv/bin:$PATH"

# Switch to non-root user (principle of least privilege).
USER appuser

# Copy application code (as appuser to avoid root-owned files).
COPY --chown=appuser:appgroup ./app/ ./app/

# Copy entrypoint script and make it executable.
COPY --chown=appuser:appgroup ./scripts/docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh


ENTRYPOINT [ "/app/docker-entrypoint.sh" ]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
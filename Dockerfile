# ===== STAGE 1: Builder ===== #
FROM python:3.13-slim-bullseye AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Accept build argument for environment.
ARG ENVIRONMENT=local

WORKDIR /app

COPY requirements/ ./requirements/

# Create virtual environment and upgrade pip.
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip wheel setuptools && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements/base.txt

# Install environment-specific requirements
RUN if [ "$ENVIRONMENT" = "local" ] && [ -f "requirements/local.txt" ]; then \
    /opt/venv/bin/pip install --no-cache-dir -r requirements/local.txt; \
    elif [ "$ENVIRONMENT" = "production" ] && [ -f "requirements/production.txt" ]; then \
    /opt/venv/bin/pip install --no-cache-dir -r requirements/production.txt; \
    fi

# ===== STAGE 2: Runtime ===== #
FROM python:3.13-slim-bullseye

# Create non-root user and group with explicit UID/GID.
RUN groupadd --system --gid 1000 appgroup && \
    useradd --system --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser && \
    echo 'appuser ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

WORKDIR /app

# Set correct ownership for the app dir.
RUN chown appuser:appgroup /app

# Copy venv from builder.
COPY --from=builder /opt/venv /opt/venv

# Update ownership of venv.
RUN chown -R appuser:appgroup /opt/venv

# Add venv to PATH.
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=appuser:appgroup ./app/ ./app/

# Switch to non-root user.
USER appuser

RUN whoami && id

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
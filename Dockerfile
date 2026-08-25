# Conversion Architect API - Dockerfile for Railway
FROM python:3.13-slim

WORKDIR /app

# Install pipx and analytics-mcp
RUN apt-get update && apt-get install -y --no-install-recommends \
    pipx \
    && rm -rf /var/lib/apt/lists/*

# Install pipx-managed packages
ENV PIPX_HOME=/opt/pipx
ENV PIPX_BIN_DIR=/usr/local/bin
RUN pipx install analytics-mcp && pipx ensurepath

# Copy project files
COPY pyproject.toml ./
COPY conversion_architect/ ./conversion_architect/

# Install Python dependencies
RUN pip install --no-cache-dir pydantic pydantic-settings fastapi uvicorn mcp httpx

# Make sure analytics-mcp is in PATH
ENV PATH="/usr/local/bin:${PATH}"

EXPOSE 8000

# Use the entrypoint script for better error reporting
CMD ["python", "-m", "uvicorn", "conversion_architect.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
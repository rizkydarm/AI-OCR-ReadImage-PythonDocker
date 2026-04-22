# ===== Stage 1: Builder =====
FROM python:3.12-slim-bookworm AS builder

# Install system tools needed for uv installation
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Install uv (official install script)
ADD https://astral.sh/uv/0.6.17/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:$PATH"

# Optimizations for uv in Docker
ENV UV_COMPILE_BYTECODE=1        # Pre-compiles .pyc files, faster startup
ENV UV_LINK_MODE=copy            # Required when using Docker cache mounts

WORKDIR /app

# Copy dependency files first → maximizes Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
# --frozen ensures exact reproduction of uv.lock
RUN uv sync --frozen --no-install-project

# ===== Stage 2: Runtime =====
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Copy only the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY app ./app

# Add the virtual environment's bin to PATH
ENV PATH="/home/rizkyeky/python-projects/ai_read_image/.venv/bin:$PATH"

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
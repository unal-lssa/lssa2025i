FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.17 /uv /bin/

# Install dependencies
COPY pyproject.toml uv.lock .
RUN uv sync --locked

# Copy application code and config
COPY . .

# Run the application
CMD ["uv", "run", "python", "main.py"]

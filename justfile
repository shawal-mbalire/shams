set shell := ['bash', '-cu']

default:
    @just --list

serve:
    @uv run main.py

# Build docker image
docker-build:
    docker build -t shams-bot .

# Run docker container
docker-run:
    docker run --env-file .env shams-bot

# Build and run docker
docker: docker-build docker-run

# Clean generated files
clean:
    rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true


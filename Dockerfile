FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY main.py config.py handlers.py moderator.py utils.py ./
COPY config.json ./

# Install dependencies
RUN uv pip install --system -r pyproject.toml

# Run the bot
CMD ["python", "main.py"]

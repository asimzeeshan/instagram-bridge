FROM python:3.11-slim

# Debian security fixes released since the base image was built
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y upgrade && apt-get clean && rm -rf /var/lib/apt/lists/*

# uv for fast, reproducible Python installs (pinned; Dependabot bumps it)
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv

WORKDIR /app

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

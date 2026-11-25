FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Fixed UID so host directories can be given to it for bind mounts.
RUN useradd --system --uid 10001 --no-create-home app && \
    install -d -o app -g app -m 700 /var/log/anonymization-manager

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv pip install --system .

ENV ANONYMIZATION_MANAGER_LOG_FILE=/var/log/anonymization-manager/audit.log
VOLUME /var/log/anonymization-manager

USER app

# The slim image has no curl, so the check uses Python.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]
EXPOSE 8000

CMD ["uvicorn", "anonymization_manager.api:app", "--host", "0.0.0.0", "--port", "8000"]

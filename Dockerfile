FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless git && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

RUN uv pip install --system git+https://github.com/AI-team-UoA/RECITALS-anonymization-manager.git@main

EXPOSE 8000

CMD ["uvicorn", "anonymization_manager.api:app", "--host", "0.0.0.0", "--port", "8000"]

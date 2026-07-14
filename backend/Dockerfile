FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY backend ./backend

RUN python -m pip install . \
    && groupadd --system opslab \
    && useradd --system --gid opslab --create-home opslab \
    && mkdir -p /data \
    && chown opslab:opslab /data

USER opslab

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]

CMD ["uvicorn", "ops_lab.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

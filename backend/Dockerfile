# SpotHound backend: FastAPI + APScheduler + Playwright (Chromium) under xvfb,
# so headful browsing works on a headless server (needed for bot-protected sites).
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
ENV PATH="/app/.venv/bin:$PATH"

# Chromium + its OS deps, plus xvfb/xauth for a virtual display
RUN apt-get update \
    && apt-get install -y --no-install-recommends xvfb xauth \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

# entrypoint starts Xvfb (virtual display) then execs the server
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

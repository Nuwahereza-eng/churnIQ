# ChurnIQ: one container serving the FastAPI backend and the built React frontend.
#   docker build -t churniq .
#   docker run -p 8000:8000 churniq        -> http://localhost:8000

# ---- 1. Build the frontend ----
FROM node:22.15.0-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---- 2. Runtime: API + static files ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CHURNIQ_STATIC_DIR=/app/frontend/dist
WORKDIR /app

COPY requirements-api.txt ./
RUN pip install -r requirements-api.txt

COPY src/ src/
COPY backend/ backend/
COPY scripts/download_data.py scripts/
COPY models/ models/
COPY reports/evaluation_results.json reports/

# The dataset is not committed: fetch the public IBM file and check it is the
# exact version the model was trained and evaluated on.
RUN python scripts/download_data.py \
 && echo "16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91  data/raw/Telco-Customer-Churn.csv" | sha256sum -c -

COPY --from=frontend /app/frontend/dist frontend/dist

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
# Hosts such as Render set $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]

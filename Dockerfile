# ============================================================
#  BG Cleaner — Docker Image
#  Build:  docker build -t bg-cleaner .
#  Run:    docker run -p 5000:5000 bg-cleaner
# ============================================================

FROM python:3.12-slim AS base

# Prevent Python from buffering stdout/stderr (better logs)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# ---- System deps for onnxruntime + Pillow ----
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Python deps (cached layer) ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Pre-download the AI model (u2net: accurate subject detection) ----
RUN python -c "from rembg import new_session; new_session('u2net')"

# ---- Copy application code ----
COPY app/ app/
COPY app.py .

# ---- Create runtime directories ----
RUN mkdir -p uploads results

EXPOSE 5000

# Health check — confirm Flask is serving
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')"

CMD ["python", "app.py"]

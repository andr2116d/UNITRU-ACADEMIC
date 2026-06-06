# Backend: FastAPI + Playwright (Chromium) + Tesseract OCR.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Tesseract es OBLIGATORIO: el captcha se resuelve por OCR local
# (TesseractAdapter invoca el binario `tesseract` por stdin).
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Dependencias de Python primero (mejor cache de capas).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Chromium + sus dependencias del sistema, en la versión que coincide con el
# paquete playwright recién instalado.
RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8000

# Railway inyecta $PORT en runtime; localmente cae a 8000. Forma shell para que
# ${PORT} se expanda. --proxy-headers para que el WS funcione detrás del proxy TLS.
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips="*"

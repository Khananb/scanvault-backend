FROM python:3.10-slim

# Install Tesseract OCR (Eng + Hindi) and Poppler PDF utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-hin \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server_backend.py .

EXPOSE 5050

# Use Gunicorn WSGI server for multi-worker production stability
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "2", "--timeout", "120", "server_backend:app"]

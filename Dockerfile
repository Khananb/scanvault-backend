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

CMD ["python", "server_backend.py"]

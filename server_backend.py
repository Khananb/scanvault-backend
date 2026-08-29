#!/usr/bin/env python3
"""
ScanVault - Core OCR & PDF Cloud Backend
Supports Multi-Page PDF OCR, Image OCR, Multi-language (Eng + Hindi), Preprocessing & File Hosting
"""
import os
import io
import re
import sys
import uuid
import base64
import argparse
import tempfile
import urllib.request
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import pypdf
from pdf2image import convert_from_bytes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

STORAGE_DIR = os.path.expanduser('~/pdf_host')
os.makedirs(STORAGE_DIR, exist_ok=True)

def get_base_url():
    """Dynamically determine public base URL respecting proxies/Cloudflare tunnels."""
    forwarded_proto = request.headers.get('X-Forwarded-Proto', request.scheme)
    forwarded_host = request.headers.get('X-Forwarded-Host', request.host)
    return f"{forwarded_proto}://{forwarded_host}"

def preprocess_image(image):
    """Enhance image quality for higher OCR accuracy."""
    try:
        if image.mode in ('RGBA', 'P', 'LA'):
            image = image.convert('RGB')
        
        gray = image.convert('L')
        enhanced = ImageOps.autocontrast(gray, cutoff=2)
        contrast = ImageEnhance.Contrast(enhanced)
        final_img = contrast.enhance(1.4)
        sharpness = ImageEnhance.Sharpness(final_img)
        return sharpness.enhance(1.3)
    except Exception:
        return image.convert('RGB') if image.mode != 'RGB' else image

def ocr_single_image(image, lang='eng'):
    """Run optimized Tesseract OCR on a PIL Image."""
    prep_img = preprocess_image(image)
    config = r'--oem 1 --psm 3'
    try:
        text = pytesseract.image_to_string(prep_img, lang=lang, config=config)
    except Exception as e:
        print(f"Tesseract lang '{lang}' error: {e}. Falling back to 'eng'")
        try:
            text = pytesseract.image_to_string(prep_img, lang='eng', config=config)
        except Exception:
            text = ""
    return text.strip()

def process_pdf_ocr(pdf_bytes, lang='eng'):
    """
    Hybrid PDF extraction:
    1. First tries fast digital text extraction.
    2. If scanned / low text, renders high-DPI page images and runs OCR on each page.
    """
    page_texts = []
    
    # Step 1: Try digital text extraction via pypdf
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            txt = (page.extract_text() or '').strip()
            if txt:
                extracted_pages.append(f"--- Page {i + 1} ---\n{txt}")
            else:
                extracted_pages.append("")
        
        total_len = sum(len(p) for p in extracted_pages)
        if total_len >= (num_pages * 25) and num_pages > 0:
            return "\n\n".join([p for p in extracted_pages if p]), num_pages
    except Exception as e:
        print(f"Digital PDF extract fallback to OCR: {e}")

    # Step 2: Optical Character Recognition on PDF pages (via poppler pdftoppm)
    try:
        images = convert_from_bytes(pdf_bytes, dpi=220, thread_count=4)
        for i, img in enumerate(images):
            page_text = ocr_single_image(img, lang=lang)
            if page_text:
                page_texts.append(f"--- Page {i + 1} ---\n{page_text}")
            else:
                page_texts.append(f"--- Page {i + 1} ---\n(No readable text detected on this page)")
        
        return "\n\n".join(page_texts), len(images)
    except Exception as e:
        raise Exception(f"PDF OCR failed: {str(e)}")

@app.route('/')
@app.route('/api/health')
def health():
    return jsonify({
        "status": "online",
        "service": "ScanVault Core API",
        "engine": "Tesseract 5.5.3 Native (Eng + Hin) + Poppler PDF",
        "version": "2.1.0",
        "features": ["Image OCR", "Multi-Page PDF OCR", "Hindi + English", "Instant PDF Cloud Hosting"]
    })

# --------------------------------------------------------------------------
# 1. Unified OCR Endpoint (Images, Multi-Page PDFs, Base64 Screenshots, Remote URLs)
# --------------------------------------------------------------------------
@app.route('/api/ocr', methods=['POST'])
def process_ocr():
    try:
        json_data = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or json_data.get('lang') or 'eng'
        
        text = ""
        page_count = 1
        
        # A. Remote URL check (from Context Menu on web image)
        image_url = json_data.get('image_url') or json_data.get('url')
        if image_url:
            req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                file_bytes = resp.read()
                image = Image.open(io.BytesIO(file_bytes))
                text = ocr_single_image(image, lang=lang)
                page_count = 1
        else:
            # B. File Upload Check (Image or PDF)
            upload_file = request.files.get('image') or request.files.get('file')
            
            if upload_file:
                filename = upload_file.filename.lower()
                file_bytes = upload_file.read()
                
                if filename.endswith('.pdf') or upload_file.content_type == 'application/pdf':
                    text, page_count = process_pdf_ocr(file_bytes, lang=lang)
                else:
                    image = Image.open(io.BytesIO(file_bytes))
                    text = ocr_single_image(image, lang=lang)
                    page_count = 1

            else:
                # C. Base64 / JSON Payload Check
                raw_base64 = json_data.get('image') or json_data.get('image_base64') or json_data.get('dataUrl')
                
                if not raw_base64:
                    return jsonify({
                        "success": False,
                        "error": "No image or PDF file provided."
                    }), 400

                if ',' in raw_base64:
                    raw_base64 = raw_base64.split(',', 1)[1]
                
                raw_bytes = base64.b64decode(raw_base64)
                
                if raw_bytes.startswith(b'%PDF'):
                    text, page_count = process_pdf_ocr(raw_bytes, lang=lang)
                else:
                    image = Image.open(io.BytesIO(raw_bytes))
                    text = ocr_single_image(image, lang=lang)
                    page_count = 1

        clean_text = text.strip()
        words = len(clean_text.split()) if clean_text else 0
        chars = len(clean_text)

        return jsonify({
            "success": True,
            "text": clean_text,
            "pages": page_count,
            "word_count": words,
            "char_count": chars
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# --------------------------------------------------------------------------
# 2. PDF Hosting Endpoint (Upload File OR Remote PDF URL from Context Menu)
# --------------------------------------------------------------------------
@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    try:
        json_data = request.get_json(silent=True) or {}
        pdf_url = json_data.get('pdf_url') or json_data.get('url')
        
        filename = "document.pdf"
        file_bytes = None
        
        if pdf_url:
            req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                file_bytes = resp.read()
                filename = pdf_url.split('/')[-1].split('?')[0] or "remote_document.pdf"
        elif 'file' in request.files:
            file = request.files['file']
            filename = file.filename
            file_bytes = file.read()

        if not file_bytes:
            return jsonify({"success": False, "error": "No PDF file or URL provided"}), 400

        short_id = uuid.uuid4().hex[:8]
        save_filename = f"{short_id}.pdf"
        file_path = os.path.join(STORAGE_DIR, save_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        base_url = get_base_url()
        share_url = f"{base_url}/v/{short_id}"
        
        return jsonify({
            "success": True,
            "id": short_id,
            "name": filename,
            "size": len(file_bytes),
            "share_url": share_url
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --------------------------------------------------------------------------
# 3. View Hosted PDF
# --------------------------------------------------------------------------
@app.route('/v/<short_id>')
def view_pdf(short_id):
    clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', short_id)
    filename = f"{clean_id}.pdf"
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        return "PDF not found or link has expired.", 404
        
    return send_from_directory(STORAGE_DIR, filename, mimetype='application/pdf')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ScanVault Core Backend')
    default_port = int(os.environ.get('PORT', 5050))
    parser.add_argument('--port', type=int, default=default_port, help='Port to run server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()

    print(f"🚀 ScanVault Core Backend running on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)

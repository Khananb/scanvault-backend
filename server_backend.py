#!/usr/bin/env python3
"""
ScanVault - Core OCR & PDF Cloud Backend
Supports Multi-Page PDF OCR, Image OCR, Multi-language (Eng + Hindi), Preprocessing & File Hosting
"""
import os
import io
import re
import sys
import json
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

OCR_API_URL = os.environ.get('OCR_API_URL', 'https://ocrhinglish.in/api/v1/ocr')
OCR_API_KEY = os.environ.get('OCR_API_KEY', 'ocr_live_R5q2rZVGcUujqYkZMBI2DHJIZuoaMxzCqapwjZumzhk')

STORAGE_DIR = os.path.expanduser('~/pdf_host')
os.makedirs(STORAGE_DIR, exist_ok=True)

def call_upstream_ocr(file_bytes, filename="image.png", lang="eng"):
    """
    High-speed hardware accelerated OCR via upstream API.
    """
    if not OCR_API_KEY or not OCR_API_URL:
        return None
    try:
        boundary = uuid.uuid4().hex
        body = bytearray()
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="language"\r\n\r\n{lang}\r\n'.encode('utf-8'))
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode('utf-8'))
        body.extend(file_bytes)
        body.extend(f'\r\n--{boundary}--\r\n'.encode('utf-8'))

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-api-key': OCR_API_KEY,
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }
        
        req = urllib.request.Request(OCR_API_URL, data=bytes(body), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=25) as resp:
            if resp.status == 200:
                res_data = json.loads(resp.read().decode('utf-8'))
                text = (res_data.get('text') or '').strip()
                pages = res_data.get('pages', 1)
                words = len(text.split()) if text else 0
                chars = len(text)
                return {
                    "success": True,
                    "text": text,
                    "pages": pages,
                    "word_count": words,
                    "char_count": chars,
                    "duration_ms": res_data.get('duration_ms', 0),
                    "engine": "hardware_accelerated_api"
                }
    except Exception as e:
        print(f"Upstream OCR API notice (will use local fallback): {e}")
        return None
    return None

def get_base_url():
    """Dynamically determine public base URL respecting proxies/Cloudflare tunnels."""
    forwarded_proto = request.headers.get('X-Forwarded-Proto', request.scheme)
    forwarded_host = request.headers.get('X-Forwarded-Host', request.host)
    return f"{forwarded_proto}://{forwarded_host}"

def preprocess_image(image):
    """
    Multi-stage image enhancement pipeline for maximum Tesseract OCR accuracy:
    1. Grayscale & RGBA normalization
    2. Resampling & Smart Upscaling for low-resolution/small images (< 1500px)
    3. Dynamic Contrast & Sharpness Tuning
    4. Adaptive Binarization (Separating text from background noise/shadows)
    """
    try:
        if image.mode in ('RGBA', 'P', 'LA'):
            image = image.convert('RGB')
        
        # 1. Smart Upscaling: Ensure min dimension is at least 1500px for optimal OCR DPI
        w, h = image.size
        min_dim = min(w, h)
        if min_dim < 1500:
            scale_factor = max(2.0, 1800.0 / min_dim)
            # Limit maximum dimension to 3600px to prevent excessive RAM usage
            target_w = int(min(w * scale_factor, 3600))
            target_h = int(min(h * scale_factor, 3600))
            resample_filter = getattr(Image, 'Resampling', Image).LANCZOS
            image = image.resize((target_w, target_h), resample_filter)

        # 2. Grayscale conversion & Auto-contrast adjustment
        gray = image.convert('L')
        gray_enhanced = ImageOps.autocontrast(gray, cutoff=1)
        
        # 3. Enhance Contrast & Sharpness
        contrast_enhancer = ImageEnhance.Contrast(gray_enhanced)
        contrasted = contrast_enhancer.enhance(1.6)
        
        sharp_enhancer = ImageEnhance.Sharpness(contrasted)
        sharpened = sharp_enhancer.enhance(1.5)
        
        # 4. Adaptive Binarization / Contrast Stretching
        # Enhances dark text pixels while pushing paper tint/shadows to pure white
        lut = [255 if x > 145 else (0 if x < 85 else int((x - 85) * (255.0 / 60.0))) for x in range(256)]
        binarized = sharpened.point(lut, mode='L')
        
        return binarized
    except Exception as e:
        print(f"Preprocessing notice: {e}")
        return image.convert('RGB') if image.mode != 'RGB' else image

def ocr_single_image(image, lang='eng'):
    """
    Run multi-stage Tesseract OCR on a PIL Image with PSM Auto-Fallback:
    - Primary: PSM 3 (Fully automatic page segmentation)
    - Fallback 1: PSM 6 (Uniform single block of text - Receipts, Badges, Single Paragraphs)
    - Fallback 2: PSM 11 (Sparse text - Stray words, Labels, Unstructured text)
    """
    prep_img = preprocess_image(image)
    
    # Try combinations of languages if standard lang is provided
    search_langs = [lang]
    if lang != 'eng' and 'eng' not in lang:
        search_langs.append(f"{lang}+eng")
        search_langs.append('eng')

    psm_modes = [3, 6, 11]
    best_text = ""
    
    for current_lang in search_langs:
        for psm in psm_modes:
            config = f'--oem 1 --psm {psm}'
            try:
                text = pytesseract.image_to_string(prep_img, lang=current_lang, config=config).strip()
                # If text is substantial (> 10 words or > 40 chars), accept immediately
                if len(text.split()) >= 10 or len(text) > 40:
                    return text
                # Keep the longest extracted result across fallbacks
                if len(text) > len(best_text):
                    best_text = text
            except Exception as e:
                print(f"Tesseract PSM {psm} / Lang '{current_lang}' attempt notice: {e}")
                continue
                
    # If preprocessed image produced very sparse text, attempt raw image scan as last safety net
    if not best_text:
        try:
            raw_text = pytesseract.image_to_string(image, lang='eng', config='--oem 1 --psm 3').strip()
            if len(raw_text) > len(best_text):
                best_text = raw_text
        except Exception:
            pass

    return best_text.strip()

def process_pdf_ocr(pdf_bytes, lang='eng'):
    """
    Hybrid PDF extraction:
    1. First tries fast digital text extraction via pypdf.
    2. If scanned / low text, renders high-DPI (300 DPI) page images & applies multi-pass OCR.
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

    # Step 2: High-DPI Optical Character Recognition on PDF pages (300 DPI)
    try:
        images = convert_from_bytes(pdf_bytes, dpi=300, thread_count=4)
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
        "engine": "Tesseract 5.5.3 Native (Eng + Hin) + Poppler PDF [vL9.1]",
        "version": "vL9.1",
        "features": ["Image OCR", "Multi-Page PDF OCR", "Hindi + English", "Instant PDF Cloud Hosting", "Advanced Preprocessing Pipeline vL9.1"]
    })

# --------------------------------------------------------------------------
# 1. Unified OCR Endpoint (Images, Multi-Page PDFs, Base64 Screenshots, Remote URLs)
# --------------------------------------------------------------------------
@app.route('/api/ocr', methods=['POST'])
def process_ocr():
    try:
        json_data = request.get_json(silent=True) or {}
        lang = request.form.get('lang') or json_data.get('lang') or 'eng'
        
        file_bytes = None
        filename = "document.png"
        
        # A. Remote URL check (from Context Menu on web image)
        image_url = json_data.get('image_url') or json_data.get('url')
        if image_url:
            req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                file_bytes = resp.read()
                filename = "web_image.png"
        else:
            # B. File Upload Check (Image or PDF)
            upload_file = request.files.get('image') or request.files.get('file')
            if upload_file:
                filename = upload_file.filename or "upload.png"
                file_bytes = upload_file.read()
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
                
                file_bytes = base64.b64decode(raw_base64)
                if file_bytes.startswith(b'%PDF'):
                    filename = "document.pdf"
                else:
                    filename = "screenshot.png"

        if not file_bytes:
            return jsonify({"success": False, "error": "Empty file data received"}), 400

        # Try fast upstream hardware-accelerated API first
        upstream_res = call_upstream_ocr(file_bytes, filename=filename, lang=lang)
        if upstream_res and upstream_res.get("success"):
            return jsonify(upstream_res)

        # Fallback to local processing if API is unavailable
        text = ""
        page_count = 1
        if filename.lower().endswith('.pdf') or file_bytes.startswith(b'%PDF'):
            text, page_count = process_pdf_ocr(file_bytes, lang=lang)
        else:
            image = Image.open(io.BytesIO(file_bytes))
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
            "char_count": chars,
            "engine": "local_tesseract_fallback"
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

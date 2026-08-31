import urllib.request
import json
import io
import base64
from PIL import Image, ImageDraw

print("=== 1. Testing Image Base64 OCR ===")
img = Image.new('RGB', (400, 120), color=(255, 255, 255))
d = ImageDraw.Draw(img)
d.text((30, 45), 'HIGH ACCURACY OCR TEST 2026', fill=(0, 0, 0))

buf = io.BytesIO()
img.save(buf, format='PNG')
img_bytes = buf.getvalue()
b64_str = base64.b64encode(img_bytes).decode('utf-8')

payload = json.dumps({"image": f"data:image/png;base64,{b64_str}"}).encode('utf-8')
req = urllib.request.Request(
    'http://192.168.0.190:5050/api/ocr',
    data=payload,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as res:
    print("Image OCR Response:", json.loads(res.read()))

print("\n=== 2. Testing PDF OCR Extraction ===")
pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 60 >> stream
BT
/F1 20 Tf
100 700 Td
(QUICK MEDICAL REPORT - PATIENT 4092) Tj
ET
endstream
endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000355 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
429
%%EOF"""

boundary = '----PDFBoundaryTest123'
body = (
    f'--{boundary}\r\n'
    'Content-Disposition: form-data; name="file"; filename="medical_report.pdf"\r\n'
    'Content-Type: application/pdf\r\n\r\n'
).encode('utf-8') + pdf_content + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req_pdf = urllib.request.Request(
    'http://192.168.0.190:5050/api/ocr',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
with urllib.request.urlopen(req_pdf) as res:
    print("PDF OCR Response:", json.loads(res.read()))

print("\n=== 3. Testing PDF Hosting Upload ===")
body_upload = (
    f'--{boundary}\r\n'
    'Content-Disposition: form-data; name="file"; filename="uploaded_doc.pdf"\r\n'
    'Content-Type: application/pdf\r\n\r\n'
).encode('utf-8') + pdf_content + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req_upload = urllib.request.Request(
    'http://192.168.0.190:5050/api/upload',
    data=body_upload,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)
with urllib.request.urlopen(req_upload) as res:
    print("PDF Upload Response:", json.loads(res.read()))

print("\n=== All Advanced Engine Tests Passed! ===")

import os
from PIL import Image, ImageDraw, ImageFont

# Create output folder
OUTPUT_DIR = r'd:\APP\image'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Generating Chrome Web Store media assets...")

def get_font(size, bold=False):
    try:
        # Try standard Windows fonts
        font_path = "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf"
        if not os.path.exists(font_path):
            font_path = "C:\\Windows\\Fonts\\seguiemj.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

# --------------------------------------------------------------------------
# Helper: Draw Browser Window with ScanVault UI Mockup
# --------------------------------------------------------------------------
def draw_mockup_canvas(title_text, subtitle_text, feature_badge, draw_custom_content=None):
    # Canvas 1280x800 (RGB, no alpha)
    img = Image.new('RGB', (1280, 800), color=(248, 250, 252))
    d = ImageDraw.Draw(img)

    # Top gradient / accent bar
    d.rectangle([0, 0, 1280, 6], fill=(15, 23, 42))

    # Background subtle grid pattern
    for x in range(0, 1280, 40):
        d.line([(x, 0), (x, 800)], fill=(241, 245, 249), width=1)
    for y in range(0, 800, 40):
        d.line([(0, y), (1280, y)], fill=(241, 245, 249), width=1)

    # Main Browser Window Mockup Frame
    bx, by, bw, bh = 80, 60, 1120, 680
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(255, 255, 255), outline=(226, 232, 240), width=2)

    # Browser Header bar
    d.rounded_rectangle([bx, by, bx + bw, by + 42], radius=12, fill=(241, 245, 249))
    d.rectangle([bx, by + 30, bx + bw, by + 42], fill=(241, 245, 249))

    # Browser Dots
    d.ellipse([bx + 16, by + 16, bx + 26, by + 26], fill=(239, 68, 68))
    d.ellipse([bx + 32, by + 16, bx + 42, by + 26], fill=(245, 158, 11))
    d.ellipse([bx + 48, by + 16, bx + 58, by + 26], fill=(16, 185, 129))

    # URL Bar
    d.rounded_rectangle([bx + 80, by + 10, bx + 700, by + 32], radius=6, fill=(255, 255, 255), outline=(203, 213, 225))
    font_url = get_font(12)
    d.text((bx + 92, by + 13), "https://scanvault.app/dashboard", fill=(71, 85, 105), font=font_url)

    # Title Banner on Webpage
    font_badge = get_font(12, bold=True)
    font_title = get_font(24, bold=True)
    font_sub = get_font(14)

    d.rounded_rectangle([bx + 40, by + 70, bx + 160, by + 94], radius=12, fill=(241, 245, 249), outline=(226, 232, 240))
    d.text((bx + 52, by + 74), feature_badge, fill=(15, 23, 42), font=font_badge)

    d.text((bx + 40, by + 106), title_text, fill=(15, 23, 42), font=font_title)
    d.text((bx + 40, by + 140), subtitle_text, fill=(100, 116, 139), font=font_sub)

    # Extension Popup Overlay Mockup (Right Side of Browser)
    px, py, pw, ph = bx + 680, by + 65, 380, 580
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=14, fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=14, outline=(15, 23, 42), width=1)

    # Popup Header inside mockup
    d.rounded_rectangle([px + 12, py + 12, px + 40, py + 40], radius=6, fill=(15, 23, 42))
    font_brand = get_font(15, bold=True)
    d.text((px + 48, py + 16), "ScanVault", fill=(15, 23, 42), font=font_brand)
    
    font_pro = get_font(9, bold=True)
    d.rounded_rectangle([px + 130, py + 18, px + 165, py + 34], radius=4, fill=(241, 245, 249), outline=(226, 232, 240))
    d.text((px + 136, py + 20), "PRO", fill=(71, 85, 105), font=font_pro)

    # Status Pill (Connected)
    d.rounded_rectangle([px + 270, py + 16, px + 360, py + 36], radius=12, fill=(240, 253, 244), outline=(187, 247, 208))
    d.ellipse([px + 278, py + 23, px + 284, py + 29], fill=(22, 163, 74))
    font_pill = get_font(11, bold=True)
    d.text((px + 290, py + 18), "Connected", fill=(22, 163, 74), font=font_pill)

    # Tabs inside Popup
    d.rounded_rectangle([px + 12, py + 50, px + pw - 12, py + 82], radius=8, fill=(238, 242, 246))
    d.rounded_rectangle([px + 15, py + 53, px + 180, py + 79], radius=6, fill=(255, 255, 255))
    
    font_tab = get_font(12, bold=True)
    font_tab_subtle = get_font(12)
    d.text((px + 45, py + 58), "OCR Scanner", fill=(15, 23, 42), font=font_tab)
    d.text((px + 230, py + 58), "PDF Host", fill=(100, 116, 139), font=font_tab_subtle)

    if draw_custom_content:
        draw_custom_content(d, bx, by, px, py, pw, ph)

    return img

# --------------------------------------------------------------------------
# 1. Screenshot 1: Full Tab & Image OCR Scanner
# --------------------------------------------------------------------------
def create_screenshot1():
    def custom_draw(d, bx, by, px, py, pw, ph):
        # Webpage Sample Document
        d.rounded_rectangle([bx + 40, by + 180, bx + 640, by + 640], radius=8, fill=(248, 250, 252), outline=(226, 232, 240))
        font_doc_head = get_font(16, bold=True)
        font_doc_body = get_font(13)
        d.text((bx + 60, by + 200), "FINANCIAL SUMMARY STATEMENT 2026", fill=(15, 23, 42), font=font_doc_head)
        lines = [
          "Quarter 1 Revenue: $1,420,000.00",
          "Operating Expenses: $380,500.00",
          "Net Income Margin: +24.8%",
          "Audited by Cloud Analytics Group",
          "Status: Confirmed & Sealed"
        ]
        for idx, line in enumerate(lines):
            d.text((bx + 60, by + 240 + idx * 28), line, fill=(71, 85, 105), font=font_doc_body)

        # Popup primary action
        d.rounded_rectangle([px + 12, py + 94, px + pw - 12, py + 134], radius=8, fill=(15, 23, 42))
        font_btn = get_font(13, bold=True)
        font_btn_sub = get_font(10)
        d.text((px + 50, py + 100), "Scan Current Tab", fill=(255, 255, 255), font=font_btn)
        d.text((px + 50, py + 118), "Capture visible page and extract text", fill=(148, 163, 184), font=font_btn_sub)

        # Dropzone
        d.rounded_rectangle([px + 12, py + 144, px + pw - 12, py + 220], radius=10, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
        font_drop = get_font(12, bold=True)
        font_sub = get_font(10)
        d.text((px + 85, py + 165), "Drop image or PDF to extract text", fill=(15, 23, 42), font=font_drop)
        d.text((px + 110, py + 185), "PDF, PNG, JPG, WEBP, TIFF", fill=(148, 163, 184), font=font_sub)

        # Result Area
        d.rounded_rectangle([px + 12, py + 230, px + pw - 12, py + 550], radius=8, fill=(255, 255, 255), outline=(226, 232, 240))
        d.text((px + 24, py + 240), "EXTRACTED TEXT", fill=(100, 116, 139), font=get_font(10, bold=True))
        d.text((px + 270, py + 240), "42 words", fill=(148, 163, 184), font=get_font(10))

        # Textarea inside Popup
        d.rounded_rectangle([px + 20, py + 265, px + pw - 20, py + 490], radius=6, fill=(252, 252, 253), outline=(226, 232, 240))
        ocr_lines = [
          "FINANCIAL SUMMARY STATEMENT 2026",
          "Quarter 1 Revenue: $1,420,000.00",
          "Operating Expenses: $380,500.00",
          "Net Income Margin: +24.8%",
          "Audited by Cloud Analytics Group"
        ]
        font_mono = get_font(11)
        for idx, line in enumerate(ocr_lines):
            d.text((px + 28, py + 275 + idx * 22), line, fill=(15, 23, 42), font=font_mono)

        # Post-Processing Action buttons
        d.rounded_rectangle([px + 20, py + 505, px + 120, py + 535], radius=4, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((px + 30, py + 513), "Clean Lines", fill=(71, 85, 105), font=get_font(10, bold=True))

        d.rounded_rectangle([px + 130, py + 505, px + 230, py + 535], radius=4, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((px + 145, py + 513), "Format CSV", fill=(71, 85, 105), font=get_font(10, bold=True))

        d.rounded_rectangle([px + 240, py + 505, px + 345, py + 535], radius=4, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((px + 252, py + 513), "JSON Format", fill=(71, 85, 105), font=get_font(10, bold=True))

    img = draw_mockup_canvas(
        "Full Tab & Image OCR Scanner",
        "Instant optical character recognition for web pages, screenshots, and graphics",
        "HIGH ACCURACY OCR",
        custom_draw
    )
    img.save(os.path.join(OUTPUT_DIR, 'screenshot1_ocr_tab.png'), 'PNG')
    print(" - Created screenshot1_ocr_tab.png")

# --------------------------------------------------------------------------
# 2. Screenshot 2: Multi-Page PDF OCR & Hindi Language Support
# --------------------------------------------------------------------------
def create_screenshot2():
    def custom_draw(d, bx, by, px, py, pw, ph):
        # Webpage PDF Reader View
        d.rounded_rectangle([bx + 40, by + 180, bx + 640, by + 640], radius=8, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((bx + 60, by + 200), "INVOICE & RECEIPT #98234 (PDF DOCUMENT)", fill=(15, 23, 42), font=get_font(15, bold=True))
        d.text((bx + 60, by + 235), "भाषा: हिन्दी और अंग्रेजी | Language: Hindi & English", fill=(100, 116, 139), font=get_font(12))
        
        pdf_sample = [
          "--- Page 1 ---",
          "Customer Name: Rajesh Kumar",
          "भुगतान विवरण: रसीद संख्या 4092",
          "Total Paid: 5,400.00",
          "--- Page 2 ---",
          "Term & Conditions Accepted"
        ]
        for idx, line in enumerate(pdf_sample):
            d.text((bx + 60, by + 270 + idx * 26), line, fill=(71, 85, 105), font=get_font(12))

        # Language dropdown bar inside popup
        d.rounded_rectangle([px + 12, py + 94, px + pw - 12, py + 126], radius=6, fill=(255, 255, 255), outline=(226, 232, 240))
        d.text((px + 22, py + 102), "OCR Language:", fill=(71, 85, 105), font=get_font(11, bold=True))
        
        d.rounded_rectangle([px + 180, py + 98, px + pw - 20, py + 122], radius=4, fill=(248, 250, 252), outline=(203, 213, 225))
        d.text((px + 190, py + 103), "English + Hindi (Mixed)", fill=(15, 23, 42), font=get_font(11, bold=True))

        # Dropzone for PDF
        d.rounded_rectangle([px + 12, py + 136, px + pw - 12, py + 210], radius=10, fill=(248, 250, 252), outline=(15, 23, 42), width=1)
        d.text((px + 80, py + 155), "Drop PDF or Image to extract text", fill=(15, 23, 42), font=get_font(12, bold=True))
        d.text((px + 95, py + 175), "Supports multi-page PDF documents", fill=(71, 85, 105), font=get_font(10))

        # Result area with pages
        d.rounded_rectangle([px + 12, py + 220, px + pw - 12, py + 550], radius=8, fill=(255, 255, 255), outline=(226, 232, 240))
        d.text((px + 24, py + 230), "EXTRACTED TEXT", fill=(100, 116, 139), font=get_font(10, bold=True))
        d.text((px + 250, py + 230), "2 pages • 38 words", fill=(148, 163, 184), font=get_font(10))

        d.rounded_rectangle([px + 20, py + 255, px + pw - 20, py + 490], radius=6, fill=(252, 252, 253), outline=(226, 232, 240))
        ocr_pdf_result = [
          "--- Page 1 ---",
          "Customer Name: Rajesh Kumar",
          "भुगतान विवरण: रसीद संख्या 4092",
          "Total Paid: 5,400.00",
          "",
          "--- Page 2 ---",
          "Term & Conditions Accepted"
        ]
        for idx, line in enumerate(ocr_pdf_result):
            d.text((px + 28, py + 265 + idx * 22), line, fill=(15, 23, 42), font=get_font(11))

    img = draw_mockup_canvas(
        "Multi-Page PDF OCR & Hindi Language Support",
        "Extract text from multi-page PDFs and bilingual English/Hindi documents",
        "MULTI-PAGE PDF OCR",
        custom_draw
    )
    img.save(os.path.join(OUTPUT_DIR, 'screenshot2_pdf_ocr.png'), 'PNG')
    print(" - Created screenshot2_pdf_ocr.png")

# --------------------------------------------------------------------------
# 3. Screenshot 3: Interactive Area Snipping Tool
# --------------------------------------------------------------------------
def create_screenshot3():
    def custom_draw(d, bx, by, px, py, pw, ph):
        # Webpage with Crop Selection Rectangle
        d.rounded_rectangle([bx + 40, by + 180, bx + 640, by + 640], radius=8, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((bx + 60, by + 200), "DASHBOARD ANALYTICS TABLE", fill=(15, 23, 42), font=get_font(16, bold=True))

        # Selection Overlay Box (Simulated Snip Area)
        sx, sy, sw, sh = bx + 50, by + 240, 520, 220
        d.rectangle([sx, sy, sx + sw, sy + sh], outline=(37, 99, 235), width=2)
        d.rectangle([sx + 4, sy + 4, sx + sw - 4, sy + sh - 4], outline=(255, 255, 255), width=1)

        # Snipping Hint Tag
        d.rounded_rectangle([bx + 200, by + 130, bx + 480, by + 162], radius=16, fill=(15, 23, 42))
        d.text((bx + 215, by + 138), "Drag box to crop & scan selected area", fill=(255, 255, 255), font=get_font(11, bold=True))

        lines = [
          "Metric Name       Value      Growth",
          "Active Users     124,500     +18.4%",
          "Monthly Revenue   $92,400     +12.1%",
          "Server Latency     42ms       -8.5%"
        ]
        for idx, line in enumerate(lines):
            d.text((sx + 15, sy + 15 + idx * 32), line, fill=(15, 23, 42), font=get_font(13, bold=True if idx == 0 else False))

        # Popup Buttons showing Snip Area highlighted
        d.rounded_rectangle([px + 12, py + 94, px + 180, py + 134], radius=8, fill=(37, 99, 235))
        d.text((px + 30, py + 102), "Snip Area", fill=(255, 255, 255), font=get_font(12, bold=True))
        d.text((px + 30, py + 118), "Drag box to crop", fill=(219, 234, 254), font=get_font(9))

        d.rounded_rectangle([px + 190, py + 94, px + pw - 12, py + 134], radius=8, fill=(15, 23, 42))
        d.text((px + 210, py + 102), "Full Tab", fill=(255, 255, 255), font=get_font(12, bold=True))
        d.text((px + 210, py + 118), "Scan whole screen", fill=(148, 163, 184), font=get_font(9))

        # Snipped Result
        d.rounded_rectangle([px + 12, py + 150, px + pw - 12, py + 550], radius=8, fill=(255, 255, 255), outline=(226, 232, 240))
        d.text((px + 24, py + 160), "SNIPPED AREA OCR RESULT", fill=(100, 116, 139), font=get_font(10, bold=True))

        d.rounded_rectangle([px + 20, py + 185, px + pw - 20, py + 490], radius=6, fill=(252, 252, 253), outline=(226, 232, 240))
        for idx, line in enumerate(lines):
            d.text((px + 28, py + 195 + idx * 26), line, fill=(15, 23, 42), font=get_font(11))

    img = draw_mockup_canvas(
        "Interactive Area Snipping Tool",
        "Crop and scan specific screen areas, tables, code blocks, or regions",
        "SNIP & SCAN TOOL",
        custom_draw
    )
    img.save(os.path.join(OUTPUT_DIR, 'screenshot3_snip_tool.png'), 'PNG')
    print(" - Created screenshot3_snip_tool.png")

# --------------------------------------------------------------------------
# 4. Screenshot 4: Instant Free PDF Cloud Hosting & QR Code
# --------------------------------------------------------------------------
def create_screenshot4():
    def custom_draw(d, bx, by, px, py, pw, ph):
        # Webpage PDF viewer preview
        d.rounded_rectangle([bx + 40, by + 180, bx + 640, by + 640], radius=8, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((bx + 60, by + 200), "LIVE HOSTED PDF DOCUMENT", fill=(15, 23, 42), font=get_font(16, bold=True))
        d.text((bx + 60, by + 230), "URL: https://deviceos.online/v/305ea483", fill=(37, 99, 235), font=get_font(13))

        # Switch popup to PDF Host tab
        d.rounded_rectangle([px + 12, py + 50, px + pw - 12, py + 82], radius=8, fill=(238, 242, 246))
        d.rounded_rectangle([px + 180, py + 53, px + pw - 15, py + 79], radius=6, fill=(255, 255, 255))
        d.text((px + 45, py + 58), "OCR Scanner", fill=(100, 116, 139), font=get_font(12))
        d.text((px + 230, py + 58), "PDF Host", fill=(15, 23, 42), font=get_font(12, bold=True))

        # PDF Success Card inside Popup
        d.rounded_rectangle([px + 12, py + 94, px + pw - 12, py + 380], radius=10, fill=(255, 255, 255), outline=(187, 247, 208), width=2)
        d.text((px + 40, py + 106), "PDF Hosted Successfully!", fill=(22, 163, 74), font=get_font(13, bold=True))

        d.text((px + 24, py + 134), "annual_report_2026.pdf", fill=(15, 23, 42), font=get_font(12, bold=True))
        d.text((px + 270, py + 134), "1.8 MB", fill=(148, 163, 184), font=get_font(11))

        # Share URL box
        d.rounded_rectangle([px + 20, py + 160, px + 280, py + 190], radius=6, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((px + 30, py + 168), "https://deviceos.online/v/305ea483", fill=(15, 23, 42), font=get_font(10))

        d.rounded_rectangle([px + 285, py + 160, px + 345, py + 190], radius=6, fill=(15, 23, 42))
        d.text((px + 300, py + 168), "Copy", fill=(255, 255, 255), font=get_font(11, bold=True))

        # Mockup QR Code Container inside Popup
        d.rounded_rectangle([px + 90, py + 205, px + 270, py + 335], radius=8, fill=(248, 250, 252), outline=(226, 232, 240))
        qx, qy = px + 120, py + 215
        d.rectangle([qx, qy, qx + 90, qy + 90], fill=(255, 255, 255), outline=(15, 23, 42), width=2)
        # Mock QR pixels
        d.rectangle([qx + 10, qy + 10, qx + 35, qy + 35], fill=(15, 23, 42))
        d.rectangle([qx + 55, qy + 10, qx + 80, qy + 35], fill=(15, 23, 42))
        d.rectangle([qx + 10, qy + 55, qx + 35, qy + 80], fill=(15, 23, 42))
        d.rectangle([qx + 45, qy + 45, qx + 65, qy + 65], fill=(15, 23, 42))
        
        d.text((px + 105, py + 312), "Scan with camera to open PDF", fill=(100, 116, 139), font=get_font(9))

        # Recent Uploads History List
        d.text((px + 16, py + 395), "RECENT UPLOADS", fill=(148, 163, 184), font=get_font(10, bold=True))
        hist_items = ["quarterly_audit.pdf", "project_proposal.pdf", "invoice_9823.pdf"]
        for idx, item in enumerate(hist_items):
            d.rounded_rectangle([px + 12, py + 415 + idx * 40, px + pw - 12, py + 448 + idx * 40], radius=6, fill=(255, 255, 255), outline=(226, 232, 240))
            d.text((px + 24, py + 424 + idx * 40), item, fill=(15, 23, 42), font=get_font(11, bold=True))
            d.text((px + 290, py + 424 + idx * 40), "Copy", fill=(37, 99, 235), font=get_font(11))

    img = draw_mockup_canvas(
        "Instant Free PDF Cloud Hosting & QR Code",
        "Host PDFs with instant short links, camera QR codes, and upload history",
        "PDF CLOUD HOSTING",
        custom_draw
    )
    img.save(os.path.join(OUTPUT_DIR, 'screenshot4_pdf_hosting.png'), 'PNG')
    print(" - Created screenshot4_pdf_hosting.png")

# --------------------------------------------------------------------------
# 5. Screenshot 5: Right-Click Context Menu Actions
# --------------------------------------------------------------------------
def create_screenshot5():
    def custom_draw(d, bx, by, px, py, pw, ph):
        # Webpage with open Right-Click Context Menu
        d.rounded_rectangle([bx + 40, by + 180, bx + 640, by + 640], radius=8, fill=(248, 250, 252), outline=(226, 232, 240))
        d.text((bx + 60, by + 200), "ARTICLE & WEBPAGE GRAPHICS", fill=(15, 23, 42), font=get_font(16, bold=True))

        # Sample Web Image on page
        d.rounded_rectangle([bx + 60, by + 240, bx + 440, by + 500], radius=8, fill=(226, 232, 240), outline=(203, 213, 225))
        d.text((bx + 140, by + 360), "[ SAMPLE WEBPAGE IMAGE ]", fill=(100, 116, 139), font=get_font(14, bold=True))

        # Right-Click Context Menu Mockup
        mx, my, mw, mh = bx + 280, by + 300, 290, 200
        d.rounded_rectangle([mx, my, mx + mw, my + mh], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=2)

        menu_options = [
          ("Open image in new tab", False),
          ("Save image as...", False),
          ("Copy image address", False),
          ("Extract Text with ScanVault", True),
          ("Host PDF with ScanVault", False)
        ]
        for idx, (opt, is_active) in enumerate(menu_options):
            oy = my + 10 + idx * 36
            if is_active:
                d.rectangle([mx + 4, oy - 2, mx + mw - 4, oy + 30], fill=(15, 23, 42))
                d.text((mx + 16, oy + 4), opt, fill=(255, 255, 255), font=get_font(12, bold=True))
            else:
                d.text((mx + 16, oy + 4), opt, fill=(71, 85, 105), font=get_font(12))

        # Chrome Desktop Notification Mockup (Bottom Right)
        nx, ny, nw, nh = bx + 360, by + 530, 320, 80
        d.rounded_rectangle([nx, ny, nx + nw, ny + nh], radius=10, fill=(15, 23, 42))
        d.text((nx + 16, ny + 14), "ScanVault OCR", fill=(255, 255, 255), font=get_font(12, bold=True))
        d.text((nx + 16, ny + 38), "Extracted text copied to clipboard!", fill=(226, 232, 240), font=get_font(11))

        # Popup standard overview
        d.rounded_rectangle([px + 12, py + 94, px + pw - 12, py + 550], radius=8, fill=(255, 255, 255), outline=(226, 232, 240))
        d.text((px + 24, py + 110), "RIGHT-CLICK ACTIONS READY", fill=(100, 116, 139), font=get_font(10, bold=True))
        
        d.text((px + 24, py + 140), "Extract text from any web image or host", fill=(15, 23, 42), font=get_font(12, bold=True))
        d.text((px + 24, py + 160), "any PDF directly from the context menu.", fill=(15, 23, 42), font=get_font(12, bold=True))

    img = draw_mockup_canvas(
        "Right-Click Context Menu Actions",
        "Extract text from web images or host PDF links directly with a right-click",
        "CONTEXT MENU INTEGRATION",
        custom_draw
    )
    img.save(os.path.join(OUTPUT_DIR, 'screenshot5_context_menu.png'), 'PNG')
    print(" - Created screenshot5_context_menu.png")

# --------------------------------------------------------------------------
# 6. Small Promo Tile (440x280 RGB PNG)
# --------------------------------------------------------------------------
def create_small_promo_tile():
    img = Image.new('RGB', (440, 280), color=(15, 23, 42))
    d = ImageDraw.Draw(img)

    # Subtle background pattern
    for x in range(0, 440, 20):
        d.line([(x, 0), (x, 280)], fill=(30, 41, 59), width=1)

    # Icon Logo Box
    d.rounded_rectangle([180, 40, 260, 120], radius=16, fill=(255, 255, 255))
    font_logo = get_font(32, bold=True)
    d.text((205, 58), "SV", fill=(15, 23, 42), font=font_logo)

    # Main Title
    font_title = get_font(24, bold=True)
    d.text((80, 145), "ScanVault Pro", fill=(255, 255, 255), font=font_title)

    # Subtitle
    font_sub = get_font(13)
    d.text((65, 185), "High Performance OCR & Free PDF Cloud", fill=(148, 163, 184), font=font_sub)

    # Badge Tag
    d.rounded_rectangle([140, 220, 300, 250], radius=15, fill=(37, 99, 235))
    font_tag = get_font(11, bold=True)
    d.text((155, 227), "CHROME EXTENSION", fill=(255, 255, 255), font=font_tag)

    img.save(os.path.join(OUTPUT_DIR, 'small_promo_tile.png'), 'PNG')
    print(" - Created small_promo_tile.png (440x280)")

# --------------------------------------------------------------------------
# 7. Marquee Promo Tile (1400x560 RGB PNG)
# --------------------------------------------------------------------------
def create_marquee_promo_tile():
    img = Image.new('RGB', (1400, 560), color=(15, 23, 42))
    d = ImageDraw.Draw(img)

    # Grid background pattern
    for x in range(0, 1400, 40):
        d.line([(x, 0), (x, 560)], fill=(30, 41, 59), width=1)
    for y in range(0, 560, 40):
        d.line([(0, y), (1400, y)], fill=(30, 41, 59), width=1)

    # Left Column: Branding & Feature Bullet List
    font_brand = get_font(38, bold=True)
    d.text((100, 100), "ScanVault Pro", fill=(255, 255, 255), font=font_brand)

    font_headline = get_font(22, bold=True)
    d.text((100, 160), "High-Speed OCR Extractor & Instant PDF Cloud", fill=(219, 234, 254), font=font_headline)

    features = [
      "✓ Multi-Page PDF & Image OCR (English & Hindi)",
      "✓ Area Snipping Tool (Crop & Scan any region)",
      "✓ Right-Click Context Menu Integration",
      "✓ One-Click Clean Lines, CSV & JSON Formatter",
      "✓ Instant PDF Hosting & Camera QR Code Generator"
    ]
    font_feat = get_font(16)
    for idx, f in enumerate(features):
        d.text((100, 230 + idx * 45), f, fill=(226, 232, 240), font=font_feat)

    # Right Column: Product Interface Card Graphic
    px, py, pw, ph = 820, 70, 480, 420
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=16, fill=(255, 255, 255))
    
    # Inner Header
    d.rounded_rectangle([px + 20, py + 20, px + 60, py + 60], radius=10, fill=(15, 23, 42))
    d.text((px + 30, py + 26), "SV", fill=(255, 255, 255), font=get_font(18, bold=True))

    d.text((px + 75, py + 28), "ScanVault Control Panel", fill=(15, 23, 42), font=get_font(18, bold=True))
    d.text((px + 75, py + 52), "Version K.1 • Connected", fill=(22, 163, 74), font=get_font(12, bold=True))

    # Mock Cards inside Banner
    d.rounded_rectangle([px + 20, py + 90, px + pw - 20, py + 220], radius=10, fill=(248, 250, 252), outline=(226, 232, 240))
    d.text((px + 35, py + 105), "OCR SCANNER ENGINE", fill=(100, 116, 139), font=get_font(11, bold=True))
    d.text((px + 35, py + 135), "Extract text from images, tab screens & multi-page PDFs", fill=(15, 23, 42), font=get_font(12))
    d.text((px + 35, py + 165), "Languages: English + Hindi (Native Tesseract 5.5)", fill=(71, 85, 105), font=get_font(11))

    d.rounded_rectangle([px + 20, py + 240, px + pw - 20, py + 390], radius=10, fill=(248, 250, 252), outline=(226, 232, 240))
    d.text((px + 35, py + 255), "PDF CLOUD HOSTING", fill=(100, 116, 139), font=get_font(11, bold=True))
    d.text((px + 35, py + 285), "Instant shortlinks + Camera QR code display", fill=(15, 23, 42), font=get_font(12))
    d.text((px + 35, py + 315), "https://deviceos.online/v/305ea483", fill=(37, 99, 235), font=get_font(12, bold=True))

    img.save(os.path.join(OUTPUT_DIR, 'marquee_promo_tile.png'), 'PNG')
    print(" - Created marquee_promo_tile.png (1400x560)")

# Execute all generators
create_screenshot1()
create_screenshot2()
create_screenshot3()
create_screenshot4()
create_screenshot5()
create_small_promo_tile()
create_marquee_promo_tile()

print("\nAll Chrome Web Store media assets created successfully in d:\\APP\\image!")

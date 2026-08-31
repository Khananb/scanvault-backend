// ScanVault Chrome Extension - Area Snipping Content Script & On-Page HUD

(function () {
  if (window.hasScanVaultSnipper) return;
  window.hasScanVaultSnipper = true;

  let currentLang = 'eng';

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'START_AREA_SNIP') {
      currentLang = request.lang || 'eng';
      startSnipping();
      sendResponse({ success: true });
    }

    if (request.action === 'PROCESS_SNIP_IMAGE') {
      handleSnipImage(request.dataUrl, request.crop, request.lang || currentLang);
    }

    if (request.action === 'SNIP_ERROR') {
      showToastHUD('❌ ' + (request.error || 'Capture failed'), 'error');
    }
  });

  function startSnipping() {
    const oldOverlay = document.getElementById('scanvault-snip-overlay');
    if (oldOverlay) oldOverlay.remove();

    const overlay = document.createElement('div');
    overlay.id = 'scanvault-snip-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 2147483647;
      background: rgba(15, 23, 42, 0.35);
      cursor: crosshair;
      user-select: none;
    `;

    const box = document.createElement('div');
    box.style.cssText = `
      position: absolute;
      border: 2px dashed #2563eb;
      background: rgba(37, 99, 235, 0.12);
      box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.45);
      display: none;
      pointer-events: none;
    `;
    overlay.appendChild(box);

    const hint = document.createElement('div');
    hint.style.cssText = `
      position: fixed;
      top: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: #0f172a;
      color: #f8fafc;
      padding: 10px 20px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 600;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 8px 24px rgba(0,0,0,0.35);
      border: 1px solid rgba(255,255,255,0.15);
      pointer-events: none;
      z-index: 2147483647;
      letter-spacing: 0.3px;
    `;
    hint.textContent = '✂️ Drag a box to crop & scan • Press Esc to cancel';
    overlay.appendChild(hint);

    document.body.appendChild(overlay);

    let startX = 0, startY = 0, isSelecting = false;

    function onKeyDown(e) {
      if (e.key === 'Escape') {
        cleanup();
      }
    }

    function onMouseDown(e) {
      isSelecting = true;
      startX = e.clientX;
      startY = e.clientY;
      box.style.left = startX + 'px';
      box.style.top = startY + 'px';
      box.style.width = '0px';
      box.style.height = '0px';
      box.style.display = 'block';
    }

    function onMouseMove(e) {
      if (!isSelecting) return;
      const currentX = e.clientX;
      const currentY = e.clientY;

      const left = Math.min(startX, currentX);
      const top = Math.min(startY, currentY);
      const width = Math.abs(currentX - startX);
      const height = Math.abs(currentY - startY);

      box.style.left = left + 'px';
      box.style.top = top + 'px';
      box.style.width = width + 'px';
      box.style.height = height + 'px';
    }

    function onMouseUp(e) {
      if (!isSelecting) return;
      isSelecting = false;

      const currentX = e.clientX;
      const currentY = e.clientY;

      const left = Math.min(startX, currentX);
      const top = Math.min(startY, currentY);
      const width = Math.abs(currentX - startX);
      const height = Math.abs(currentY - startY);

      cleanup();

      if (width > 15 && height > 15) {
        showToastHUD('⚡ ScanVault: Extracting text...', 'loading');
        const crop = {
          x: left,
          y: top,
          width: width,
          height: height,
          devicePixelRatio: window.devicePixelRatio || 1
        };

        chrome.runtime.sendMessage({
          action: 'AREA_SNIP_CAPTURED',
          crop: crop,
          lang: currentLang
        });
      }
    }

    function cleanup() {
      window.removeEventListener('keydown', onKeyDown);
      overlay.removeEventListener('mousedown', onMouseDown);
      overlay.removeEventListener('mousemove', onMouseMove);
      overlay.removeEventListener('mouseup', onMouseUp);
      if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    }

    window.addEventListener('keydown', onKeyDown);
    overlay.addEventListener('mousedown', onMouseDown);
    overlay.addEventListener('mousemove', onMouseMove);
    overlay.addEventListener('mouseup', onMouseUp);
  }

  // --------------------------------------------------------------------------
  // Process Snip & Extract Text
  // --------------------------------------------------------------------------
  async function handleSnipImage(dataUrl, crop, lang) {
    try {
      const croppedBase64 = await cropImageCanvas(dataUrl, crop);
      
      chrome.runtime.sendMessage({ action: 'GET_BACKEND_URL' }, async (resp) => {
        const backendUrl = resp && resp.backendUrl ? resp.backendUrl : 'https://combining-personality-defend-holmes.trycloudflare.com';
        
        try {
          const ocrResp = await fetch(`${backendUrl}/api/ocr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: croppedBase64, lang: lang || 'eng' })
          });

          if (!ocrResp.ok) {
            throw new Error(`Server returned HTTP ${ocrResp.status}`);
          }

          const result = await ocrResp.json();
          const cleanText = (result.text || '').trim();

          if (cleanText) {
            try {
              await navigator.clipboard.writeText(cleanText);
            } catch (clipErr) {
              console.warn('Clipboard write failed, saved to storage:', clipErr);
            }

            chrome.storage.local.set({ last_ocr_result: cleanText });
            showFloatingResultHUD(cleanText, result.word_count || cleanText.split(/\s+/).length);
          } else {
            showToastHUD('⚠️ No readable text detected in selected area', 'warn');
          }
        } catch (err) {
          console.error('ScanVault Content OCR error:', err);
          showToastHUD(`❌ OCR Error: ${err.message}`, 'error');
        }
      });
    } catch (e) {
      console.error('Crop failure:', e);
      showToastHUD('❌ Failed to crop image', 'error');
    }
  }

  function cropImageCanvas(dataUrl, crop) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const ratio = crop.devicePixelRatio || 1;
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(crop.width * ratio);
        canvas.height = Math.round(crop.height * ratio);
        const ctx = canvas.getContext('2d');

        ctx.drawImage(
          img,
          Math.round(crop.x * ratio),
          Math.round(crop.y * ratio),
          Math.round(crop.width * ratio),
          Math.round(crop.height * ratio),
          0,
          0,
          canvas.width,
          canvas.height
        );

        resolve(canvas.toDataURL('image/png'));
      };
      img.onerror = reject;
      img.src = dataUrl;
    });
  }

  // --------------------------------------------------------------------------
  // Floating On-Page UI Badges
  // --------------------------------------------------------------------------
  function showToastHUD(text, type = 'info') {
    const old = document.getElementById('scanvault-toast-hud');
    if (old) old.remove();

    const toast = document.createElement('div');
    toast.id = 'scanvault-toast-hud';
    toast.style.cssText = `
      position: fixed;
      bottom: 28px;
      right: 28px;
      z-index: 2147483647;
      background: #0f172a;
      color: #f8fafc;
      padding: 12px 20px;
      border-radius: 12px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 13px;
      font-weight: 600;
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.15);
      animation: scanvaultFadeIn 0.25s ease-out;
      display: flex;
      align-items: center;
      gap: 10px;
    `;
    toast.textContent = text;

    document.body.appendChild(toast);

    if (type !== 'loading') {
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 3500);
    }
  }

  function showFloatingResultHUD(text, wordCount) {
    const old = document.getElementById('scanvault-toast-hud');
    if (old) old.remove();

    const oldModal = document.getElementById('scanvault-result-hud');
    if (oldModal) oldModal.remove();

    const hud = document.createElement('div');
    hud.id = 'scanvault-result-hud';
    hud.style.cssText = `
      position: fixed;
      bottom: 28px;
      right: 28px;
      width: 360px;
      max-width: calc(100vw - 56px);
      z-index: 2147483647;
      background: #0f172a;
      color: #f8fafc;
      padding: 16px;
      border-radius: 14px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 16px 40px rgba(0,0,0,0.45);
      border: 1px solid rgba(255,255,255,0.18);
      animation: scanvaultFadeIn 0.25s ease-out;
    `;

    const previewSnippet = text.length > 120 ? text.slice(0, 120) + '...' : text;

    hud.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10b981;"></span>
          <span style="font-weight:700; font-size:13px; color:#10b981;">✓ Copied to Clipboard</span>
        </div>
        <span style="font-size:11px; color:#94a3b8;">${wordCount} words</span>
      </div>
      <div style="background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:10px; font-size:12px; line-height:1.45; color:#cbd5e1; max-height:120px; overflow-y:auto; font-family:'JetBrains Mono', monospace; white-space:pre-wrap; margin-bottom:12px;">${escapeHtml(previewSnippet)}</div>
      <div style="display:flex; gap:8px;">
        <button id="scanvault-hud-copy" style="flex:1; background:#2563eb; color:#fff; border:none; border-radius:6px; padding:7px 12px; font-size:12px; font-weight:600; cursor:pointer;">Copy Again</button>
        <button id="scanvault-hud-close" style="background:rgba(255,255,255,0.1); color:#cbd5e1; border:none; border-radius:6px; padding:7px 12px; font-size:12px; font-weight:500; cursor:pointer;">Close</button>
      </div>
    `;

    document.body.appendChild(hud);

    document.getElementById('scanvault-hud-copy').addEventListener('click', async () => {
      await navigator.clipboard.writeText(text);
      document.getElementById('scanvault-hud-copy').textContent = '✓ Copied!';
      setTimeout(() => {
        const b = document.getElementById('scanvault-hud-copy');
        if (b) b.textContent = 'Copy Again';
      }, 1500);
    });

    document.getElementById('scanvault-hud-close').addEventListener('click', () => {
      hud.remove();
    });

    setTimeout(() => {
      if (hud.parentNode) hud.parentNode.removeChild(hud);
    }, 9000);
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
})();

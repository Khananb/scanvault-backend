// ScanVault Chrome Extension - High Performance OCR, Snipping, PDF Cloud & Post-Processing

document.addEventListener('DOMContentLoaded', async () => {
  const RENDER_BACKEND_URL = 'https://scanvault-backend-1.onrender.com';
  const TUNNEL_BACKEND_URL = 'https://ocrhinglish.in';
  const LAN_BACKEND_URL = 'http://192.168.0.192:9090';
  const DEFAULT_BACKEND_URL = RENDER_BACKEND_URL;

  // Header & Settings
  const connectionPill = document.getElementById('connection-pill');
  const connectionText = document.getElementById('connection-text');
  const btnToggleSettings = document.getElementById('btn-toggle-settings');
  const settingsPanel = document.getElementById('settings-panel');
  const backendUrlInput = document.getElementById('backend-url-input');
  const btnTestBackend = document.getElementById('btn-test-backend');
  const btnSaveSettings = document.getElementById('btn-save-settings');
  const presetRender = document.getElementById('preset-render');
  const presetTunnel = document.getElementById('preset-tunnel');
  const presetLan = document.getElementById('preset-lan');

  // Navigation
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  // OCR Elements
  const btnScanTab = document.getElementById('btn-scan-tab');
  const btnSnipArea = document.getElementById('btn-snip-area');
  const ocrLangSelect = document.getElementById('ocr-lang-select');
  const ocrDropZone = document.getElementById('ocr-drop-zone');
  const ocrFileInput = document.getElementById('ocr-file-input');
  const ocrStatusCard = document.getElementById('ocr-status-card');
  const ocrStatusText = document.getElementById('ocr-status-text');
  const ocrResultCard = document.getElementById('ocr-result-card');
  const ocrOutputText = document.getElementById('ocr-output-text');
  const ocrMetaInfo = document.getElementById('ocr-meta-info');
  const btnCopyOcr = document.getElementById('btn-copy-ocr');
  const btnDownloadOcr = document.getElementById('btn-download-ocr');
  const btnClearOcr = document.getElementById('btn-clear-ocr');

  // Post-Processing Buttons
  const btnCleanLines = document.getElementById('btn-clean-lines');
  const btnFormatCsv = document.getElementById('btn-format-csv');
  const btnFormatJson = document.getElementById('btn-format-json');

  // PDF Host Elements
  const pdfDropZone = document.getElementById('pdf-drop-zone');
  const pdfFileInput = document.getElementById('pdf-file-input');
  const pdfUploadCard = document.getElementById('pdf-upload-card');
  const pdfUploadStatus = document.getElementById('pdf-upload-status');
  const pdfSuccessCard = document.getElementById('pdf-success-card');
  const pdfFilenameDisplay = document.getElementById('pdf-filename-display');
  const pdfFilesizeDisplay = document.getElementById('pdf-filesize-display');
  const pdfShareUrl = document.getElementById('pdf-share-url');
  const btnCopyPdf = document.getElementById('btn-copy-pdf');
  const pdfOpenLink = document.getElementById('pdf-open-link');
  const btnHostAnother = document.getElementById('btn-host-another');
  const btnToggleQr = document.getElementById('btn-toggle-qr');
  const qrContainer = document.getElementById('qr-container');
  const qrCodeDisplay = document.getElementById('qr-code-display');
  
  const historyList = document.getElementById('history-list');
  const btnClearHistory = document.getElementById('btn-clear-history');
  const toast = document.getElementById('toast');

  let currentBackendUrl = DEFAULT_BACKEND_URL;

  // --------------------------------------------------------------------------
  // 1. Config & Health Check Engine
  // --------------------------------------------------------------------------
  async function loadConfig() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['scanvault_backend_url', 'scanvault_ocr_lang'], (res) => {
        let savedUrl = res.scanvault_backend_url;
        // Fix old defunct url without '-1'
        if (!savedUrl || savedUrl === 'https://scanvault-backend.onrender.com' || savedUrl === 'https://scanvault-backend.onrender.com/') {
          currentBackendUrl = RENDER_BACKEND_URL;
          chrome.storage.local.set({ scanvault_backend_url: RENDER_BACKEND_URL });
        } else {
          currentBackendUrl = savedUrl.replace(/\/+$/, '');
        }

        if (res.scanvault_ocr_lang) {
          ocrLangSelect.value = res.scanvault_ocr_lang;
        }
        backendUrlInput.value = currentBackendUrl;
        resolve(currentBackendUrl);
      });
    });
  }

  async function checkBackendHealth(targetUrl = currentBackendUrl, showFeedback = false) {
    targetUrl = (targetUrl || currentBackendUrl).replace(/\/+$/, '');
    connectionPill.className = 'status-pill checking';
    connectionText.textContent = 'Checking...';

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);

    try {
      const resp = await fetch(`${targetUrl}/api/health`, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (resp.ok) {
        currentBackendUrl = targetUrl;
        backendUrlInput.value = targetUrl;
        connectionPill.className = 'status-pill online';
        connectionText.textContent = 'Connected';
        if (showFeedback) showToast('Server connected!');
        return true;
      } else {
        throw new Error(`HTTP ${resp.status}`);
      }
    } catch (err) {
      clearTimeout(timeoutId);
      connectionPill.className = 'status-pill offline';
      connectionText.textContent = 'Offline';
      if (showFeedback) showToast('Could not connect to API server');
      return false;
    }
  }

  btnToggleSettings.addEventListener('click', () => {
    settingsPanel.classList.toggle('hidden');
  });

  connectionPill.addEventListener('click', () => {
    checkBackendHealth(currentBackendUrl, true);
  });

  if (presetRender) {
    presetRender.addEventListener('click', () => {
      backendUrlInput.value = RENDER_BACKEND_URL;
      btnSaveSettings.click();
    });
  }

  if (presetTunnel) {
    presetTunnel.addEventListener('click', () => {
      backendUrlInput.value = TUNNEL_BACKEND_URL;
      btnSaveSettings.click();
    });
  }

  if (presetLan) {
    presetLan.addEventListener('click', () => {
      backendUrlInput.value = LAN_BACKEND_URL;
      btnSaveSettings.click();
    });
  }

  btnTestBackend.addEventListener('click', async () => {
    const testUrl = backendUrlInput.value.trim();
    if (!testUrl) {
      showToast('Please enter a valid URL');
      return;
    }
    btnTestBackend.textContent = '...';
    await checkBackendHealth(testUrl, true);
    btnTestBackend.textContent = 'Test';
  });

  btnSaveSettings.addEventListener('click', async () => {
    let newUrl = backendUrlInput.value.trim().replace(/\/+$/, '');
    if (!newUrl.startsWith('http://') && !newUrl.startsWith('https://')) {
      newUrl = 'https://' + newUrl;
      backendUrlInput.value = newUrl;
    }

    chrome.storage.local.set({ scanvault_backend_url: newUrl }, async () => {
      currentBackendUrl = newUrl;
      showToast('Endpoint saved');
      settingsPanel.classList.add('hidden');
      await checkBackendHealth(newUrl, true);
    });
  });

  ocrLangSelect.addEventListener('change', () => {
    chrome.storage.local.set({ scanvault_ocr_lang: ocrLangSelect.value });
    showToast(`Language set to ${ocrLangSelect.options[ocrLangSelect.selectedIndex].text}`);
  });

  // --------------------------------------------------------------------------
  // 2. Navigation Tabs
  // --------------------------------------------------------------------------
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const tabId = `tab-${btn.dataset.tab}`;
      const targetTab = document.getElementById(tabId);
      if (targetTab) targetTab.classList.add('active');
    });
  });

  // Toast Helper
  let toastTimer = null;
  function showToast(message) {
    if (toastTimer) clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add('show');
    toastTimer = setTimeout(() => {
      toast.classList.remove('show');
    }, 2200);
  }

  // --------------------------------------------------------------------------
  // 3. OCR Engine (Images, PDFs & Base64)
  // --------------------------------------------------------------------------
  async function performOcr({ file, dataUrl }) {
    ocrStatusCard.classList.remove('hidden');
    ocrResultCard.classList.add('hidden');

    const selectedLang = ocrLangSelect.value || 'eng';

    if (file && file.name.toLowerCase().endsWith('.pdf')) {
      ocrStatusText.textContent = 'Working (analyzing PDF pages)...';
    } else {
      ocrStatusText.textContent = 'Working (extracting text)...';
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 25000);

    try {
      let response;
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('lang', selectedLang);
        response = await fetch(`${currentBackendUrl}/api/ocr`, {
          method: 'POST',
          body: formData,
          signal: controller.signal
        });
      } else if (dataUrl) {
        response = await fetch(`${currentBackendUrl}/api/ocr`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: dataUrl, lang: selectedLang }),
          signal: controller.signal
        });
      }
      clearTimeout(timeoutId);

      if (!response || !response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error || `Server error (${response ? response.status : 'offline'})`);
      }

      const result = await response.json();
      ocrResultCard.classList.remove('hidden');

      const cleanText = (result.text || '').trim();
      ocrOutputText.value = cleanText || '(No readable text detected)';

      const pages = result.pages || 1;
      const words = result.word_count !== undefined ? result.word_count : (cleanText ? cleanText.split(/\s+/).length : 0);
      const pageLabel = pages > 1 ? `${pages} pages • ` : '';
      ocrMetaInfo.textContent = `${pageLabel}${words} words`;

      showToast('Text extracted successfully');
    } catch (err) {
      clearTimeout(timeoutId);
      console.error('OCR Error:', err);
      const errMsg = err.name === 'AbortError' ? 'Timeout (Server busy)' : err.message;
      showToast(`Scan failed: ${errMsg}`);
      connectionPill.className = 'status-pill offline';
      connectionText.textContent = 'Offline';
    } finally {
      ocrStatusCard.classList.add('hidden');
      btnScanTab.disabled = false;
    }
  }

  // Scan Full Current Tab
  btnScanTab.addEventListener('click', () => {
    btnScanTab.disabled = true;
    ocrStatusText.textContent = 'Working...';
    ocrStatusCard.classList.remove('hidden');

    chrome.runtime.sendMessage({ action: 'CAPTURE_VISIBLE_TAB' }, (response) => {
      btnScanTab.disabled = false;
      if (response && response.success && response.dataUrl) {
        performOcr({ dataUrl: response.dataUrl });
      } else {
        ocrStatusCard.classList.add('hidden');
        showToast('Could not capture tab: ' + (response ? response.error : 'Permission error'));
      }
    });
  });

  // Snip Area Tool
  btnSnipArea.addEventListener('click', () => {
    const selectedLang = ocrLangSelect.value || 'eng';
    chrome.runtime.sendMessage({ action: 'START_AREA_SNIP', lang: selectedLang }, (response) => {
      if (response && response.error) {
        showToast(response.error);
      } else {
        showToast('✂️ Drag a box on page to snip');
        setTimeout(() => window.close(), 300);
      }
    });
  });

  // Pending snip crop check
  chrome.storage.local.get(['pending_snip'], (res) => {
    if (res.pending_snip && (Date.now() - res.pending_snip.timestamp < 30000)) {
      const { dataUrl, crop, lang } = res.pending_snip;
      chrome.storage.local.remove(['pending_snip']);

      const img = new Image();
      img.onload = () => {
        const ratio = crop.devicePixelRatio || 1;
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(crop.width * ratio);
        canvas.height = Math.round(crop.height * ratio);
        const ctx = canvas.getContext('2d');

        ctx.drawImage(
          img,
          Math.round(crop.x * ratio), Math.round(crop.y * ratio),
          Math.round(crop.width * ratio), Math.round(crop.height * ratio),
          0, 0, canvas.width, canvas.height
        );

        const croppedDataUrl = canvas.toDataURL('image/png');
        performOcr({ dataUrl: croppedDataUrl });
      };
      img.src = dataUrl;
    }
  });

  // Context Menu / Snip OCR check
  chrome.storage.local.get(['last_ocr_result'], (res) => {
    if (res.last_ocr_result) {
      ocrResultCard.classList.remove('hidden');
      ocrOutputText.value = res.last_ocr_result;
      const words = res.last_ocr_result.trim().split(/\s+/).length;
      ocrMetaInfo.textContent = `${words} words`;
    }
  });

  // Dropzone File Select
  ocrDropZone.addEventListener('click', () => ocrFileInput.click());
  ocrFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) performOcr({ file });
  });

  ['dragenter', 'dragover'].forEach(name => {
    ocrDropZone.addEventListener(name, (e) => {
      e.preventDefault();
      ocrDropZone.classList.add('drag-active');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    ocrDropZone.addEventListener(name, (e) => {
      e.preventDefault();
      ocrDropZone.classList.remove('drag-active');
    });
  });

  ocrDropZone.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
      const isImg = file.type.startsWith('image/');
      const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
      if (isImg || isPdf) {
        performOcr({ file });
      } else {
        showToast('Please drop an image or PDF file');
      }
    }
  });

  // Clipboard Paste
  document.addEventListener('paste', (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    for (const item of items) {
      if (item.type.indexOf('image') === 0) {
        const file = item.getAsFile();
        performOcr({ file });
        showToast('Pasted image from clipboard');
        break;
      }
    }
  });

  // OCR Action buttons
  btnCopyOcr.addEventListener('click', () => {
    if (!ocrOutputText.value) return;
    navigator.clipboard.writeText(ocrOutputText.value);
    showToast('Copied to clipboard');
  });

  btnDownloadOcr.addEventListener('click', () => {
    if (!ocrOutputText.value) return;
    const blob = new Blob([ocrOutputText.value], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `extracted_text_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Downloaded .txt');
  });

  btnClearOcr.addEventListener('click', () => {
    ocrOutputText.value = '';
    ocrResultCard.classList.add('hidden');
    ocrMetaInfo.textContent = '0 words';
    showToast('Cleared');
  });

  // --------------------------------------------------------------------------
  // 4. Post-Processing Tools
  // --------------------------------------------------------------------------
  btnCleanLines.addEventListener('click', () => {
    let txt = ocrOutputText.value;
    if (!txt) return;
    txt = txt.replace(/([^\n])\n([^\n])/g, '$1 $2').replace(/ +/g, ' ');
    ocrOutputText.value = txt.trim();
    showToast('Cleaned paragraphs');
  });

  btnFormatCsv.addEventListener('click', () => {
    let txt = ocrOutputText.value;
    if (!txt) return;
    const lines = txt.split('\n');
    const csvLines = lines.map(line => {
      const parts = line.split(/\s{2,}|\t/);
      return parts.map(p => `"${p.replace(/"/g, '""').trim()}"`).join(',');
    });
    ocrOutputText.value = csvLines.join('\n');
    showToast('Formatted as CSV');
  });

  btnFormatJson.addEventListener('click', () => {
    let txt = ocrOutputText.value;
    if (!txt) return;
    const lines = txt.split('\n').map(l => l.trim()).filter(Boolean);
    const jsonObj = {
      timestamp: new Date().toISOString(),
      total_lines: lines.length,
      lines: lines,
      full_text: txt
    };
    ocrOutputText.value = JSON.stringify(jsonObj, null, 2);
    showToast('Formatted as JSON');
  });

  // --------------------------------------------------------------------------
  // 5. PDF Hosting & QR Code Generator
  // --------------------------------------------------------------------------
  function formatBytes(bytes, decimals = 1) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  function loadRecentHistory() {
    chrome.storage.local.get(['scanvault_pdf_history'], (result) => {
      const list = result.scanvault_pdf_history || [];
      renderHistory(list);
    });
  }

  function saveToHistory(item) {
    chrome.storage.local.get(['scanvault_pdf_history'], (result) => {
      let list = result.scanvault_pdf_history || [];
      list.unshift(item);
      if (list.length > 8) list = list.slice(0, 8);
      chrome.storage.local.set({ scanvault_pdf_history: list }, () => {
        renderHistory(list);
      });
    });
  }

  function renderHistory(list) {
    historyList.innerHTML = '';
    if (!list || list.length === 0) {
      historyList.innerHTML = '<div class="history-empty">No hosted files yet</div>';
      return;
    }

    list.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'history-item';
      div.innerHTML = `
        <span class="name" title="${item.name}">${item.name}</span>
        <div class="actions">
          <button class="action-icon-btn copy-hist-btn" data-url="${item.url}" title="Copy Link">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
          </button>
          <a href="${item.url}" target="_blank" class="action-icon-btn" title="Open PDF">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
          </a>
        </div>
      `;
      historyList.appendChild(div);
    });

    historyList.querySelectorAll('.copy-hist-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        navigator.clipboard.writeText(btn.dataset.url);
        showToast('Link copied');
      });
    });
  }

  btnClearHistory.addEventListener('click', () => {
    chrome.storage.local.set({ scanvault_pdf_history: [] }, () => {
      renderHistory([]);
      showToast('History cleared');
    });
  });

  function renderQrCodeSvg(text, container) {
    container.innerHTML = '';
    const googleQrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=110x110&data=${encodeURIComponent(text)}`;
    const img = document.createElement('img');
    img.src = googleQrUrl;
    img.width = 110;
    img.height = 110;
    img.alt = "PDF QR Code";
    img.style.borderRadius = "4px";
    container.appendChild(img);
  }

  btnToggleQr.addEventListener('click', () => {
    qrContainer.classList.toggle('hidden');
    if (!qrContainer.classList.contains('hidden') && pdfShareUrl.value) {
      renderQrCodeSvg(pdfShareUrl.value, qrCodeDisplay);
    }
  });

  async function hostPdfFile(file) {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Please select a PDF file (.pdf)');
      return;
    }

    pdfDropZone.style.display = 'none';
    pdfUploadCard.classList.remove('hidden');
    pdfSuccessCard.classList.add('hidden');
    qrContainer.classList.add('hidden');
    pdfUploadStatus.textContent = 'Working (uploading file)...';

    try {
      const formData = new FormData();
      formData.append('file', file);

      const resp = await fetch(`${currentBackendUrl}/api/upload`, {
        method: 'POST',
        body: formData
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error || `Server error (${resp.status})`);
      }

      const result = await resp.json();

      pdfUploadCard.classList.add('hidden');
      pdfSuccessCard.classList.remove('hidden');

      pdfFilenameDisplay.textContent = file.name;
      pdfFilesizeDisplay.textContent = formatBytes(file.size);
      pdfShareUrl.value = result.share_url;
      pdfOpenLink.href = result.share_url;

      renderQrCodeSvg(result.share_url, qrCodeDisplay);

      saveToHistory({
        id: result.id,
        name: file.name,
        size: formatBytes(file.size),
        url: result.share_url,
        date: new Date().toLocaleDateString()
      });

      showToast('PDF hosted live');
    } catch (err) {
      console.error('PDF Upload Error:', err);
      pdfUploadCard.classList.add('hidden');
      pdfDropZone.style.display = 'block';
      showToast(`Upload failed: ${err.message}`);
    }
  }

  // PDF Dropzone events
  pdfDropZone.addEventListener('click', () => pdfFileInput.click());
  pdfFileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) hostPdfFile(e.target.files[0]);
  });

  ['dragenter', 'dragover'].forEach(name => {
    pdfDropZone.addEventListener(name, (e) => {
      e.preventDefault();
      pdfDropZone.classList.add('drag-active');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    pdfDropZone.addEventListener(name, (e) => {
      e.preventDefault();
      pdfDropZone.classList.remove('drag-active');
    });
  });

  pdfDropZone.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    if (file) hostPdfFile(file);
  });

  btnCopyPdf.addEventListener('click', () => {
    navigator.clipboard.writeText(pdfShareUrl.value);
    showToast('Link copied to clipboard');
  });

  btnHostAnother.addEventListener('click', () => {
    pdfSuccessCard.classList.add('hidden');
    pdfDropZone.style.display = 'block';
    pdfFileInput.value = '';
  });

  // Initial Load
  await loadConfig();
  await checkBackendHealth();
  loadRecentHistory();
});

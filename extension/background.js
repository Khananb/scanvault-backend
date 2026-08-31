// ScanVault Chrome Extension - Background Service Worker

const DEFAULT_BACKEND_URL = 'https://scanvault-backend-2.onrender.com';

async function getBackendUrl() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['scanvault_backend_url'], (res) => {
      let url = res.scanvault_backend_url;
      if (!url || url.includes('scanvault-backend.onrender.com') || url.includes('scanvault-backend-1.onrender.com')) {
        url = DEFAULT_BACKEND_URL;
        chrome.storage.local.set({ scanvault_backend_url: DEFAULT_BACKEND_URL });
      }
      resolve(url.replace(/\/+$/, ''));
    });
  });
}

// --------------------------------------------------------------------------
// 1. Context Menus Setup
// --------------------------------------------------------------------------
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'scanvault_ocr_image',
    title: 'Extract Text with ScanVault',
    contexts: ['image']
  });

  chrome.contextMenus.create({
    id: 'scanvault_host_pdf',
    title: 'Host PDF with ScanVault',
    contexts: ['link']
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const backendUrl = await getBackendUrl();

  if (info.menuItemId === 'scanvault_ocr_image' && info.srcUrl) {
    showNotification('ScanVault OCR', 'Analyzing image text...');
    try {
      const resp = await fetch(`${backendUrl}/api/ocr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: info.srcUrl, lang: 'eng' })
      });
      const res = await resp.json();
      if (res.success && res.text) {
        chrome.storage.local.set({ last_ocr_result: res.text });
        showNotification('ScanVault OCR', `Extracted (${res.word_count} words):\n${res.text.slice(0, 100)}...`);
      } else {
        showNotification('ScanVault Error', res.error || 'No text recognized');
      }
    } catch (err) {
      showNotification('ScanVault Error', `Failed to connect: ${err.message}`);
    }
  }

  if (info.menuItemId === 'scanvault_host_pdf' && info.linkUrl) {
    showNotification('ScanVault PDF Host', 'Hosting PDF document...');
    try {
      const resp = await fetch(`${backendUrl}/api/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pdf_url: info.linkUrl })
      });
      const res = await resp.json();
      if (res.success && res.share_url) {
        showNotification('ScanVault PDF Hosted!', `Link: ${res.share_url}`);
      } else {
        showNotification('ScanVault Error', res.error || 'Upload failed');
      }
    } catch (err) {
      showNotification('ScanVault Error', `Failed to connect: ${err.message}`);
    }
  }
});

function showNotification(title, message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon48.png',
    title: title,
    message: message,
    priority: 2
  });
}

// --------------------------------------------------------------------------
// 2. Messaging & Tab Snipping Engine
// --------------------------------------------------------------------------
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'GET_BACKEND_URL') {
    getBackendUrl().then((url) => sendResponse({ backendUrl: url }));
    return true;
  }

  if (request.action === 'CAPTURE_VISIBLE_TAB') {
    chrome.tabs.captureVisibleTab(null, { format: 'png' }, (dataUrl) => {
      if (chrome.runtime.lastError) {
        sendResponse({ success: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ success: true, dataUrl: dataUrl });
      }
    });
    return true;
  }

  if (request.action === 'START_AREA_SNIP') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0] && tabs[0].id) {
        const url = tabs[0].url || '';
        if (url.startsWith('chrome://') || url.startsWith('edge://') || url.startsWith('chrome-extension://') || url.startsWith('about:')) {
          sendResponse({ success: false, error: 'Cannot snip system/restricted pages. Please switch to a regular website (e.g. google.com).' });
          return;
        }

        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          files: ['content_script.js']
        }, () => {
          if (chrome.runtime.lastError) {
            sendResponse({ success: false, error: chrome.runtime.lastError.message });
          } else {
            chrome.tabs.sendMessage(tabs[0].id, { action: 'START_AREA_SNIP', lang: request.lang || 'eng' });
            sendResponse({ success: true });
          }
        });
      } else {
        sendResponse({ success: false, error: 'No active tab found' });
      }
    });
    return true;
  }

  if (request.action === 'AREA_SNIP_CAPTURED') {
    const crop = request.crop;
    const lang = request.lang || 'eng';
    chrome.tabs.captureVisibleTab(null, { format: 'png' }, (fullDataUrl) => {
      if (!fullDataUrl) {
        if (sender.tab && sender.tab.id) {
          chrome.tabs.sendMessage(sender.tab.id, { action: 'SNIP_ERROR', error: 'Failed to capture screen.' });
        }
        return;
      }
      
      // Store in local storage for popup
      chrome.storage.local.set({
        pending_snip: {
          dataUrl: fullDataUrl,
          crop: crop,
          lang: lang,
          timestamp: Date.now()
        }
      });

      // Send captured tab back to content script to crop & display result immediately on page
      if (sender.tab && sender.tab.id) {
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'PROCESS_SNIP_IMAGE',
          dataUrl: fullDataUrl,
          crop: crop,
          lang: lang
        });
      }
    });
    return true;
  }

  if (request.action === 'SHOW_NOTIFICATION') {
    showNotification(request.title || 'ScanVault', request.message || '');
  }
});

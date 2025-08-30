// Background script for Contextual Database Extension

// Set up extension on installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
  
  // Create context menu for search only
  // Quick guide menu
  chrome.contextMenus.create({
    id: 'open-quick-guide',
    title: 'Quick Guide',
    contexts: ['page', 'action']
  });
});

// Handle extension icon click (action click)
chrome.action.onClicked.addListener(async () => {
  
  // Check authentication
  const storage = await chrome.storage.local.get(['access_token', 'refresh_token']);
  const isAuthenticated = Boolean(storage.refresh_token || storage.access_token);

  if (!isAuthenticated) {
    await chrome.tabs.create({
      url: chrome.runtime.getURL('signup.html'),
    });
    return;
  }

  // Save page immediately
  await handleSingleClick();
});

// Handle context menu clicks (search only)
chrome.contextMenus.onClicked.addListener(async (info) => {
  // Open quick guide without auth requirement
  if (info.menuItemId === 'open-quick-guide') {
    await chrome.tabs.create({ url: chrome.runtime.getURL('quick-guide.html') });
    return;
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {

  if (message.action === 'EXTRACT_PAGE_CONTENT') {
    // Forward content extraction requests to the active tab
    chrome.tabs.query({ active: true, currentWindow: true }).then(tabs => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, message).then(response => {
          sendResponse(response);
        }).catch(error => {
          sendResponse({ success: false, error: error.message });
        });
      } else {
        sendResponse({ success: false, error: 'No active tab found' });
      }
    });
    return true; 
  }
});

async function handleSingleClick() {
  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) {
      return;
    }

    // Show immediate "Saving..." popup
    chrome.tabs.sendMessage(tab.id, {
      action: 'SHOW_SAVING_POPUP'
    }).catch(() => {
      console.log('Could not show saving popup');
    });

    // Update popup with extraction status
    chrome.tabs.sendMessage(tab.id, {
      action: 'UPDATE_SAVING_POPUP',
      status: 'Extracting webpage content...'
    }).catch(() => {});

    // Extract content from the page
    const response = await chrome.tabs.sendMessage(tab.id, { 
      action: 'EXTRACT_PAGE_CONTENT' 
    });

    if (!response?.success || !response?.data) {
      throw new Error('Failed to extract content from page');
    }

    const data = response.data;

    // Update popup with processing status
    chrome.tabs.sendMessage(tab.id, {
      action: 'UPDATE_SAVING_POPUP',
      status: `Processing "${data.title}" (${data.wordCount.toLocaleString()} words)...`
    }).catch(() => {});

    const storage = await chrome.storage.local.get(['access_token', 'refresh_token', 'user']);

    // Update popup with upload status
    chrome.tabs.sendMessage(tab.id, {
      action: 'UPDATE_SAVING_POPUP',
      status: 'Uploading to ContextDB...'
    }).catch(() => {});

    await saveToContextualDB({
      user_id: storage.user.id,
      url: data.url,
      title: data.title,
      contenthtml: data.content,
    });

    // Show final success popup
    chrome.tabs.sendMessage(tab.id, {
      action: 'SHOW_SAVE_POPUP',
      data: {
        title: data.title,
        wordCount: data.wordCount
      }
    }).catch(error => {
      console.log('Could not show success popup:', error);
    });
    

  } catch (error) {
    console.error('❌ Content extraction failed:', error);
    
    // Show error popup on the current tab
    const [currentTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (currentTab?.id) {
      chrome.tabs.sendMessage(currentTab.id, {
        action: 'SHOW_ERROR_POPUP',
        error: error instanceof Error ? error.message : 'Please refresh the page and try again.'
      }).catch(err => {
        console.log('Could not show error popup:', err);
      });
    }
  }
}

interface CleanedDataPayload {
  user_id: string;
  title?: string;
  url?: string;
  contenthtml?: string;
}

async function saveToContextualDB(cleanedData: CleanedDataPayload) {
  const formData = new FormData();
  
  formData.append('user_id', cleanedData.user_id);

  const fileName = createFilenameFromMeta(cleanedData.title);
  formData.append('file_name', fileName);
  
  const htmlBlob = new Blob([cleanedData.contenthtml || ''], { type: 'text/html' });
  formData.append('contenthtml', htmlBlob, fileName);
  
  // Include auth header if available
  const { access_token } = await chrome.storage.local.get(['access_token']);

  const response = await fetch('https://aci-contextualdb.onrender.com/ingest', {
    method: 'POST',
    headers: access_token ? { 'Authorization': `Bearer ${access_token}` } : {},
    body: formData
  });
  
  console.log(response);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
}

function createFilenameFromMeta(title?: string, url?: string): string {
  const base = (title && title.trim().length > 0) ? title : (url || 'page');
  // Replace invalid filename characters and slashes, collapse spaces, trim
  let safe = base
    .replace(/https?:\/\//gi, '')
    .replace(/[^a-zA-Z0-9\s._-]/g, '-')
    .replace(/[\s/\\]+/g, '-')
    .replace(/-+/g, '-')
    .trim();

  if (safe.length === 0) safe = 'page';

  // Limit length reasonably
  if (safe.length > 80) safe = safe.substring(0, 80);

  // Ensure .html extension
  if (!safe.toLowerCase().endsWith('.html')) safe += '.html';

  return safe;
}
// Content script runs in the context of web pages
// This provides enhanced DOM access and real-time webpage interaction

import { Readability } from '@mozilla/readability';

// Types for message passing
interface ExtractedData {
  title: string;
  content: string;
  textContent: string;
  url: string;
  domain: string;
  wordCount: number;
  timestamp: string;
  metadata: {
    description?: string;
    keywords?: string;
    author?: string;
    publishedTime?: string;
    modifiedTime?: string;
    lang?: string;
    canonical?: string;
    readabilityScore?: number;
    extractionMethod?: string;
    contentQuality?: string;
  };
}

// Listen for messages from popup or background script
chrome.runtime.onMessage.addListener(
  (
    message: any,
    _sender: chrome.runtime.MessageSender,
    sendResponse: (response: any) => void
  ) => {
    if (message.action === 'EXTRACT_PAGE_CONTENT') {
      try {
        const extractedData = extractPageContent();
        sendResponse({ success: true, data: extractedData });
      } catch (error) {
        console.error('Content extraction failed:', error);
        sendResponse({
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    }
    
    if (message.action === 'SHOW_SAVING_POPUP') {
      showSavingPopup();
    }
    
    if (message.action === 'UPDATE_SAVING_POPUP') {
      updateSavingPopup(message.status);
    }
    
    if (message.action === 'SHOW_SAVE_POPUP') {
      showSavePopup(message.data);
    }
    
    if (message.action === 'SHOW_ERROR_POPUP') {
      showErrorPopup(message.error);
    }
    
    return true; // Keep message channel open
  }
);

// Main content extraction function
function extractPageContent(): ExtractedData {
  const url = window.location.href;
  const domain = window.location.hostname;
  const title = document.title;
  
  // Clone document for Readability (it modifies the DOM)
  const documentClone = document.cloneNode(true) as Document;
  
  // Extract clean content using Readability with optimized settings
  const reader = new Readability(documentClone, {
    charThreshold: 300,        // Lower threshold to catch more content
    classesToPreserve: ['highlight', 'code', 'pre', 'code-block', 'formula', 'math'],
    keepClasses: true,         // Preserve important CSS classes
    debug: false               // Set to true for debugging
  });
  
  const article = reader.parse();
  
  let content = '';
  let textContent = '';
  let readabilityScore = 0;
  let extractionMethod = 'fallback';
  
  if (article) {
    content = article.content || '';
    textContent = article.textContent || '';
    readabilityScore = article.length || 0;
    extractionMethod = 'mozilla-readability';
    
    console.log('Mozilla Readability Success:', {
      title: article.title,
      length: article.length,
      excerpt: article.excerpt?.substring(0, 100)
    });
  } else {
    // Fallback extraction method
    console.log('Mozilla Readability failed, using fallback extraction');
    const fallbackContent = extractFallbackContent();
    content = fallbackContent.html;
    textContent = fallbackContent.text;
    extractionMethod = 'dom-fallback';
  }
  
  // Extract page metadata
  const metadata = extractPageMetadata();
  
  // Calculate word count
  const wordCount = textContent.split(/\s+/).filter(word => word.length > 0).length;
  
  return {
    title,
    content: content.substring(0, 15000), // Reasonable content limit
    textContent: textContent.substring(0, 15000),
    url,
    domain,
    wordCount,
    timestamp: new Date().toISOString(),
    metadata: {
      ...metadata,
      readabilityScore,
      extractionMethod,
      contentQuality: readabilityScore > 500 ? 'high' : readabilityScore > 200 ? 'medium' : 'low'
    }
  };
}

// Fallback content extraction for pages where Readability fails
function extractFallbackContent(): { html: string; text: string } {
  // Remove unwanted elements
  const unwantedSelectors = [
    'script', 'style', 'nav', 'header', 'footer', 'aside',
    '.advertisement', '.ads', '.social-share', '.comments',
    '[class*="sidebar"]', '[class*="menu"]', '[class*="nav"]'
  ];
  
  const clone = document.body.cloneNode(true) as HTMLElement;
  
  unwantedSelectors.forEach(selector => {
    const elements = clone.querySelectorAll(selector);
    elements.forEach(el => el.remove());
  });
  
  // Try to find main content area
  const contentSelectors = [
    'main', 'article', '[role="main"]',
    '.content', '#content', '.post', '.entry',
    '.article', '.story', '.news-article'
  ];
  
  let contentElement = null;
  
  for (const selector of contentSelectors) {
    contentElement = clone.querySelector(selector);
    if (contentElement) break;
  }
  
  // If no specific content area found, use the cleaned body
  const targetElement = contentElement || clone;
  
  return {
    html: targetElement.innerHTML || '',
    text: targetElement.textContent?.trim() || ''
  };
}

// Extract page metadata from meta tags and structured data
function extractPageMetadata() {
  const metadata: any = {};
  
  // Standard meta tags
  const metaDescription = document.querySelector('meta[name="description"]') as HTMLMetaElement;
  if (metaDescription) metadata.description = metaDescription.content;
  
  const metaKeywords = document.querySelector('meta[name="keywords"]') as HTMLMetaElement;
  if (metaKeywords) metadata.keywords = metaKeywords.content;
  
  const metaAuthor = document.querySelector('meta[name="author"]') as HTMLMetaElement;
  if (metaAuthor) metadata.author = metaAuthor.content;
  
  // Open Graph meta tags
  const ogDescription = document.querySelector('meta[property="og:description"]') as HTMLMetaElement;
  if (ogDescription) metadata.description = metadata.description || ogDescription.content;
  
  // Article meta tags
  const publishedTime = document.querySelector('meta[property="article:published_time"]') as HTMLMetaElement;
  if (publishedTime) metadata.publishedTime = publishedTime.content;
  
  const modifiedTime = document.querySelector('meta[property="article:modified_time"]') as HTMLMetaElement;
  if (modifiedTime) metadata.modifiedTime = modifiedTime.content;
  
  // Language
  const htmlLang = document.documentElement.lang;
  if (htmlLang) metadata.lang = htmlLang;
  
  // Canonical URL
  const canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
  if (canonical) metadata.canonical = canonical.href;
  
  return metadata;
}

// Enhanced page readiness detection
function isPageReady(): boolean {
  return document.readyState === 'complete' && 
         document.body !== null && 
         document.body.children.length > 0;
}

// Content script is now simplified - no more Ctrl key tracking needed!

// Wait for page to be fully loaded before making content available
if (!isPageReady()) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      console.log('Contextual Database content script ready');
    });
  } else {
    // Document is already loaded
    console.log('Contextual Database content script ready');
  }
} else {
  console.log('Contextual Database content script ready');
}

// Popup notification functions
function showSavingPopup() {
  createNotificationPopup({
    type: 'loading',
    title: 'Saving Content...',
    message: 'Extracting webpage content and preparing for upload',
    persistent: true
  });
}

function updateSavingPopup(status: string) {
  updateNotificationPopup({
    type: 'loading',
    title: 'Saving Content...',
    message: status,
    persistent: true
  });
}

function showSavePopup(data: any) {
  updateNotificationPopup({
    type: 'success',
    title: 'Content Saved Successfully!',
    message: `Saved "${data.title}" (${data.wordCount.toLocaleString()} words) to ContextDB`,
    persistent: false
  });
}

function showErrorPopup(error: string) {
  updateNotificationPopup({
    type: 'error',
    title: 'Failed to Save Content',
    message: error || 'Please refresh the page and try again.',
    persistent: false
  });
}

interface NotificationOptions {
  type: 'success' | 'error' | 'info' | 'loading';
  title: string;
  message: string;
  duration?: number;
  persistent?: boolean;
}

function updateNotificationPopup(options: NotificationOptions) {
  const existingNotification = document.querySelector('#contextdb-notification');
  if (existingNotification) {
    // Update existing notification
    updateExistingNotification(existingNotification, options);
  } else {
    // Create new notification
    createNotificationPopup(options);
  }
}

function createNotificationPopup(options: NotificationOptions) {
  // Remove any existing notifications
  const existingNotification = document.querySelector('#contextdb-notification');
  if (existingNotification) {
    existingNotification.remove();
  }

  const duration = options.persistent ? 0 : (options.duration || 5000);

  // Create notification container
  const notification = document.createElement('div');
  notification.id = 'contextdb-notification';
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    width: 380px;
    background: #171717;
    border: 1px solid #262626;
    border-radius: 12px;
    box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.5);
    z-index: 2147483647;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
    color: #fafafa;
    overflow: hidden;
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
    opacity: 0;
  `;

  // Create header with icon and close button
  const header = document.createElement('div');
  header.style.cssText = `
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 16px 8px 16px;
  `;

  const leftSection = document.createElement('div');
  leftSection.style.cssText = `
    display: flex;
    align-items: center;
    gap: 12px;
  `;

  // Create icon
  const iconElement = document.createElement('div');
  iconElement.style.cssText = `
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  `;

  if (options.type === 'success') {
    iconElement.style.backgroundColor = '#34d399';
    iconElement.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
        <polyline points="20,6 9,17 4,12"/>
      </svg>
    `;
  } else if (options.type === 'error') {
    iconElement.style.backgroundColor = '#ef4444';
    iconElement.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    `;
  } else if (options.type === 'loading') {
    iconElement.style.backgroundColor = '#34d399';
    iconElement.innerHTML = `
      <div style="
        width: 14px; 
        height: 14px; 
        border: 2px solid rgba(255,255,255,0.3); 
        border-top: 2px solid white; 
        border-radius: 50%; 
        animation: spin 1s linear infinite;
      "></div>
    `;
    
    // Add spinning animation if not already present
    if (!document.getElementById('contextdb-spin-animation')) {
      const style = document.createElement('style');
      style.id = 'contextdb-spin-animation';
      style.innerHTML = `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
      document.head.appendChild(style);
    }
  }

  const title = document.createElement('h3');
  title.textContent = options.title;
  title.style.cssText = `
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #fafafa;
  `;

  leftSection.appendChild(iconElement);
  leftSection.appendChild(title);

  // Create close button
  const closeButton = document.createElement('button');
  closeButton.style.cssText = `
    background: none;
    border: none;
    color: #a3a3a3;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: color 0.2s ease;
  `;
  closeButton.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  `;

  closeButton.addEventListener('mouseenter', () => {
    closeButton.style.color = '#fafafa';
  });
  closeButton.addEventListener('mouseleave', () => {
    closeButton.style.color = '#a3a3a3';
  });

  closeButton.addEventListener('click', () => {
    dismissNotification();
  });

  header.appendChild(leftSection);
  header.appendChild(closeButton);

  // Create message content
  const messageElement = document.createElement('p');
  messageElement.textContent = options.message;
  messageElement.style.cssText = `
    margin: 0;
    padding: 0 16px 16px 52px;
    font-size: 14px;
    line-height: 1.5;
    color: #d4d4d8;
  `;

  // Create progress bar for auto-dismiss (only if not persistent)
  let progressBar = null;
  if (!options.persistent && duration > 0) {
    progressBar = document.createElement('div');
    progressBar.style.cssText = `
      position: absolute;
      bottom: 0;
      left: 0;
      height: 3px;
      background: ${options.type === 'success' ? '#34d399' : options.type === 'error' ? '#ef4444' : '#34d399'};
      width: 100%;
      transform-origin: left;
      transform: scaleX(1);
      transition: transform ${duration}ms linear;
    `;
  }

  // Assemble notification
  notification.appendChild(header);
  notification.appendChild(messageElement);
  if (progressBar) {
    notification.appendChild(progressBar);
  }

  // Add to page
  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
    notification.style.opacity = '1';
  }, 100);

  let dismissTimeout: NodeJS.Timeout | undefined;
  
  // Start progress bar animation and auto-dismiss only for non-persistent notifications
  if (progressBar && duration > 0) {
    setTimeout(() => {
      progressBar.style.transform = 'scaleX(0)';
    }, 200);

    // Auto dismiss
    dismissTimeout = setTimeout(() => {
      dismissNotification();
    }, duration);
  }

  function dismissNotification() {
    if (dismissTimeout) {
      clearTimeout(dismissTimeout);
    }
    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';
    
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 300);
  }

  // Pause auto-dismiss on hover (only for non-persistent notifications)
  if (progressBar && !options.persistent) {
    notification.addEventListener('mouseenter', () => {
      if (progressBar) {
        progressBar.style.animationPlayState = 'paused';
        progressBar.style.transitionDuration = '0s';
      }
    });

    notification.addEventListener('mouseleave', () => {
      if (progressBar) {
        progressBar.style.animationPlayState = 'running';
        progressBar.style.transitionDuration = `${duration}ms`;
      }
    });
  }
}

function updateExistingNotification(notification: Element, options: NotificationOptions) {
  // Update icon
  const iconElement = notification.querySelector('div[style*="border-radius: 50%"]');
  if (iconElement) {
    const icon = iconElement as HTMLElement;
    if (options.type === 'success') {
      icon.style.backgroundColor = '#34d399';
      icon.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
          <polyline points="20,6 9,17 4,12"/>
        </svg>
      `;
    } else if (options.type === 'error') {
      icon.style.backgroundColor = '#ef4444';
      icon.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      `;
    } else if (options.type === 'loading') {
      icon.style.backgroundColor = '#34d399';
      icon.innerHTML = `
        <div style="
          width: 14px; 
          height: 14px; 
          border: 2px solid rgba(255,255,255,0.3); 
          border-top: 2px solid white; 
          border-radius: 50%; 
          animation: spin 1s linear infinite;
        "></div>
      `;
    }
  }
  
  // Update title
  const titleElement = notification.querySelector('h3');
  if (titleElement) {
    titleElement.textContent = options.title;
  }
  
  // Update message
  const messageElement = notification.querySelector('p');
  if (messageElement) {
    messageElement.textContent = options.message;
  }
  
  // Handle progress bar for final states
  if (!options.persistent) {
    const duration = options.duration || 5000;
    const existingProgressBar = notification.querySelector('div[style*="position: absolute"]');
    
    if (!existingProgressBar) {
      // Add progress bar for final state
      const progressBar = document.createElement('div');
      progressBar.style.cssText = `
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: ${options.type === 'success' ? '#34d399' : '#ef4444'};
        width: 100%;
        transform-origin: left;
        transform: scaleX(1);
        transition: transform ${duration}ms linear;
      `;
      
      notification.appendChild(progressBar);
      
      // Start progress bar animation
      setTimeout(() => {
        progressBar.style.transform = 'scaleX(0)';
      }, 100);
      
      // Auto dismiss
      setTimeout(() => {
        notification.remove();
      }, duration);
    }
  }
}
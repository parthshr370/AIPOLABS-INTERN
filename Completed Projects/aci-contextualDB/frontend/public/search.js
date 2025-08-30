document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const status = document.getElementById('status');
    const resultsSection = document.getElementById('resultsSection');
    const resultsList = document.getElementById('resultsList');
    const resultsCount = document.getElementById('resultsCount');
    const emptyState = document.getElementById('emptyState');
    const searchSection = document.querySelector('.search-section');

    // Auth gate initialization
    initAuthGate();

    // Search on button click or Enter key
    searchButton.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    async function handleSearch() {
        const query = searchInput.value.trim();
        
        if (!query) {
            showStatus('Please enter a search query', 'error');
            return;
        }

        // Show loading state
        searchButton.disabled = true;
        showStatus('Searching your content...', 'info');
        hideResults();

        try {
            const results = await performSearch(query);
            displayResults(results, query);
        } catch (error) {
            console.error('Search failed:', error);
            showStatus(error?.message || 'Unexpected error. Please try again.', 'error');
        } finally {
            searchButton.disabled = false;
        }
    }

    async function initAuthGate() {
        try {
            const storage = await chrome.storage.local.get(['access_token', 'refresh_token', 'user']);
            const isAuthenticated = Boolean(storage.refresh_token || storage.access_token);

            if (!isAuthenticated) {
                // Disable search UI
                if (searchInput) searchInput.disabled = true;
                if (searchButton) searchButton.disabled = true;
                if (searchSection) searchSection.style.display = 'none';

                // Show auth required message
                resultsSection.style.display = 'none';
                emptyState.style.display = 'flex';
                emptyState.innerHTML = `
                    <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 16v-4"/>
                        <path d="M12 8h.01"/>
                    </svg>
                    <h3>Sign in required</h3>
                    <p>You need to sign in to search your saved content. Click below to continue.</p>
                    <button id="openSignup" class="cta-button">Sign in</button>
                `;

                const btn = emptyState.querySelector('#openSignup');
                if (btn) {
                    btn.addEventListener('click', async () => {
                        await chrome.tabs.create({ url: chrome.runtime.getURL('signup.html') });
                    });
                }

                showStatus('Please sign in to use search', 'info');
            }
        } catch (e) {
            // If chrome APIs are unavailable, do nothing
        }
    }

    async function performSearch(query) {
        try {
            // Get user authentication from Chrome storage
            const storage = await chrome.storage.local.get(['access_token', 'user']);
            
            if (!storage.access_token || !storage.user) {
                throw new Error('User not authenticated');
            }

            // Build URL with query parameters
            const url = new URL('https://aci-contextualdb.onrender.com/search');
            url.searchParams.append('query', query);
            url.searchParams.append('user_id', storage.user.id);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${storage.access_token}`
                }
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            return data.results || [];
        } catch (error) {
            console.error('Search API call failed:', error);
            throw new Error('Unexpected error. Please try again.');
        }
    }

    // Delete context from ContextDB
    async function deleteContext(contextId) {
        // Get auth and user
        const storage = await chrome.storage.local.get(['access_token', 'user']);
        if (!storage.access_token || !storage.user?.id) {
            throw new Error('User not authenticated');
        }

        const url = new URL('https://aci-contextualdb.onrender.com/context');
        url.searchParams.set('context_id', contextId);
        url.searchParams.set('user_id', storage.user.id);

        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${storage.access_token}`
            }
        });

        if (!response.ok) {
            const text = await response.text().catch(() => '');
            throw new Error(`Delete failed: ${response.status} ${response.statusText}${text ? ` - ${text}` : ''}`);
        }

        return true;
    }

    // Note: intentionally no dummy fallback. Errors surface via showStatus in handleSearch.

    function displayResults(results, query) {
        hideStatus();
        
        if (results.length === 0) {
            showNoResults(query);
            return;
        }

        // Show results section
        resultsSection.style.display = 'block';
        emptyState.style.display = 'none';
        
        // Update results count
        resultsCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''} found`;

        // Render results - updated for backend API response format
        resultsList.innerHTML = results.map((result, i) => {
            const asset = result.asset || {};
            const titleFromFilename = asset.original_filename || asset.uploaded_filename || null;
            const titleFromUrl = (() => {
                if (!asset.source_url) return null;
                try { return new URL(asset.source_url).hostname; } catch (_) { return asset.source_url; }
            })();
            const title = titleFromFilename || titleFromUrl || result.source || 'Document';
            const snippet = result.content || result.snippet || 'No content available';
            const scorePct = typeof result.relevance_score === 'number' ? Math.round(result.relevance_score * 100) : 'N/A';
            const ctxId = result.id || result.context_id;

            return `
            <div class="result-item">
                <div class="result-title">${highlightQuery(title, query)}</div>
                <div class="result-snippet">${highlightQuery(snippet, query)}</div>
                <div class="raw-html-toggle" style="margin: 6px 0;">
                    <button class="toggle-raw" data-idx="${i}" title="Show raw HTML">View HTML</button>
                </div>
                <div class="raw-html-container" data-idx="${i}" style="display:none; border: 1px solid var(--border); background: var(--muted); padding: 8px; border-radius: 6px; max-height: 240px; overflow: auto;">
                    <pre class="raw-html" style="white-space: pre-wrap; word-wrap: break-word;"></pre>
                </div>
                <div class="result-meta">
                    <span class="meta-spacer"></span>
                    <span class="result-score">${scorePct}% match</span>
                    <button class="copy-context" data-idx="${i}" title="Copy context for LLM">Copy context</button>
                    ${ctxId ? `<button class="delete-context" data-id="${ctxId}" title="Delete this context">Delete</button>` : ''}
                </div>
            </div>`;
        }).join('');

        // Wire up copy-context buttons
        const contextButtons = resultsList.querySelectorAll('.copy-context');
        contextButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const idx = parseInt(btn.getAttribute('data-idx'), 10);
                if (Number.isNaN(idx) || !results[idx]) return;
                const r = results[idx];
                const asset = r.asset || {};
                const title = (asset.original_filename || asset.uploaded_filename || r.source || 'Document');
                const sourceUrl = asset.source_url || '';
                const snippet = r.content || r.snippet || '';

                const copyBlock = [
                    title ? `Title: ${title}` : null,
                    sourceUrl ? `Source: ${sourceUrl}` : null,
                    '---',
                    snippet
                ].filter(Boolean).join('\n');

                try {
                    await navigator.clipboard.writeText(copyBlock);
                    btn.textContent = 'Copied!';
                    setTimeout(() => { btn.textContent = 'Copy context'; }, 1200);
                } catch (err) {
                    // Fallback for environments without Clipboard API permissions
                    const temp = document.createElement('textarea');
                    temp.value = copyBlock;
                    document.body.appendChild(temp);
                    temp.select();
                    document.execCommand('copy');
                    document.body.removeChild(temp);
                    btn.textContent = 'Copied!';
                    setTimeout(() => { btn.textContent = 'Copy context'; }, 1200);
                }
            });
        });

        // Wire up delete-context buttons
        const deleteButtons = resultsList.querySelectorAll('.delete-context');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const contextId = btn.getAttribute('data-id');
                if (!contextId) return;

                const confirmed = window.confirm('Delete this context? This action cannot be undone.');
                if (!confirmed) return;

                const originalText = btn.textContent;
                btn.disabled = true;
                btn.textContent = 'Deleting...';
                try {
                    await deleteContext(contextId);
                    btn.textContent = 'Deleted';
                    // Refresh results to reflect deletion
                    setTimeout(() => { handleSearch(); }, 300);
                } catch (err) {
                    btn.disabled = false;
                    btn.textContent = originalText;
                    showStatus(err?.message || 'Failed to delete context', 'error');
                }
            });
        });

        // Wire up toggle raw HTML buttons
        const toggleButtons = resultsList.querySelectorAll('.toggle-raw');
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = btn.getAttribute('data-idx');
                if (idx == null) return;
                const container = resultsList.querySelector(`.raw-html-container[data-idx="${idx}"]`);
                const pre = container ? container.querySelector('.raw-html') : null;
                if (!container || !pre) return;

                // Simple logging to trace UI behavior
                console.log('Toggling raw HTML for result index:', idx);

                if (container.style.display === 'none') {
                    const r = results[Number(idx)] || {};
                    const raw = r.raw_html || 'No raw HTML available';
                    // Do not set innerHTML to avoid executing scripts; use textContent
                    pre.textContent = raw;
                    container.style.display = 'block';
                    btn.textContent = 'Hide HTML';
                } else {
                    container.style.display = 'none';
                    btn.textContent = 'View HTML';
                }
            });
        });
    }

    function showNoResults(query) {
        resultsSection.style.display = 'none';
        emptyState.style.display = 'flex';
        emptyState.innerHTML = `
            <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
            </svg>
            <h3>No Results Found</h3>
                <p>No content found for "${(String(query)
                .replace(/&/g,'&amp;')
                .replace(/</g,'&lt;')
                .replace(/>/g,'&gt;')
                .replace(/"/g,'&quot;')
                .replace(/'/g,'&#39;')
                .replace(/`/g,'&#96;'))}". Try a different search term or save more content first.</p>
            <p>If you're sure you've saved content, try refreshing the page.</p>
        `;
    }

    function highlightQuery(text, query) {
        const escHtml = (s) => String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/`/g, '&#96;');
        const escRe = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const safeText = escHtml(text ?? '');
        const q = escRe(query ?? '');
        if (!q) return safeText;
        const re = new RegExp(`(${q})`, 'gi');
        return safeText.replace(re, '<strong style="background: var(--primary); color: var(--primary-foreground); padding: 1px 3px; border-radius: 2px;">$1</strong>');
    }

    function showStatus(message, type) {
        let icon = '';
        switch(type) {
            case 'info':
                icon = '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>';
                break;
            case 'success':
                icon = '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22,4 12,14.01 9,11.01"/></svg>';
                break;
            case 'error':
                icon = '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';
                break;
        }
        status.innerHTML = icon + '<span>' + message + '</span>';
        status.className = `status ${type}`;
        status.style.display = 'flex';
    }

    function hideStatus() {
        status.style.display = 'none';
    }

    function hideResults() {
        resultsSection.style.display = 'none';
        emptyState.style.display = 'flex';
    }
});
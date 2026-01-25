(function () {
    'use strict';

    var SUPABASE_URL = 'https://ydwjzlikslebokuxzwco.supabase.co';
    var SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU';

    var supabaseClient;
    var allProjects = [];
    var currentFilter = 'all';

    var AUTO_REFRESH_INTERVAL = 60000;

    function init() {
        waitForSupabase(function () {
            supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
            loadProjects();
            setupEventListeners();
            updateGlobalTime();

            setInterval(function () {
                loadProjects();
                updateGlobalTime();
            }, AUTO_REFRESH_INTERVAL);
        });
    }

    function updateGlobalTime() {
        var now = new Date();
        var timeStr = now.toLocaleDateString() + ' ' + now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const el = document.getElementById('globalTimestamp');
        if (el) el.innerHTML = 'LAST UPDATE: ' + timeStr;
    }

    function waitForSupabase(callback) {
        var attempts = 0;
        var maxAttempts = 50;
        function check() {
            if (window.supabase && window.supabase.createClient) {
                callback();
            } else if (attempts < maxAttempts) {
                attempts++;
                setTimeout(check, 100);
            } else {
                document.getElementById('projectsGrid').innerHTML =
                    '<div style="text-align:center; padding:40px; color:var(--neon-red);">SYSTEM ERROR: Supabase connection failed</div>';
            }
        }
        check();
    }

    function loadProjects() {
        const grid = document.getElementById('projectsGrid');
        if (allProjects.length === 0) {
            grid.innerHTML = '<div style="padding:40px; color:var(--text-dim); text-align:center;">SCANNING SECTOR...</div>';
        }

        supabaseClient
            .from('claude_projects')
            .select('*')
            .order('updated_at', { ascending: false })
            .then(function (result) {
                if (result.error) {
                    console.error('Error loading projects:', result.error);
                    grid.innerHTML = '<div style="text-align:center; padding:40px; color:var(--neon-red);">COMMUNICATION ERROR</div>';
                    return;
                }
                allProjects = result.data || [];
                updateStats();
                renderProjects();
                updateGlobalTime();
            });
    }

    function getProjectIconInfo(project) {
        const text = (project.name + ' ' + (project.description || '') + ' ' + (project.tags || []).join(' ')).toLowerCase();

        // Return object: { src: string, variantClass: string }

        // Writing Challenge - prioritize specifically to distinguish from generic knowledge
        if (text.includes('writing challenge') || text.includes('habit-tracker')) {
            return { src: 'assets/icon_knowledge.png', variantClass: 'variant-gold' };
        }

        // Voice/Music
        if (text.includes('voice') || text.includes('audio') || text.includes('speak') || text.includes('transcription')) {
            // Voice memo vs generic media
            if (text.includes('memo') || text.includes('record')) {
                return { src: 'assets/icon_media.png', variantClass: 'variant-green' };
            }
            return { src: 'assets/icon_media.png', variantClass: '' };
        }

        // Biology
        if (text.includes('bio') || text.includes('gene') || text.includes('dna')) {
            return { src: 'assets/icon_bio.png', variantClass: '' };
        }

        // NotebookLM (Knowledge)
        if (text.includes('notebooklm') || text.includes('study') || text.includes('learn')) {
            return { src: 'assets/icon_knowledge.png', variantClass: '' }; // Default blue knowledge
        }

        // Time
        if (text.includes('time') || text.includes('clock') || text.includes('schedule')) {
            return { src: 'assets/icon_chrono.png', variantClass: '' };
        }

        // Core/Bot
        if (text.includes('bot') || text.includes('command') || text.includes('meta')) {
            return { src: 'assets/icon_core.png', variantClass: '' };
        }

        // Fallback
        return { src: 'assets/icon_knowledge.png', variantClass: '' };
    }

    function updateStats() {
        const activeCount = allProjects.filter(p => p.status === 'active').length;
        const totalCount = allProjects.length;
        const deployedCount = allProjects.filter(p => p.hosted_url).length;
        const criticalCount = allProjects.filter(p => p.status === 'needs-fix').length;

        setText('stat-total', totalCount.toString().padStart(2, '0'));
        setText('stat-active', activeCount.toString().padStart(2, '0'));
        setText('stat-deployed', deployedCount.toString().padStart(2, '0'));

        const criticalEl = document.getElementById('stat-critical');
        if (criticalEl) {
            criticalEl.textContent = criticalCount.toString().padStart(2, '0');
            criticalEl.parentElement.style.color = criticalCount > 0 ? 'var(--neon-red)' : 'var(--neon-blue)';
        }

        const statusText = criticalCount > 0 ? 'ATTENTION REQUIRED' : 'SYSTEMS ONLINE';
        const systemStatus = document.getElementById('system-status-text');
        if (systemStatus) {
            systemStatus.innerHTML = `<div class="status-indicator"></div> ${statusText}`;
            systemStatus.className = criticalCount > 0 ? 'status-text warning' : 'status-text safe';
        }

        renderLogs();
    }

    function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    function renderLogs() {
        const logsContainer = document.getElementById('system-logs');
        if (!logsContainer) return;

        let html = '';
        const timeStr = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });

        const attentionProjects = allProjects.filter(p => p.status === 'needs-fix' || p.status === 'wip');

        if (attentionProjects.length > 0) {
            attentionProjects.forEach(p => {
                const type = p.status === 'needs-fix' ? 'ERROR' : 'WARN';
                const msg = p.last_error || p.status_note || (p.status === 'wip' ? 'Work in progress' : 'Maintenance required');
                html += `<div class="log-entry ${type.toLowerCase()}">
                    <span class="log-time">[${timeStr}]</span>
                    <span class="log-msg"><strong style="color:inherit">${type}</strong>: ${p.name} - ${msg}</span>
                 </div>`;
            });
        }

        html += `<div class="log-entry info">
            <span class="log-time">[${timeStr}]</span>
            <span class="log-msg">Scan complete. ${allProjects.length} modules loaded.</span>
        </div>`;

        logsContainer.innerHTML = html;
    }

    function renderProjects() {
        var grid = document.getElementById('projectsGrid');
        var filtered = allProjects;

        if (currentFilter !== 'all') {
            if (currentFilter === 'deployed') {
                filtered = allProjects.filter(function (p) { return p.hosted_url; });
            } else if (currentFilter === 'active') {
                filtered = allProjects.filter(function (p) { return p.status === 'active'; });
            } else {
                filtered = allProjects.filter(function (p) { return p.status === currentFilter; });
            }
        }

        if (filtered.length === 0) {
            grid.innerHTML = '<div style="padding:40px; color:var(--text-dim); text-align:center; grid-column:1/-1;">NO MODULES FOUND IN THIS SECTOR</div>';
            return;
        }

        grid.innerHTML = filtered.map(renderProjectCard).join('');
    }

    function renderProjectCard(p) {
        const iconInfo = getProjectIconInfo(p);
        const statusClass = 'status-' + (p.status || 'active');

        let actions = '';
        if (p.hosted_url) {
            actions += `<a href="${p.hosted_url}" target="_blank" class="hud-btn primary">LAUNCH</a>`;
        }
        if (p.path) {
            actions += `<button onclick="copyToClipboard('${p.path.replace(/'/g, "\\'")}')" class="hud-btn secondary">COPY PATH</button>`;
        }

        const tags = (p.tags || []).slice(0, 3).map(t => `<span class="hud-tag">${t}</span>`).join('');

        let updateTime = 'Unknown';
        if (p.updated_at || p.created) {
            const date = new Date(p.updated_at || p.created);
            // Format: DD/MM HH:MM
            updateTime = date.getDate().toString().padStart(2, '0') + '/' +
                (date.getMonth() + 1).toString().padStart(2, '0') + ' ' +
                date.getHours().toString().padStart(2, '0') + ':' +
                date.getMinutes().toString().padStart(2, '0');
        }

        let statusMsgHTML = '';
        if (p.status === 'needs-fix' && (p.status_note || p.last_error)) {
            statusMsgHTML = `<div class="status-msg-box">
                <span style="font-size:18px">⚠️</span>
                <span>${p.status_note || p.last_error}</span>
            </div>`;
        }

        return `
        <div class="hud-card ${statusClass}">
            <div class="card-icon-container">
                <img src="${iconInfo.src}" class="card-icon ${iconInfo.variantClass}" alt="icon">
            </div>
            <div class="card-content">
                <div class="card-header">
                    <h3 class="card-title">${p.name}</h3>
                </div>
                
                <div class="card-meta-line">
                    <span class="meta-tag">${p.type || 'UNKNOWN'}</span>
                    <span class="meta-time">UPD: ${updateTime}</span>
                </div>

                ${statusMsgHTML}
                <div class="card-desc">${p.description || 'No data available'}</div>
                <div class="card-tags">${tags}</div>
                <div class="card-actions">
                    ${actions}
                    ${p.github_repo ? `<a href="${p.github_repo}" target="_blank" class="hud-btn icon-only" title="GitHub">GH</a>` : ''}
                    ${p.claude_session_url ? `<a href="${p.claude_session_url}" target="_blank" class="hud-btn icon-only" title="Claude">AI</a>` : ''}
                </div>
            </div>
        </div>
        `;
    }

    function setupEventListeners() {
        document.querySelectorAll('.filter-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                renderProjects();
            });
        });
    }

    window.copyToClipboard = function (text) {
        navigator.clipboard.writeText(text).then(function () {
            showToast('DATA COPIED TO CLIPBOARD');
        });
    };

    function showToast(msg) {
        const t = document.getElementById('hud-toast');
        t.innerText = `[SYS] ${msg}`;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 3000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

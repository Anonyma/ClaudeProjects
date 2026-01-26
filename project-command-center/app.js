(function () {
    'use strict';

    var SUPABASE_URL = 'https://ydwjzlikslebokuxzwco.supabase.co';
    var SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU';

    var supabaseClient;
    var allProjects = [];
    var currentFilter = 'all';
    var currentCategory = 'all';

    var CATEGORY_INFO = {
        utilities: { icon: '🔧', title: 'Utilities', description: 'System monitoring & admin tools' },
        apps: { icon: '📱', title: 'Apps', description: 'Full-featured standalone applications' },
        upskilling: { icon: '📚', title: 'Upskilling', description: 'Learning & personal development tools' },
        infrastructure: { icon: '🏗️', title: 'Infrastructure', description: 'Meta/tracking/productivity tools' },
        bots: { icon: '🤖', title: 'Bots', description: 'Telegram/chat bots' },
        archived: { icon: '📦', title: 'Archived', description: 'Deprecated/archived projects' }
    };

    var CATEGORY_ORDER = ['utilities', 'apps', 'upskilling', 'infrastructure', 'bots', 'archived'];

    var AUTO_REFRESH_INTERVAL = 60000; // Refresh every 60 seconds

    function init() {
        waitForSupabase(function () {
            supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
            loadProjects();
            setupEventListeners();

            // Auto-refresh every minute
            setInterval(function () {
                loadProjects();
                updateLastRefresh();
            }, AUTO_REFRESH_INTERVAL);

            updateLastRefresh();
        });
    }

    function updateLastRefresh() {
        // This is just the browser refresh time, lastSync shows data age
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
                    '<div class="empty-state">Failed to load Supabase library</div>';
            }
        }
        check();
    }

    function loadProjects() {
        supabaseClient
            .from('claude_projects')
            .select('*')
            .order('updated_at', { ascending: false })
            .then(function (result) {
                if (result.error) {
                    console.error('Error loading projects:', result.error);
                    document.getElementById('projectsGrid').innerHTML =
                        '<div class="empty-state">Error loading projects. Check console.</div>';
                    return;
                }
                allProjects = result.data || [];
                updateStats();
                renderProjects();
            });
    }

    function updateStats() {
        var activeCount = allProjects.filter(function (p) { return p.status === 'active'; }).length;
        var needsFixCount = allProjects.filter(function (p) { return p.status === 'needs-fix'; }).length;
        var wipCount = allProjects.filter(function (p) { return p.status === 'wip'; }).length;
        var archivedCount = allProjects.filter(function (p) {
            return p.status === 'archived' || p.status === 'deprecated';
        }).length;

        // Header stats
        document.getElementById('totalProjects').textContent = allProjects.length;
        document.getElementById('activeProjects').textContent = activeCount;
        document.getElementById('needsFixProjects').textContent = needsFixCount;
        document.getElementById('deployedProjects').textContent =
            allProjects.filter(function (p) { return p.hosted_url; }).length;

        // Health panel
        document.getElementById('healthyCount').textContent = activeCount;
        document.getElementById('needsFixCount').textContent = needsFixCount;
        document.getElementById('wipCount').textContent = wipCount;
        document.getElementById('archivedCount').textContent = archivedCount;

        // Attention list (projects needing attention)
        var attentionProjects = allProjects.filter(function (p) {
            return p.status === 'needs-fix' || p.status === 'wip';
        });
        var attentionHtml = '';
        attentionProjects.forEach(function (p) {
            var isWip = p.status === 'wip';
            var reason = p.last_error || p.status_note || (isWip ? 'Work in progress' : 'Needs attention');

            // Build links based on what info we have
            var links = '';

            // Deployment link - detect platform
            if (p.deployment_platform === 'railway' || (p.hosted_url && p.hosted_url.includes('railway'))) {
                links += '<a href="https://railway.com/dashboard" target="_blank" class="attention-link primary">🚂 Railway</a>';
            } else if (p.deployment_platform === 'netlify' || (p.hosted_url && p.hosted_url.includes('netlify'))) {
                links += '<a href="https://app.netlify.com/" target="_blank" class="attention-link primary">🚀 Netlify</a>';
            } else if (p.deployment_platform === 'replit' || (p.hosted_url && p.hosted_url.includes('replit'))) {
                links += '<a href="https://replit.com/" target="_blank" class="attention-link primary">💻 Replit</a>';
            }

            // Live app if exists
            if (p.hosted_url) {
                links += '<a href="' + p.hosted_url + '" target="_blank" class="attention-link">🌐 Live App</a>';
            }

            // GitHub
            if (p.github_repo) {
                links += '<a href="' + p.github_repo + '" target="_blank" class="attention-link">🐙 GitHub</a>';
            }

            // Claude session
            if (p.claude_session_url) {
                links += '<a href="' + p.claude_session_url + '" target="_blank" class="attention-link">🤖 Claude Session</a>';
            }

            // Supabase if it's a supabase project
            if (p.tags && p.tags.includes('supabase')) {
                links += '<a href="https://supabase.com/dashboard/project/ydwjzlikslebokuxzwco" target="_blank" class="attention-link">🗄️ Supabase</a>';
            }

            // Local path copy
            if (p.path) {
                links += '<button onclick="copyToClipboard(\'' + p.path.replace(/'/g, "\\'") + '\')" class="attention-link">📁 Copy Path</button>';
            }

            attentionHtml += '<div class="attention-item' + (isWip ? ' wip' : '') + '">' +
                '<div class="attention-header">' +
                '<span>' + (isWip ? '🚧' : '⚠️') + '</span>' +
                '<span>' + p.name + '</span>' +
                '</div>' +
                '<div class="attention-reason">' + reason + '</div>' +
                (links ? '<div class="attention-links">' + links + '</div>' : '') +
                '</div>';
        });

        if (attentionProjects.length === 0) {
            attentionHtml = '<div style="color: var(--accent-green); padding: 8px 0;">✓ All projects healthy</div>';
        }

        document.getElementById('attentionList').innerHTML = attentionHtml;

        // Claude sessions
        var sessionsHtml = '';
        var projectsWithSessions = allProjects.filter(function (p) { return p.claude_session_url; });
        if (projectsWithSessions.length === 0) {
            sessionsHtml = '<span class="no-sessions">No saved sessions</span>';
        } else {
            projectsWithSessions.forEach(function (p) {
                sessionsHtml += '<a href="' + p.claude_session_url + '" target="_blank" class="session-btn">' +
                    '🔗 ' + p.name + '</a>';
            });
        }
        document.getElementById('sessionsList').innerHTML = sessionsHtml;

        // Last sync - show the latest updated_at from projects
        var latestUpdate = null;
        allProjects.forEach(function (p) {
            var d = new Date(p.updated_at || p.created);
            if (!latestUpdate || d > latestUpdate) latestUpdate = d;
        });

        if (latestUpdate) {
            var timeStr = latestUpdate.toLocaleDateString() + ' ' + latestUpdate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            document.getElementById('lastSync').textContent = 'Data as of: ' + timeStr;
        } else {
            document.getElementById('lastSync').textContent = 'Sync status unknown';
        }
    }

    function renderProjects() {
        var grid = document.getElementById('projectsGrid');
        var filtered = allProjects;

        // Apply category filter first
        if (currentCategory !== 'all') {
            filtered = filtered.filter(function (p) { return p.category === currentCategory; });
        }

        // Then apply status filter
        if (currentFilter !== 'all') {
            if (currentFilter === 'deployed') {
                filtered = filtered.filter(function (p) { return p.hosted_url; });
            } else if (currentFilter === 'local') {
                filtered = filtered.filter(function (p) { return p.path && !p.hosted_url; });
            } else {
                filtered = filtered.filter(function (p) { return p.status === currentFilter; });
            }
        }

        if (filtered.length === 0) {
            grid.innerHTML = '<div class="empty-state">No projects found</div>';
            return;
        }

        // If showing all categories, group by category
        if (currentCategory === 'all') {
            var html = '';
            CATEGORY_ORDER.forEach(function (cat) {
                var catProjects = filtered.filter(function (p) { return p.category === cat; });
                if (catProjects.length > 0) {
                    var info = CATEGORY_INFO[cat] || { icon: '📁', title: cat, description: '' };
                    html += '<div class="category-section">' +
                        '<div class="category-header ' + cat + '">' +
                        '<span class="category-icon">' + info.icon + '</span>' +
                        '<span class="category-title">' + info.title + '</span>' +
                        '<span class="category-count">' + catProjects.length + ' project' + (catProjects.length !== 1 ? 's' : '') + '</span>' +
                        '<span class="category-description">' + info.description + '</span>' +
                        '</div>' +
                        '<div class="projects-grid">' + catProjects.map(renderProjectCard).join('') + '</div>' +
                        '</div>';
                }
            });

            // Handle projects without a category
            var uncategorized = filtered.filter(function (p) { return !p.category || !CATEGORY_INFO[p.category]; });
            if (uncategorized.length > 0) {
                html += '<div class="category-section">' +
                    '<div class="category-header">' +
                    '<span class="category-icon">❓</span>' +
                    '<span class="category-title">Uncategorized</span>' +
                    '<span class="category-count">' + uncategorized.length + ' project' + (uncategorized.length !== 1 ? 's' : '') + '</span>' +
                    '</div>' +
                    '<div class="projects-grid">' + uncategorized.map(renderProjectCard).join('') + '</div>' +
                    '</div>';
            }

            grid.innerHTML = html;
        } else {
            // Single category view - no section headers needed
            grid.innerHTML = filtered.map(renderProjectCard).join('');
        }
    }

    function renderProjectCard(p) {
        var statusClass = 'status-' + (p.status || 'active');
        var statusLabel = (p.status || 'active').replace('-', ' ');
        var accessLinks = '';

        // Access type badge (Online/Local/Not Configured)
        var accessBadge = '';
        if (p.hosted_url) {
            accessBadge = '<span class="access-badge online">🌐 Online</span>';
        } else if (p.path) {
            accessBadge = '<span class="access-badge local">💻 Local</span>';
        } else {
            accessBadge = '<span class="access-badge unconfigured">⚠️ No Access</span>';
        }

        if (p.hosted_url) {
            accessLinks += '<a href="' + p.hosted_url + '" target="_blank" class="access-link primary">' +
                '<span class="platform-icon">🌐</span><span>Open Live App</span></a>';
        }

        if (p.path) {
            var fileUrl = 'file://' + p.path;
            accessLinks += '<div class="access-link-row">' +
                '<a href="' + fileUrl + '" class="access-link"><span class="platform-icon">📁</span>' +
                '<span>Open Folder</span></a>' +
                '<button class="copy-path-btn" onclick="event.stopPropagation(); copyToClipboard(\'' + p.path.replace(/'/g, "\\'") + '\')" title="Copy path">📋</button>' +
                '</div>';
        }

        if (p.github_repo) {
            accessLinks += '<a href="' + p.github_repo + '" target="_blank" class="access-link">' +
                '<span class="platform-icon">🐙</span><span>GitHub</span></a>';
        }

        // Localhost command - show copyable run command
        if (p.localhost_command || p.server_command) {
            var cmd = p.localhost_command || p.server_command;
            accessLinks += '<button class="access-link" onclick="event.stopPropagation(); copyToClipboard(\'' + cmd.replace(/'/g, "\\'") + '\')" title="' + cmd + '">' +
                '<span class="platform-icon">▶️</span><span>Copy Run Command</span></button>';
        }

        var tags = (p.tags || []).map(function (t) { return '<span class="tag">' + t + '</span>'; }).join('');
        var sessionLink = p.claude_session_url ?
            '<a href="' + p.claude_session_url + '" target="_blank" class="session-link">📎 Claude Session</a>' : '';
        var updatedAt = p.updated_at ? new Date(p.updated_at).toLocaleDateString() : 'Unknown';

        // Category badge
        var catInfo = CATEGORY_INFO[p.category] || { icon: '📁', title: p.category || 'Unknown' };
        var categoryBadge = '<span class="category-badge cat-' + (p.category || 'unknown') + '">' + catInfo.icon + ' ' + catInfo.title + '</span>';

        return '<div class="project-card">' +
            '<div class="project-header"><div>' +
            '<div class="project-name">' + p.name + '</div>' +
            '<div style="display: flex; gap: 6px; margin-top: 4px;">' + categoryBadge + '<span class="project-type">' + (p.type || 'project') + '</span></div></div>' +
            '<div class="header-badges">' + accessBadge + '<span class="status-badge ' + statusClass + '">' + statusLabel + '</span></div></div>' +
            '<div class="project-description">' + (p.description || 'No description') + '</div>' +
            '<div class="project-tags">' + tags + '</div>' +
            '<div class="access-section"><div class="access-title">Access</div>' +
            '<div class="access-links">' + (accessLinks || '<div style="color: var(--text-secondary); font-size: 12px;">No access configured</div>') + '</div></div>' +
            sessionLink +
            '<div class="project-meta"><span class="meta-item">Updated: ' + updatedAt + '</span></div></div>';
    }

    function setupEventListeners() {
        // Category filter buttons
        var catBtns = document.querySelectorAll('.cat-filter-btn');
        catBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                catBtns.forEach(function (b) { b.classList.remove('active'); });
                btn.classList.add('active');
                currentCategory = btn.dataset.category;
                renderProjects();
            });
        });

        // Status filter buttons
        var filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                filterBtns.forEach(function (b) { b.classList.remove('active'); });
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                renderProjects();
            });
        });

        document.getElementById('addProjectForm').addEventListener('submit', function (e) {
            e.preventDefault();
            var formData = new FormData(e.target);
            var project = {
                id: formData.get('id'),
                name: formData.get('name'),
                description: formData.get('description'),
                type: formData.get('type'),
                status: formData.get('status'),
                hosted_url: formData.get('hosted_url') || null,
                path: formData.get('path') || null,
                github_repo: formData.get('github_repo') || null,
                claude_session_url: formData.get('claude_session_url') || null,
                tags: formData.get('tags') ? formData.get('tags').split(',').map(function (t) { return t.trim(); }) : [],
                created: new Date().toISOString().split('T')[0]
            };

            supabaseClient.from('claude_projects').upsert(project, { onConflict: 'id' }).then(function (result) {
                if (result.error) {
                    alert('Error saving project: ' + result.error.message);
                    return;
                }
                closeAddModal();
                loadProjects();
            });
        });

        document.getElementById('addModal').addEventListener('click', function (e) {
            if (e.target.id === 'addModal') closeAddModal();
        });
    }

    // Expose modal functions globally
    window.openAddModal = function () {
        document.getElementById('addModal').classList.add('show');
    };

    window.closeAddModal = function () {
        document.getElementById('addModal').classList.remove('show');
        document.getElementById('addProjectForm').reset();
    };

    // Quick Actions functions
    var COMMANDS = {
        'sync': '/Users/z/miniforge3/bin/python3 /Users/z/Desktop/PersonalProjects/ClaudeProjects/scripts/sync_projects.py',
        'dry-run': '/Users/z/miniforge3/bin/python3 /Users/z/Desktop/PersonalProjects/ClaudeProjects/scripts/sync_projects.py --dry-run'
    };

    var PATHS = {
        'projects-json': '/Users/z/Desktop/PersonalProjects/ClaudeProjects/projects.json',
        'sync-log': '/Users/z/Desktop/PersonalProjects/ClaudeProjects/scripts/sync.log',
        'claude-md': '/Users/z/Desktop/PersonalProjects/ClaudeProjects/CLAUDE.md',
        'tabs-backup': '/Users/z/Desktop/PersonalProjects/ClaudeProjects/chrome_tabs_backup.json'
    };

    var LINKS = {
        'supabase': 'https://supabase.com/dashboard/project/ydwjzlikslebokuxzwco',
        'netlify': 'https://app.netlify.com/',
        'railway': 'https://railway.com/dashboard',
        'github': 'https://github.com/Anonyma',
        'study-app': 'https://notebooklmstudyhub.netlify.app/',
        'art-app': 'https://art-discoverer.netlify.app',
        'writing-app': 'https://writing-challenge-app.netlify.app',
        'agent-hub': 'http://localhost:8766/dashboard.html',
        'health-monitor': 'file:///Users/z/Desktop/PersonalProjects/ClaudeProjects/health-monitor/dashboard.html',
        'tab-dashboard': 'http://localhost:8877/comet-tab-dashboard.html'
    };

    function showToast(message) {
        var toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(function () {
            toast.classList.remove('show');
        }, 2500);
    }

    window.copyCommand = function (cmd) {
        var command = COMMANDS[cmd];
        if (command) {
            navigator.clipboard.writeText(command).then(function () {
                showToast('✓ Command copied to clipboard');
            });
        }
    };

    window.copyPath = function (pathKey) {
        var path = PATHS[pathKey];
        if (path) {
            navigator.clipboard.writeText(path).then(function () {
                showToast('✓ Path copied to clipboard');
            });
        }
    };

    window.openLink = function (linkKey) {
        var url = LINKS[linkKey];
        if (url) {
            window.open(url, '_blank');
        }
    };

    window.toggleActions = function () {
        var grid = document.getElementById('actionsGrid');
        var btn = document.querySelector('.toggle-actions');
        grid.classList.toggle('collapsed');
        btn.textContent = grid.classList.contains('collapsed') ? '▶' : '▼';
    };

    window.copyToClipboard = function (text) {
        navigator.clipboard.writeText(text).then(function () {
            showToast('✓ Copied to clipboard');
        });
    };

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

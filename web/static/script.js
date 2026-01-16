document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    let currentGuildId = null;
    let guilds = [];
    let currentFeatures = [];
    let currentConfigs = [];

    // --- Config Mapping ---
    // Mapping config keys to services and validating them if needed
    // --- Config Mapping ---
    // Mapping config keys to services and validating them if needed
    const SERVICE_CONFIG_MAP = {
        'home_debt': {
            keys: ['CHANNEL_HOME_DEBT_ID'],
            validation: 'channel_list'
        },
        'noi_tu': {
            keys: ['CHANNEL_NOI_TU_IDS'],
            validation: 'channel_list'
        },
        'football': {
            keys: ['CHANNEL_FOOTBALL_IDS', 'FOOTBALL_API_KEY', 'FOOTBALL_LEAGUES', 'FOOTBALL_TEAMS'],
            validation: 'channel_list',
            meta: {
                'FOOTBALL_LEAGUES': { type: 'multi-select', options: ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1', 'UEFA Champions League', 'V-League'] },
                'FOOTBALL_TEAMS': { type: 'async-select', placeholder: 'Search team...' }
            }
        },
        'score': {
            keys: [],
            validation: null
        }
    };

    // --- Elements ---
    const serverList = document.getElementById('serverList');
    const selectedGuildName = document.getElementById('selectedGuildName');
    const contentArea = document.getElementById('contentArea');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const adminIdsInput = document.getElementById('adminIdsInput');
    const saveAdminsBtn = document.getElementById('saveAdminsBtn');
    const adminValidationMsg = document.getElementById('adminValidationMsg');
    const servicesContainer = document.getElementById('servicesContainer');
    const serverInfoContainer = document.getElementById('serverInfoContainer');
    const configTableBody = document.querySelector('#configTable tbody');
    const configForm = document.getElementById('configForm');

    // --- Init ---
    init();

    async function init() {
        await fetchGuilds();
        setupTabs();
        setupEventListeners();
    }

    function setupEventListeners() {
        // Admin Save
        saveAdminsBtn.addEventListener('click', saveAdmins);

        // Custom Config Save
        configForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(configForm);
            await saveConfig(
                formData.get('key'),
                formData.get('value'),
                formData.get('description')
            );
            configForm.reset();
            refreshData();
        });
    }

    function setupTabs() {
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // UI Toggle
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });
    }

    // --- API and Logic ---

    function showLoading(show) {
        if (show) {
            loadingOverlay.classList.remove('hidden');
            contentArea.style.opacity = '0.5';
            contentArea.style.pointerEvents = 'none';
        } else {
            loadingOverlay.classList.add('hidden');
            contentArea.style.opacity = '1';
            contentArea.style.pointerEvents = 'auto';
        }
    }

    async function fetchGuilds() {
        try {
            const res = await fetch('/api/guilds');
            guilds = await res.json();
            renderSidebar();

            // Auto-select first
            if (guilds.length > 0) {
                selectGuild(guilds[0].id);
            } else {
                serverList.innerHTML = '<li style="padding:15px">No guilds found. Invite bot to server first.</li>';
                selectedGuildName.textContent = 'No Servers Available';
            }
        } catch (e) {
            console.error(e);
            serverList.innerHTML = '<li style="padding:15px; color:var(--danger-color);">Failed to load servers</li>';
        }
    }

    // Modified refreshData to accept silent mode
    async function refreshData(silent = false) {
        if (!currentGuildId) return;

        if (!silent) showLoading(true);

        try {
            // Parallel fetch
            const [featuresRes, configsRes, detailsRes] = await Promise.all([
                fetch(`/api/guilds/${currentGuildId}/features`),
                fetch(`/api/guilds/${currentGuildId}/config`),
                fetch(`/api/guilds/${currentGuildId}/details`)
            ]);

            currentFeatures = await featuresRes.json();
            currentConfigs = await configsRes.json();
            const details = await detailsRes.json();

            renderServerInfo(details);
            renderAdminSection();
            renderServicesTab();
            renderConfigTab();
        } catch (e) {
            console.error(e);
            alert("Failed to load guild data.");
        } finally {
            if (!silent) showLoading(false);
        }
    }

    async function saveConfig(key, value, description) {
        try {
            const res = await fetch(`/api/guilds/${currentGuildId}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key, value, description, guild_id: currentGuildId })
            });
            if (!res.ok) throw new Error('Failed to save');
            return true;
        } catch (e) {
            alert(e.message);
            return false;
        }
    }

    // --- Rendering ---

    function renderSidebar() {
        serverList.innerHTML = '';
        guilds.forEach(guild => {
            const li = document.createElement('li');
            li.className = `server-item ${String(guild.id) === currentGuildId ? 'active' : ''}`;
            li.textContent = guild.name;
            li.onclick = () => selectGuild(guild.id);
            serverList.appendChild(li);
        });
    }

    function selectGuild(id) {
        currentGuildId = String(id);
        const guild = guilds.find(g => String(g.id) === currentGuildId);
        selectedGuildName.textContent = guild ? guild.name : 'Unknown Guild';
        contentArea.classList.remove('hidden');

        // Re-render sidebar to update active state
        renderSidebar();

        // Load Data
        refreshData(); // Not silent (full load)
    }

    // --- Tab 1: Server Info ---
    function renderServerInfo(details) {
        if (!details.found) {
            serverInfoContainer.innerHTML = '<p>Guild details not found in Bot cache.</p>';
            return;
        }

        const iconHtml = details.icon_url
            ? `<img src="${details.icon_url}" style="width:64px; height:64px; border-radius:50%; margin-bottom:10px;">`
            : `<div style="width:64px; height:64px; background:#444; border-radius:50%; margin:0 auto 10px; display:flex; align-items:center; justify-content:center;">?</div>`;

        serverInfoContainer.innerHTML = `
            <div class="info-item">
                ${iconHtml}
                <div style="font-weight:bold">${details.name}</div>
                <div class="text-muted">ID: ${details.id}</div>
            </div>
            <div class="info-item">
                <label>Members</label>
                <span>${details.member_count}</span>
            </div>
            <div class="info-item">
                <label>Owner ID</label>
                <span>${details.owner}</span>
            </div>
        `;
    }

    // --- Tab 2: Config & Admin ---
    function renderAdminSection() {
        const adminConfig = currentConfigs.find(c => c.key === 'ADMIN_IDS');
        adminIdsInput.value = adminConfig ? adminConfig.value : '';
        adminValidationMsg.textContent = '';
    }

    async function saveAdmins() {
        const raw = adminIdsInput.value;
        const ids = raw.split(',').map(s => s.trim()).filter(s => s.length > 0);

        // Inline Loading State
        const originalText = saveAdminsBtn.textContent;
        saveAdminsBtn.disabled = true;
        saveAdminsBtn.innerHTML = '<span class="spinner-sm"></span> Verifying...';
        adminValidationMsg.textContent = 'Checking IDs...';

        let invalidIds = [];

        // Note: For "System/Global" (ID 0), we can't really validate members unless we pick a random guild or check global cache?
        // Actually, bot.get_user() is safer for global, but endpoints use guild.get_member().
        // Let's skip validation for ID 0 for now or assume it passes.
        if (currentGuildId !== "0") {
            for (const uid of ids) {
                try {
                    const res = await fetch(`/api/guilds/${currentGuildId}/members/${uid}`);
                    if (!res.ok) invalidIds.push(uid);
                } catch (e) {
                    invalidIds.push(uid);
                }
            }
        }

        if (invalidIds.length > 0) {
            adminValidationMsg.innerHTML = `<span style="color:var(--danger-color)">Invalid User IDs: ${invalidIds.join(', ')}</span>`;
            saveAdminsBtn.disabled = false;
            saveAdminsBtn.innerHTML = originalText;
            return;
        }

        // All valid
        await saveConfig('ADMIN_IDS', ids.join(','), 'Admin List');
        adminValidationMsg.innerHTML = '<span style="color:var(--accent-color)">✅ Saved successfully!</span>';
        saveAdminsBtn.disabled = false;
        saveAdminsBtn.innerHTML = originalText;
        refreshData(true); // Silent refresh
    }

    // --- Tab 3: Services ---
    function renderServicesTab() {
        servicesContainer.innerHTML = '';
        const knownServices = ['home_debt', 'noi_tu', 'score', 'football'];

        knownServices.forEach(serviceName => {
            const feature = currentFeatures.find(f => f.feature_name === serviceName);
            const isEnabled = feature ? feature.is_enabled : false;

            const card = document.createElement('div');
            card.className = 'service-card';

            // Header
            const header = document.createElement('div');
            header.className = 'service-header';
            header.innerHTML = `<h3>${formatName(serviceName)}</h3>`;

            // Toggle
            const label = document.createElement('label');
            label.className = 'switch';
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.checked = isEnabled;
            input.onchange = () => toggleService(serviceName, input.checked);

            const span = document.createElement('span');
            span.className = 'slider';

            label.appendChild(input);
            label.appendChild(span);
            header.appendChild(label);

            // Body with Configs
            const body = document.createElement('div');
            body.className = `service-body ${isEnabled ? '' : 'disabled'}`;

            const configMeta = SERVICE_CONFIG_MAP[serviceName];
            const relevantKeys = configMeta ? configMeta.keys : [];

            if (relevantKeys.length > 0) {
                relevantKeys.forEach(key => {
                    const config = currentConfigs.find(c => c.key === key) || { value: '' };
                    const formGroup = document.createElement('div');
                    formGroup.className = 'form-group';

                    const meta = configMeta.meta && configMeta.meta[key] ? configMeta.meta[key] : {};
                    const inputType = meta.type || 'text';

                    formGroup.innerHTML = `<label>${key}</label>`;

                    // Input Container
                    const inputContainer = document.createElement('div');
                    inputContainer.style.position = 'relative'; // For dropdowns

                    if (inputType === 'multi-select') {
                        // Options Select
                        const container = document.createElement('div');

                        // Available Options (Filtered by what's not selected?)
                        // Actually simpler: Just a select box to Add, and a list of Tags for current values
                        const currentValues = config.value ? config.value.split(',').map(s => s.trim()).filter(s => s) : [];

                        const tagsDiv = document.createElement('div');
                        tagsDiv.className = 'tags-container';
                        tagsDiv.id = `tags-${key}`;
                        renderTags(tagsDiv, currentValues, key);

                        const select = document.createElement('select');
                        select.style.width = '100%';
                        select.style.marginBottom = '5px';
                        select.innerHTML = '<option value="">+ Add League...</option>';
                        meta.options.forEach(opt => {
                            if (!currentValues.includes(opt)) {
                                const o = document.createElement('option');
                                o.value = opt;
                                o.textContent = opt;
                                select.appendChild(o);
                            }
                        });

                        select.onchange = () => {
                            if (select.value) {
                                addTag(key, select.value);
                            }
                        };

                        container.appendChild(tagsDiv);
                        container.appendChild(select);
                        inputContainer.appendChild(container);

                        // Hidden input to store actual csv value for saving logic (optional, or we rebuild it)
                        const hidden = document.createElement('input');
                        hidden.type = 'hidden';
                        hidden.id = `input-${key}`;
                        hidden.value = config.value;
                        inputContainer.appendChild(hidden);

                    } else if (inputType === 'async-select') {
                        // Search & Add
                        const container = document.createElement('div');

                        const currentValues = config.value ? config.value.split(',').map(s => s.trim()).filter(s => s) : [];

                        const tagsDiv = document.createElement('div');
                        tagsDiv.className = 'tags-container';
                        tagsDiv.id = `tags-${key}`;
                        renderTags(tagsDiv, currentValues, key);

                        const searchInput = document.createElement('input');
                        searchInput.type = 'text';
                        searchInput.placeholder = meta.placeholder || 'Type to search...';
                        searchInput.style.marginBottom = '0';

                        const resultsDiv = document.createElement('div');
                        resultsDiv.className = 'dropdown-results';

                        let debounceTimer;
                        searchInput.oninput = (e) => {
                            const val = e.target.value;
                            clearTimeout(debounceTimer);
                            if (val.length < 2) {
                                resultsDiv.classList.remove('show');
                                return;
                            }
                            debounceTimer = setTimeout(async () => {
                                const res = await fetch(`/api/guilds/${currentGuildId}/football/teams?query=${encodeURIComponent(val)}`);
                                const data = await res.json();

                                resultsDiv.innerHTML = '';
                                if (data.length > 0) {
                                    data.forEach(item => {
                                        const div = document.createElement('div');
                                        div.className = 'dropdown-item';
                                        div.textContent = item.name; // Could use flag/logo if available
                                        div.onclick = () => {
                                            addTag(key, item.name); // Storing Name for now as per schema
                                            searchInput.value = '';
                                            resultsDiv.classList.remove('show');
                                        };
                                        resultsDiv.appendChild(div);
                                    });
                                    resultsDiv.classList.add('show');
                                } else {
                                    resultsDiv.classList.remove('show');
                                }
                            }, 500); // 500ms debounce
                        };

                        // Hide dropdown on click outside
                        document.addEventListener('click', (e) => {
                            if (!container.contains(e.target)) resultsDiv.classList.remove('show');
                        });

                        container.appendChild(tagsDiv);
                        container.appendChild(searchInput);
                        container.appendChild(resultsDiv);
                        inputContainer.appendChild(container);

                        const hidden = document.createElement('input');
                        hidden.type = 'hidden';
                        hidden.id = `input-${key}`;
                        hidden.value = config.value;
                        inputContainer.appendChild(hidden);

                    } else {
                        // Standard Input
                        inputContainer.innerHTML = `
                            <div style="display:flex; gap:10px;">
                                <input type="text" value="${config.value}" id="input-${key}" style="flex:1">
                            </div>
                         `;
                    }

                    formGroup.appendChild(inputContainer);

                    // Save Button (Common)
                    const saveRow = document.createElement('div');
                    saveRow.style.marginTop = '5px';
                    saveRow.innerHTML = `
                        <button class="btn secondary" id="btn-${key}" onclick="window.saveServiceConfig('${key}', '${configMeta.validation}')">Save</button>
                        <small id="msg-${key}" style="margin-left:10px"></small>
                    `;
                    formGroup.appendChild(saveRow);

                    body.appendChild(formGroup);
                });
            } else {
                body.innerHTML = '<p class="text-muted">No specific configurations for this service.</p>';
            }

            card.appendChild(header);
            card.appendChild(body);
            servicesContainer.appendChild(card);
        });
    }

    // --- Helpers for Tags ---
    function renderTags(container, values, key) {
        container.innerHTML = '';
        values.forEach(val => {
            const t = document.createElement('span');
            t.className = 'tag';
            t.innerHTML = `${val} <span class="remove" onclick="removeTag('${key}', '${val}')">&times;</span>`;
            container.appendChild(t);
        });
    }

    window.addTag = (key, value) => {
        const input = document.getElementById(`input-${key}`);
        let current = input.value ? input.value.split(',').map(s => s.trim()).filter(s => s) : [];
        if (!current.includes(value)) {
            current.push(value);
            input.value = current.join(',');
            // Re-render
            const tagsDiv = document.getElementById(`tags-${key}`);
            renderTags(tagsDiv, current, key);

            // Auto-save? user usually expects "Add" then "Save". Let's stick to explicit Save button logic for consistency.
            // Or trigger a "dirty" state.
        }
    };

    window.removeTag = (key, value) => {
        const input = document.getElementById(`input-${key}`);
        let current = input.value ? input.value.split(',').map(s => s.trim()).filter(s => s) : [];
        current = current.filter(v => v !== value);
        input.value = current.join(',');

        const tagsDiv = document.getElementById(`tags-${key}`);
        renderTags(tagsDiv, current, key);
    };

    async function toggleService(name, enabled) {
        try {
            const res = await fetch(`/api/guilds/${currentGuildId}/features`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feature_name: name, is_enabled: enabled })
            });
            if (res.ok) refreshData(true); // Silent refresh
        } catch (e) { console.error(e); }
    }

    // Helper for inline onclick
    window.saveServiceConfig = async (key, validationType) => {
        const input = document.getElementById(`input-${key}`);
        const btn = document.getElementById(`btn-${key}`);
        const msg = document.getElementById(`msg-${key}`);
        if (!input) return;

        const val = input.value.trim();

        // Inline Loading
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-sm"></span>';

        msg.textContent = 'Validating...';
        msg.style.color = 'var(--text-muted)';

        let isValid = true;
        let errStr = '';

        if (val.length > 0 && validationType === 'channel') {
            isValid = await validateChannel(val);
            if (!isValid) errStr = "Invalid Channel ID (not visible)";
        } else if (val.length > 0 && validationType === 'channel_list') {
            const ids = val.split(',').map(s => s.trim());
            for (let id of ids) {
                if (id.length > 0 && !(await validateChannel(id))) {
                    isValid = false;
                    errStr = `Invalid Channel ID: ${id}`;
                    break;
                }
            }
        }

        if (!isValid) {
            msg.textContent = errStr;
            msg.style.color = 'var(--danger-color)';
            btn.disabled = false;
            btn.textContent = originalText;
            return;
        }

        await saveConfig(key, val, 'Service Config');
        msg.textContent = 'Saved!';
        msg.style.color = 'var(--accent-color)';
        setTimeout(() => { msg.textContent = ''; }, 2000);

        btn.disabled = false;
        btn.textContent = originalText; // Restore text

        refreshData(true); // Silent
    };

    async function validateChannel(channelId) {
        try {
            const res = await fetch(`/api/guilds/${currentGuildId}/channels/${channelId}`);
            return res.ok;
        } catch (e) { return false; }
    }

    // --- Config Tab (Custom) ---
    function renderConfigTab() {
        configTableBody.innerHTML = '';

        // Exclude known service keys and admins from the generic table
        const serviceKeys = Object.values(SERVICE_CONFIG_MAP).flatMap(m => m.keys);
        const otherConfigs = currentConfigs.filter(c =>
            !serviceKeys.includes(c.key) && c.key !== 'ADMIN_IDS'
        );

        if (otherConfigs.length === 0) {
            configTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center">No custom configurations.</td></tr>';
            return;
        }

        otherConfigs.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${c.key}</td>
                <td>${c.value}</td>
                <td>${c.description || ''}</td>
                <td>
                    <button class="btn danger action-btn" onclick="deleteConfig('${c.key}')">Delete</button>
                </td>
            `;
            configTableBody.appendChild(tr);
        });
    }

    window.deleteConfig = async (key) => {
        if (!confirm('Delete config?')) return;
        try {
            await fetch(`/api/guilds/${currentGuildId}/config/${key}`, { method: 'DELETE' });
            refreshData(true); // Silent
        } catch (e) { alert(e); }
    };

    function formatName(str) {
        return str.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    }
});

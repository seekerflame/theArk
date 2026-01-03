document.addEventListener('DOMContentLoaded', function () {
    var BASE_RATE = 10;
    var LEVELS = [
        { threshold: 0, name: 'Newcomer', icon: '🌱' },
        { threshold: 100, name: 'Apprentice', icon: '🔨' },
        { threshold: 500, name: 'Journeyer', icon: '⚒️' },
        { threshold: 1500, name: 'Craftsman', icon: '🛠️' },
        { threshold: 5000, name: 'Master', icon: '⚡' },
        { threshold: 15000, name: 'Steward', icon: '👑' }
    ];
    // --- WALLET / IDENTITY SYSTEM ---
    var Wallet = {
        generateMnemonic: function () {
            // Simplified 12-word generation (simulation)
            var words = ["apple", "river", "sky", "mountain", "fire", "eagle", "stone", "forest", "rain", "sun", "moon", "star", "ocean", "tree", "wind", "cloud"];
            var phrase = [];
            for (var i = 0; i < 12; i++) phrase.push(words[Math.floor(Math.random() * words.length)]);
            return phrase.join(" ");
        },
        deriveAddress: function (mnemonic) {
            // Simple deterministic address (Simulated Hash)
            var hash = 0;
            for (var i = 0; i < mnemonic.length; i++) {
                hash = ((hash << 5) - hash) + mnemonic.charCodeAt(i);
                hash |= 0;
            }
            return "0x" + Math.abs(hash).toString(16).padStart(40, '0').substring(0, 40);
        }
    };

    var appState = {
        balance: 0,
        history: [],
        xp: 0,
        tasks: [], // Job Board State
        currentUser: { name: 'Guest', role: 'worker', address: null, mnemonic: null }
    };

    // ... (existing code) ...

    // --- DATA LOADING ---
    // loadState() is defined at the bottom, moving execution there or consolidating.
    // We will use the main loadState defined later.


    // --- JOB BOARD FILTER HELPER ---
    window.filterJobs = function () {
        renderJobBoard();
    }

    // --- JOB BOARD LOGIC ---
    window.claimTask = function (id) {
        var task = appState.tasks.find(t => t.id === id);
        if (task) {
            task.status = 'ASSIGNED';
            task.assignee = appState.currentUser.name;
            saveState(); updateUI();
            logToTerminal(`[JOB] Claimed: ${task.title}`);
        }
    };

    window.delegateTask = function (id) {
        var name = prompt("Delegate to whom?");
        if (!name) return;
        var task = appState.tasks.find(t => t.id === id);
        if (task) {
            task.status = 'ASSIGNED';
            task.assignee = name;
            saveState(); updateUI();
            logToTerminal(`[JOB] Delegated ${task.title} to ${name}`);
        }
    };

    window.dropTask = function (id) {
        if (!confirm("Abandon this task?")) return;
        var task = appState.tasks.find(t => t.id === id);
        if (task) {
            task.status = 'OPEN';
            task.assignee = null;
            saveState(); updateUI();
            logToTerminal(`[JOB] Dropped: ${task.title}`);
        }
    };

    function renderJobBoard() {
        var list = document.getElementById('quest-list');
        var myJobsList = document.getElementById('my-jobs-list');
        if (!list) return;

        // Open Jobs
        // SORT: Highest AT First
        var openTasks = appState.tasks.filter(t => t.status === 'OPEN').sort((a, b) => b.bounty - a.bounty);

        // FILTER: Check filter dropdown
        var filterEl = document.getElementById('job-filter');
        var filterVal = filterEl ? filterEl.value : 'ALL';

        if (filterVal !== 'ALL') {
            openTasks = openTasks.filter(t => t.category === filterVal);
        }

        list.innerHTML = openTasks.map(t => `
            <div class="quest-card" style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; border-left: 3px solid #10B981; margin-bottom:10px; position:relative; overflow:hidden;">
                <!-- Value Badge -->
                <div style="position:absolute; right:10px; top:10px; background:rgba(16, 185, 129, 0.2); color:#10B981; font-size:0.7rem; font-weight:bold; padding:2px 6px; border-radius:4px;">
                    ${t.bounty} AT
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <h4 style="margin:0; color:#eff6ff;">${t.title}</h4>
                    <span style="font-size:0.8rem; background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px;">${t.category}</span>
                </div>
                <p style="font-size:0.8rem; color:#94a3b8; margin:5px 0;">${t.description}</p>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px;">
                    <div style="font-size:0.75rem; color:#64748b;">ST: ${t.standard_time}h</div>
                    <div>
                        <button onclick="claimTask('${t.id}')" style="background:#10B981; border:none; color:black; font-size:0.7rem; padding:4px 8px; border-radius:4px; cursor:pointer;">✋ Claim</button>
                        <button onclick="delegateTask('${t.id}')" style="background:rgba(255,255,255,0.1); border:none; color:white; font-size:0.7rem; padding:4px 8px; border-radius:4px; cursor:pointer;">👉 Delegate</button>
                    </div>
                </div>
            </div>
        `).join('');

        // My Jobs (Assigned to Me)
        if (myJobsList) {
            var myTasks = appState.tasks.filter(t => t.assignee === appState.currentUser.name && t.status === 'ASSIGNED');
            myJobsList.innerHTML = myTasks.length ? myTasks.map(t => `
                <div class="quest-card" style="background:rgba(59, 130, 246, 0.1); padding:10px; border-radius:8px; border-left: 3px solid #3B82F6; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="margin:0; color:#eff6ff;">${t.title}</h4>
                        <span style="font-size:0.7rem; color:#3B82F6;">ACTIVE</span>
                    </div>
                     <p style="font-size:0.8rem; color:#94a3b8; margin:5px 0;">${t.description}</p>
                    <div style="display:flex; justify-content:flex-end; gap:5px; margin-top:5px;">
                        <button onclick="window.location.hash='#mint-section'; document.getElementById('task-select').value='custom'; document.getElementById('custom-desc').value='${t.title}'; document.getElementById('hours').value='${t.standard_time}'; updateTaskInfo();" 
                            style="background:#3B82F6; border:none; color:white; font-size:0.7rem; padding:4px 8px; border-radius:4px; cursor:pointer;">✅ Mint Work</button>
                        <button onclick="dropTask('${t.id}')" style="background:rgba(239, 68, 68, 0.2); border:none; color:#EF4444; font-size:0.7rem; padding:4px 8px; border-radius:4px; cursor:pointer;">✕ Drop</button>
                    </div>
                </div>
            `).join('') : '<div style="font-size:0.8rem; color:#64748b; text-align:center; padding:10px;">No active tasks. Claim one above!</div>';
        }
    }

    var loginOverlay = document.getElementById('login-overlay');
    var userBtns = document.querySelectorAll('.user-btn');
    var userBadge = document.getElementById('user-badge');
    var balanceDisplay = document.getElementById('balance-display');
    var form = document.getElementById('log-form');
    var terminalLog = document.getElementById('terminal-log');
    var clearBtn = document.getElementById('clear-data');
    var menuBtn = document.getElementById('menu-btn');
    var dropdown = document.getElementById('dropdown-menu');

    function init() {
        console.log('System Initialized');
        loadState();
        updateUI();
        logToTerminal('System Online.');
        initGraph();
        setInterval(refreshGraph, 2000);

        var savedUser = localStorage.getItem('abundanceUser');
        if (savedUser) {
            appState.currentUser = JSON.parse(savedUser);
            if (loginOverlay) loginOverlay.style.display = 'none';
        }
        updateUserUI();
    }

    // --- UI HELPERS ---
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert("Copied: " + text);
        });
    }

    // --- AUTH FLOW ---
    var createWalletBtn = document.getElementById('btn-create-wallet');
    var recoverWalletBtn = document.getElementById('btn-recover-wallet');
    var mnemonicDisplay = document.getElementById('mnemonic-display');
    var mnemonicText = document.getElementById('mnemonic-text');
    var confirmMnemonicBtn = document.getElementById('btn-confirm-mnemonic');

    // Button Listeners (if elements exist, created dynamically later)
    // --- LOGIN WIZARD STATE ---
    var loginState = { role: null, name: null };

    // Exposed functions for HTML onclicks
    window.selectRole = function (role) {
        loginState.role = role;
        document.getElementById('login-step-1').style.display = 'none';
        document.getElementById('login-step-2').style.display = 'block';
        setTimeout(() => document.getElementById('setup-name').focus(), 100);
    };

    window.confirmName = function () {
        var nameInput = document.getElementById('setup-name');
        var name = nameInput.value.trim();
        if (name.length < 2) {
            alert("Please enter a valid name (2+ chars).");
            nameInput.focus();
            return;
        }
        loginState.name = name;
        document.getElementById('login-step-2').style.display = 'none';
        document.getElementById('login-step-3').style.display = 'block';
    };

    window.backToRole = function () {
        document.getElementById('login-step-2').style.display = 'none';
        document.getElementById('login-step-1').style.display = 'block';
    };

    window.backToName = function () {
        document.getElementById('login-step-3').style.display = 'none';
        document.getElementById('login-step-2').style.display = 'block';
    };

    // Button Listeners
    document.addEventListener('click', function (e) {
        // CREATE WALLET
        if (e.target.id === 'btn-create-wallet') {
            if (!loginState.role || !loginState.name) return alert("System Error: Missing Role/Name");

            var phrase = Wallet.generateMnemonic();
            var address = Wallet.deriveAddress(phrase);

            // In a real app, show the phrase nicely, but for now:
            var confirmed = confirm("⚠️ SAVE THIS SECRET PHRASE ⚠️\n\n" + phrase + "\n\nClick OK to confirm you have written it down.");
            if (confirmed) {
                loginAs(loginState.name, loginState.role, address, phrase);
            }
        }

        // RECOVER
        if (e.target.id === 'btn-recover-wallet') {
            if (!loginState.role || !loginState.name) return alert("System Error: Missing Role/Name");
            var phrase = prompt("Enter your 12-word Recovery Phrase:");
            if (!phrase) return;
            var address = Wallet.deriveAddress(phrase);
            loginAs(loginState.name, loginState.role, address, phrase);
        }

        // Copy Address
        if (e.target.id === 'user-address-copy') {
            copyToClipboard(appState.currentUser.address);
        }
    });

    // Validated Login
    function loginAs(name, role, address, mnemonic) {
        appState.currentUser = {
            name: name,
            role: role,
            address: address,
            mnemonic: mnemonic // In real app, encrypt this!
        };
        localStorage.setItem('abundanceUser', JSON.stringify(appState.currentUser));
        if (loginOverlay) loginOverlay.style.display = 'none';
        updateUserUI();
        logToTerminal('[AUTH] Wallet Unlocked: ' + address);
        logToTerminal('[LOGIN] Welcome, ' + name + '!');
    }

    function updateUserUI() {
        var u = appState.currentUser;
        if (userBadge) {
            userBadge.innerHTML = `
                <div style="font-size:14px; font-weight:bold;">${u.role === 'oracle' ? '👁️' : '👤'} ${u.name}</div>
                <div id="user-address-copy" style="font-size:10px; opacity:0.7; cursor:pointer;" title="Click to Copy">${u.address ? u.address.substring(0, 8) + '...' + u.address.substring(36) : ''} 📋</div>
            `;
            userBadge.style.background = u.role === 'oracle' ? 'linear-gradient(135deg, #10B981, #059669)' : 'rgba(255,255,255,0.1)';
        }
        var verifyAllBtn = document.getElementById('action-verify-all');
        if (verifyAllBtn) {
            verifyAllBtn.style.display = u.role === 'oracle' ? 'block' : 'none';
        }
    }

    // --- UI MODULES ---
    function initMenu() {
        var menuBtn = document.getElementById('menu-btn');
        var dropdown = document.getElementById('dropdown-menu');

        if (!menuBtn || !dropdown) return;

        // Toggle Open/Close
        menuBtn.onclick = function (e) {
            e.stopPropagation();
            console.log("Menu clicked");
            var isVisible = dropdown.style.display === 'block';
            dropdown.style.display = isVisible ? 'none' : 'block';
            if (!isVisible) {
                // Determine if we need to force a reflow
                setTimeout(() => dropdown.classList.add('show'), 10);
            } else {
                dropdown.classList.remove('show');
            }
            logToTerminal('[UI] Menu Toggled: ' + (isVisible ? 'Closed' : 'Open'));
        };

        // Close on Link Click
        var links = dropdown.querySelectorAll('.menu-item');
        links.forEach(function (link) {
            link.addEventListener('click', function () {
                var view = link.getAttribute('data-view');
                if (view) switchView(view);
                dropdown.classList.remove('show');
            });
        });

        // Close on Click Outside
        document.addEventListener('click', function (e) {
            if (!menuBtn.contains(e.target) && !dropdown.contains(e.target)) {
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                }
            }
        });
    }

    function switchView(viewName) {
        var views = {
            'mint': document.getElementById('mint-section'),
            'transfer': document.getElementById('transfer-section'),
            'map': document.getElementById('map-section')
        };
        Object.values(views).forEach(function (el) { if (el) el.style.display = 'none'; });
        if (views[viewName]) {
            views[viewName].style.display = 'block';
            if (viewName === 'map') initMap();
        }
    }

    var verifyAllBtn = document.getElementById('action-verify-all');
    if (verifyAllBtn) {
        verifyAllBtn.addEventListener('click', function () {
            if (!confirm('Verify ALL pending blocks?')) return;
            fetch('http://localhost:3000/api/verify_all', { method: 'POST' })
                .then(function (res) { return res.json(); })
                .then(function (data) { alert(data.message); refreshGraph(); })
                .catch(function (e) { alert('Failed: ' + e); });
        });
    }

    var mapInitialized = false;
    function initMap() {
        if (mapInitialized) return;
        var mapContainer = document.getElementById('village-map');
        if (!mapContainer || typeof L === 'undefined') return;
        var map = L.map('village-map').setView([39.9, -94.5], 4);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: 'OSM/CARTO', subdomains: 'abcd', maxZoom: 19
        }).addTo(map);
        var nodes = [
            { pos: [39.9, -94.5], title: 'OSE HQ (Factor e Farm)', type: 'SEED' },
            { pos: [50.1, 8.6], title: 'The Ark (Backup)', type: 'SEED' },
            { pos: [40.7, -74.0], title: 'You (Village Node)', type: 'PEER' }
        ];
        nodes.forEach(function (n) {
            L.circleMarker(n.pos, { radius: 10, color: n.type === 'SEED' ? '#10B981' : '#3B82F6' })
                .addTo(map).bindPopup(n.title);
        });
        mapInitialized = true;
    }

    var transferForm = document.getElementById('transfer-form');
    if (transferForm) {
        transferForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var recipient = document.getElementById('recipient-input').value;
            var amount = parseFloat(document.getElementById('amount-input').value);
            if (!recipient || amount <= 0) return alert('Invalid Transfer');
            fetch('http://localhost:3000/api/transfer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sender: appState.currentUser.name, receiver: recipient, amount: amount })
            }).then(function (res) { return res.json(); })
                .then(function (data) {
                    if (data.status === 'success') {
                        logToTerminal('[TX] Sent ' + amount + ' AT to ' + recipient);
                        appState.balance -= amount;
                        saveState(); updateUI();
                        transferForm.reset();
                    }
                }).catch(function (e) { logToTerminal('[ERROR] ' + e); });
        });
    }

    var questBtn = document.getElementById('btn-post-quest');
    if (questBtn) {
        questBtn.addEventListener('click', function () {
            var title = prompt('Quest Title:');
            if (!title) return;
            var bounty = parseFloat(prompt('Bounty (AT):', '10'));
            fetch('http://localhost:3000/api/quest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: title, description: 'Web UI', bounty: bounty })
            }).then(function (res) { return res.json(); })
                .then(function (data) {
                    if (data.status === 'success') logToTerminal('[QUEST] Posted: ' + title);
                });
        });
    }

    function initGraph() {
        // Placeholder for future advanced D3 setup if needed.
        // Currently handled by renderDag via refreshGraph.
        console.log("Graph Visualization Ready");
    }

    function refreshGraph() {
        fetch('/api/graph') // RELATIVE
            .then(function (res) { return res.json(); })
            .then(function (data) { renderDag(data); renderQuestList(data); })
            .catch(function (e) { console.log('Graph poll failed', e); });
    }

    function renderQuestList(blocks) {
        var list = document.getElementById('quest-list');
        if (!list) return;
        var quests = blocks.filter(function (b) { return b.data.block_type === 'QUEST'; }).reverse();
        list.innerHTML = quests.map(function (q) {
            return '<div style="background:rgba(255,255,255,0.05);padding:10px;border-radius:8px;border-left:3px solid #3B82F6;margin-bottom:8px;">' +
                '<h4 style="margin:0;color:#eff6ff;">' + q.data.title + '</h4>' +
                '<div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#94a3b8;margin-top:5px;">' +
                '<span>' + q.hash.substring(0, 8) + '</span>' +
                '<span style="color:#3B82F6;font-weight:bold;">' + q.data.bounty + ' AT</span></div></div>';
        }).join('');
    }

    function renderDag(blocks) {
        var container = document.getElementById('dag-viz');
        if (!container || typeof d3 === 'undefined') return;
        var width = container.clientWidth;
        var height = container.clientHeight;
        d3.select('#dag-viz').selectAll('*').remove();
        var svg = d3.select('#dag-viz').append('svg').attr('width', width).attr('height', height);
        var nodes = blocks.map(function (b, i) { return { id: b.hash, index: i, block: b }; });
        var links = [];
        blocks.forEach(function (b) {
            if (b.parents) b.parents.forEach(function (p) { links.push({ source: p, target: b.hash }); });
        });
        var simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(function (d) { return d.id; }).distance(50))
            .force('charge', d3.forceManyBody().strength(-100))
            .force('center', d3.forceCenter(width / 2, height / 2));
        var link = svg.append('g').attr('stroke', '#999').selectAll('line').data(links).join('line');
        var nodeG = svg.append('g').selectAll('g').data(nodes).join('g')
            .style('cursor', appState.currentUser.role === 'oracle' ? 'pointer' : 'default')
            .on('click', function (event, d) {
                // Focus / Zoom?
                if (appState.currentUser.role === 'oracle') verifyBlock(d.id, d.block);
            });

        // ZOOM LOGIC (Basic Fit)
        // Adjust center force or viewbox? D3 v7 supports zoom behavior on SVG
        // For MVP, just ensure forces are reasonable:
        simulation.on('tick', function () {
            // Bound nodes to box
            nodes.forEach(function (d) {
                d.x = Math.max(10, Math.min(width - 10, d.x));
                d.y = Math.max(10, Math.min(height - 10, d.y));
            });
            link.attr('x1', function (d) { return d.source.x; }).attr('y1', function (d) { return d.source.y; })
                .attr('x2', function (d) { return d.target.x; }).attr('y2', function (d) { return d.target.y; });
            nodeG.attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
        });
    }

    function verifyBlock(hash, block) {
        if (block && block.data && block.data.verified) { alert('Already verified!'); return; }
        // OPEN VERIFIER PAGE
        if (confirm('Open Verification Station for this block?')) {
            window.location.href = 'verifier.html';
        }
    }

    // --- STANDARD TASK LOGIC ---
    window.updateTaskInfo = function () {
        var select = document.getElementById('task-select');
        var option = select.options[select.selectedIndex];
        var stDisplay = document.getElementById('st-display');
        var customRow = document.getElementById('custom-task-row');

        if (option.value === 'custom_task' || option.value === 'custom') {
            customRow.style.display = 'block';
            stDisplay.value = 0;
            stDisplay.readOnly = false; // Allow manual ST specifiction for custom? Or just base on actual?
            stDisplay.style.opacity = '1';
        } else {
            customRow.style.display = 'none';
            stDisplay.value = option.getAttribute('data-st');
            stDisplay.readOnly = true;
            stDisplay.style.opacity = '0.7';
        }
    };

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Get Task Info
            var select = document.getElementById('task-select');
            var option = select.options[select.selectedIndex];

            var taskName, st, rate;

            if (option.value === 'custom_task' || option.value === 'custom') {
                taskName = document.getElementById('custom-desc').value;
                st = parseFloat(document.getElementById('hours').value); // For custom, ST = Actual (No Efficiency Bonus)
                rate = 10;
            } else {
                taskName = option.text.split('(')[0].trim(); // Remove (4h)
                st = parseFloat(option.getAttribute('data-st'));
                rate = parseFloat(option.getAttribute('data-rate'));
            }

            var actualHours = parseFloat(document.getElementById('hours').value);
            var complexity = parseFloat(document.getElementById('complexity').value); // Quality/Complexity Modifier
            var proof = document.getElementById('proof').value || "Self-verified";

            // THE ABUNDANCE EQUATION: Reward = (ST * Rate) * Complexity
            // Note: Actual Hours is ONLY used for Efficiency Stat (ST / Actual)
            var reward = st * rate * complexity;
            var efficiency = 0;
            if (actualHours > 0) {
                efficiency = (st / actualHours * 100).toFixed(0);
            } else {
                efficiency = 0;
            }

            if (!taskName) return alert("Please describe the task.");

            fetch('/api/mint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task: taskName,
                    hours: actualHours, // Log actual for history
                    standard_time: st,
                    efficiency: efficiency + '%',
                    complexity: complexity,
                    proof: proof,
                    reward: reward,
                    minter: appState.currentUser.name
                })
            }).then(function (res) { return res.json(); })
                .then(function (data) {
                    if (data.status === 'success') {
                        appState.balance += reward;
                        appState.xp += Math.round(reward);
                        saveState(); updateUI();

                        var msg = `[MINT] ${taskName}\nReward: ${reward} AT\nEfficiency: ${efficiency}%`;
                        if (efficiency > 100) msg += " 🔥 (High Performance!)";
                        if (efficiency < 50) msg += " ⚠️ (Low Performance)";

                        logToTerminal(msg);
                        form.reset();
                        // Reset Dropdown
                        document.getElementById('task-select').value = 'custom';
                        updateTaskInfo();
                    }
                });
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            if (confirm('Clear all data?')) {
                localStorage.clear();
                appState = { balance: 0, history: [], currentUser: { name: 'Guest', role: 'worker' } };
                updateUI();
                if (loginOverlay) loginOverlay.style.display = 'flex';
            }
        });
    }

    function loadState() {
        var saved = localStorage.getItem('abundanceState');
        if (saved) {
            var parsed = JSON.parse(saved);
            appState.balance = parsed.balance || 0;
            appState.history = parsed.history || [];
            appState.xp = parsed.xp || 0;
            appState.tasks = parsed.tasks || []; // Load tasks
        }

        // Load default SEH7 tasks if empty
        if (!appState.tasks || appState.tasks.length === 0) {
            fetch('tasks.json')
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    appState.tasks = data;
                    saveState();
                    updateUI();
                })
                .catch(function (err) { console.error("Failed to load tasks", err); });
        }
    }

    function saveState() {
        localStorage.setItem('abundanceState', JSON.stringify({ balance: appState.balance, history: appState.history, xp: appState.xp }));
    }

    function updateUI() {
        if (balanceDisplay) balanceDisplay.innerHTML = appState.balance.toFixed(2) + ' <small>AT</small>';
        updateUserUI();
        updateLevelUI();
        renderJobBoard();
    }

    function updateLevelUI() {
        var levelBadge = document.getElementById('level-badge');
        var xpDisplay = document.getElementById('xp-display');
        var xpFill = document.getElementById('xp-fill');
        if (!levelBadge) return;

        var currentLevel = LEVELS[0];
        var nextLevel = LEVELS[1];
        for (var i = LEVELS.length - 1; i >= 0; i--) {
            if (appState.xp >= LEVELS[i].threshold) {
                currentLevel = LEVELS[i];
                nextLevel = LEVELS[i + 1] || LEVELS[i];
                break;
            }
        }

        var levelNum = LEVELS.indexOf(currentLevel) + 1;
        levelBadge.textContent = currentLevel.icon + ' Lv.' + levelNum + ' ' + currentLevel.name;

        var xpInLevel = appState.xp - currentLevel.threshold;
        var xpNeeded = nextLevel.threshold - currentLevel.threshold;
        var percent = Math.min(100, Math.round((xpInLevel / xpNeeded) * 100));

        if (xpDisplay) xpDisplay.textContent = appState.xp + ' / ' + nextLevel.threshold + ' XP';
        if (xpFill) xpFill.style.width = percent + '%';
    }

    function logToTerminal(msg) {
        if (!terminalLog) return;
        var line = document.createElement('div');
        line.className = 'log-line';
        line.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
        terminalLog.prepend(line);
    }

    init();
});

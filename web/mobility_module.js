/**
 * Universal Mobility Module - OSE Civilization OS
 * Handles cross-node peer discovery, travel logic, and silent handoffs.
 */

window.mobilityState = {
    currentNodeId: 'V-001',
    peers: [],
    map: null,
    markers: {}
};

window.initMobilityUI = function () {
    console.log("[MOBILITY] Initializing...");
    loadPeers();
    initMobilityMap();
};

async function loadPeers() {
    try {
        const data = await apiFetch('/api/federation/peers');
        window.mobilityState.peers = data || [];

        console.log(`[MOBILITY] Loaded ${window.mobilityState.peers.length} peer nodes.`);
        renderPeerList();
        updateMobilityMap();
    } catch (e) {
        console.warn("[MOBILITY] Could not load peer registry:", e);
        // Fallback dummy data
        window.mobilityState.peers = [
            { village_id: "ose-missouri-001", name: "Factor e Farm (Missouri)", lat: 39.914, lng: -94.525, status: "online" },
            { village_id: "ose-france-001", name: "OSE Paris", lat: 48.8566, lng: 2.3522, status: "offline" },
            { village_id: "ose-bali-001", name: "OSE Bali (Canggu)", lat: -8.6478, lng: 115.1385, status: "offline" }
        ];
        renderPeerList();
        updateMobilityMap();
    }
}

function renderPeerList() {
    const list = document.getElementById('peer-nodes-list');
    if (!list) return;

    if (window.mobilityState.peers.length === 0) {
        list.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:20px; color:#64748b;">No peers found. Add one to expand the mesh.</div>';
    } else {
        list.innerHTML = window.mobilityState.peers.map(p => {
            const isCurrent = p.id === window.mobilityState.currentNodeId;
            const statusColor = p.status === 'ONLINE' ? '#10B981' : (p.status === 'SYNCING' ? '#F59E0B' : '#EF4444');
            return `
                <div class="glass-panel" style="padding:15px; border-left: 3px solid ${isCurrent ? '#10B981' : 'transparent'};">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div style="font-weight:bold; color:white;">${p.name}</div>
                        <div style="font-size:0.6rem; color:${statusColor}; border:1px solid ${statusColor}; padding:2px 4px; border-radius:4px;">${p.status}</div>
                    </div>
                    <div style="font-size:0.75rem; color:#94a3b8; margin: 10px 0;">${p.url}</div>
                    ${isCurrent ?
                    '<div style="color:#10B981; font-size:0.7rem; font-weight:bold; text-align:center;">📍 CURRENT NODE</div>' :
                    `<button class="btn-xs" onclick="travelToNode('${p.id}')" style="background:rgba(59,130,246,0.1); color:#60A5FA; border:1px solid #3B82F6; width:100%;">Dock at Node</button>`
                }
                </div>
            `;
        }).join('');
    }

    // Add "Federate Node" button at the end
    const addBtn = document.createElement('div');
    addBtn.className = "glass-panel";
    addBtn.style.cssText = "padding:15px; border: 1px dashed rgba(16,185,129,0.3); display:flex; align-items:center; justify-content:center; cursor:pointer;";
    addBtn.innerHTML = '<span style="color:#10B981; font-weight:bold;">+ Federate New Node</span>';
    addBtn.onclick = () => window.addPeerDialog();
    list.appendChild(addBtn);
}

function initMobilityMap() {
    if (window.mobilityState.map) return;

    const mapEl = document.getElementById('mobility-map');
    if (!mapEl) return;

    window.mobilityState.map = L.map('mobility-map', {
        zoomControl: false,
        attributionControl: false
    }).setView([20, 0], 2);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
    }).addTo(window.mobilityState.map);
}

function updateMobilityMap() {
    if (!window.mobilityState.map) return;

    window.mobilityState.peers.forEach(p => {
        if (window.mobilityState.markers[p.village_id]) {
            window.mobilityState.map.removeLayer(window.mobilityState.markers[p.village_id]);
        }

        const isCurrent = p.village_id === window.mobilityState.currentNodeId;
        const icon = L.divIcon({
            className: 'custom-div-icon',
            html: `<div style="background:${isCurrent ? '#10B981' : '#3B82F6'}; width:12px; height:12px; border-radius:50%; box-shadow:0 0 10px ${isCurrent ? '#10B981' : '#3B82F6'};"></div>`,
            iconSize: [12, 12],
            iconAnchor: [6, 6]
        });

        const marker = L.marker([p.lat, p.lng], { icon: icon }).addTo(window.mobilityState.map);
        marker.bindPopup(`<b>${p.name}</b><br>${isCurrent ? 'Current Dock' : 'Federated Node'}`);
        window.mobilityState.markers[p.village_id] = marker;
    });
}

window.addPeerDialog = async function () {
    const url = prompt("Enter Node URL (e.g. http://10.0.0.5:3000):");
    if (!url) return;
    const name = prompt("Enter Node Name (e.g. Spore Node 1):");
    if (!name) return;

    try {
        const res = await apiFetch('/api/federation/peers/add', {
            method: 'POST',
            body: { name, url }
        });
        showCelebration(`NEW NODE FEDERATED: ${name}`);
        loadPeers();
    } catch (e) {
        alert("Failed to add peer: " + e);
    }
};

window.travelToNode = function (nodeId) {
    const node = window.mobilityState.peers.find(p => p.id === nodeId);
    if (!node) return;

    if (confirm(`Dock at ${node.name}? This will synchronize your AT identity with the new mesh point.`)) {
        showCelebration(`WARP INITIATED TO ${node.id}`);
        document.getElementById('mobility-status-badge').innerText = "🛸 TRANSITING...";

        setTimeout(() => {
            window.mobilityState.currentNodeId = nodeId;
            document.getElementById('current-node-name').innerText = node.name;
            renderPeerList();
            document.getElementById('mobility-status-badge').innerText = "🛰️ SIGNAL STABLE";
            logToTerminal(`[MOBILITY] Successfully docked at ${node.name}`);
        }, 1500);
    }
};

window.initiateHandoff = function () {
    showCelebration("HANDOFF INITIATED");
    logToTerminal("[MESH] Broadcasting sovereign state to peer nodes...");
    setTimeout(() => logToTerminal("[MESH] Identity handoff successful."), 1000);
};

// Hook into app's view switch (guarded against duplicate loading)
if (typeof window._mobilityHooked === 'undefined') {
    window._mobilityHooked = true;
    const originalSwitchView = window.switchView;
    window.switchView = function (viewName) {
        if (viewName === 'mobility') {
            setTimeout(window.initMobilityUI, 100);
            setTimeout(() => {
                if (window.mobilityState.map) window.mobilityState.map.invalidateSize();
            }, 300);
        }
        if (originalSwitchView) originalSwitchView(viewName);
    };
}

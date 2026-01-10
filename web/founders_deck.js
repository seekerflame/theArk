/**
 * Founders Deck - High-Intensity Node Management
 * Specialized for Founders, Inc. operational style.
 */

const Founders = {
    templates: [],
    machines: [],

    init: function () {
        console.log("🚀 Founders Deck Initialized");
        this.fetchData();
        this.updateTabVisibility();
    },

    updateTabVisibility: function () {
        const tab = document.getElementById('tab-founders');
        if (!tab) return;

        const user = window.appState.currentUser;
        if (user && (user.role === 'FOUNDER' || user.role === 'ADMIN' || user.role === 'NODE_ADMIN')) {
            tab.style.display = 'block';
        } else {
            tab.style.display = 'none';
        }
    },

    fetchData: async function () {
        try {
            // Fetch Templates
            const templatesData = await window.apiFetch('/api/nodes/templates');
            this.templates = templatesData.templates || [];

            // Fetch Foundry Machines (Labs)
            // Note: Reuse existing hardware/system API if possible, 
            // but we need the foundry specific list for reservations.
            const foundryData = await window.apiFetch('/api/hardware/foundry');
            this.machines = foundryData.machines || [];

            if (document.getElementById('view-founders').style.display !== 'none') {
                this.render();
            }
        } catch (e) {
            console.warn("Founders data fetch failed:", e);
        }
    },

    render: function () {
        const container = document.getElementById('view-founders');
        if (!container) return;

        const user = window.appState.currentUser;

        container.innerHTML = `
            <div class="pip-header" style="border-bottom: 2px solid #FBBF24; padding-bottom: 5px; margin-bottom: 15px;">
                <h2 style="color: #FBBF24; margin:0;">THE LAB // FOUNDERS DECK</h2>
                <div style="font-size: 0.7rem; color: var(--pip-dim);">[RESTRICTED ACCESS] [HIGH INTENSITY ENVIRONMENT]</div>
            </div>

            <div class="pip-grid-2">
                <!-- LEFT COLUMN: Resource Scheduling -->
                <div class="pip-box" style="border-color: #FBBF24;">
                    <h3 style="color: #FBBF24; margin-top:0;">RESERVE ASSETS</h3>
                    <div id="founders-asset-list" style="display: flex; flex-direction: column; gap: 10px;">
                        ${this.renderAssetList()}
                    </div>
                </div>

                <!-- RIGHT COLUMN: Node Operations -->
                <div class="pip-box">
                    <h3 style="margin-top:0;">NODE TEMPLATES</h3>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <select id="template-select" class="btn-pip" style="width: 100%; text-align: left; background: rgba(0,0,0,0.5);">
                            <option value="">-- SELECT TEMPLATE --</option>
                            ${this.templates.map(t => `<option value="${t}">${t.replace('.json', '').toUpperCase()}</option>`).join('')}
                        </select>
                        <button class="btn-pip" onclick="Founders.applyTemplate()" style="border-color: #FBBF24; color: #FBBF24;">APPLY CONFIGURATION</button>
                    </div>

                    <h3 style="margin-top: 20px;">FOUNDER MULTIPLIERS</h3>
                    <div class="pip-stat-row">
                        <span>BASE BOOST</span>
                        <span style="color: #FBBF24;">3.0x AT</span>
                    </div>
                    <div class="pip-stat-row">
                        <span>LAB ACCESS</span>
                        <span style="color: var(--pip-green);">GRANTED</span>
                    </div>
                    
                    <div style="margin-top: 20px; font-size: 0.8rem; color: var(--pip-dim); font-style: italic;">
                        "The goal is not to sustain. The goal is to evolve."
                    </div>
                </div>
            </div>

            <div class="pip-box" style="margin-top: 15px; border-color: #60A5FA;">
                <h3 style="color: #60A5FA; margin-top:0;">SYSTEM VARIABLES (Real-time Editing)</h3>
                <div class="pip-grid-2">
                    <div>
                        <div class="pip-stat-row">
                            <span>MINT_MULTIPLIER</span>
                            <input type="range" id="param-mint-mult" min="0.5" max="5.0" step="0.1" value="1.0" oninput="this.nextElementSibling.innerText = this.value + 'x'" style="flex:1; margin-left:10px;">
                            <span style="width: 40px; text-align: right;">1.0x</span>
                        </div>
                        <div class="pip-stat-row">
                            <span>GLOBAL_TAX_RATE</span>
                            <input type="range" id="param-tax-rate" min="0" max="25" step="1" value="5" oninput="this.nextElementSibling.innerText = this.value + '%'" style="flex:1; margin-left:10px;">
                            <span style="width: 40px; text-align: right;">5%</span>
                        </div>
                    </div>
                    <div>
                        <div class="pip-stat-row">
                            <span>FEDERATION_SYNC</span>
                            <select class="btn-pip" style="padding:2px; font-size:0.8rem; width:100px;">
                                <option>ACTIVE</option>
                                <option>OFFLINE</option>
                            </select>
                        </div>
                        <div class="pip-stat-row">
                            <span>AI_AUTONOMY</span>
                            <select class="btn-pip" style="padding:2px; font-size:0.8rem; width:100px;">
                                <option>GUIDED</option>
                                <option>FULL</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div style="margin-top:10px; text-align:right;">
                    <button class="btn-pip" onclick="alert('System Variables Distributed to Node Mesh!')" style="font-size:0.8rem; border-color:#60A5FA; color:#60A5FA;">PUSH TO MESH</button>
                </div>
            </div>

            <div class="pip-box" style="margin-top: 15px;">
                <h3 style="margin-top:0;">EQUITY MILESTONES</h3>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="text" id="milestone-desc" placeholder="Describe Milestone..." class="btn-pip" style="flex: 1; text-align: left;">
                    <button class="btn-pip" onclick="Founders.submitMilestone()" style="width: auto;">SUBMIT FOR ORACLE AUDIT</button>
                </div>
            </div>
        `;
    },

    renderAssetList: function () {
        const staticAssets = this.machines.filter(m => m.is_static);
        if (staticAssets.length === 0) {
            return `<div style="color: var(--pip-dim); font-size: 0.8rem; text-align:center;">No reservable assets found in this node.</div>`;
        }

        return staticAssets.map(m => `
            <div style="border-bottom: 1px solid var(--pip-dim); padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight:bold; color: var(--pip-green);">${m.name}</div>
                    <div style="font-size:0.7rem; color: var(--pip-dim);">${m.at_cost_per_hour} AT / HR</div>
                </div>
                <div style="display:flex; align-items: center; gap: 5px;">
                    <input type="number" id="duration-${m.name}" value="1" min="1" max="8" style="width: 40px; background: rgba(0,0,0,0.5); border: 1px solid var(--pip-dim); color: var(--pip-green); text-align: center;">
                    <button class="btn-pip" onclick="Founders.reserveAsset('${m.name}')" style="font-size: 0.7rem; padding: 2px 8px;">BOOK</button>
                </div>
            </div>
        `).join('');
    },

    reserveAsset: async function (assetName) {
        const duration = parseInt(document.getElementById(`duration-${assetName}`).value);
        if (!duration) return;

        try {
            const res = await window.apiFetch('/api/hardware/foundry/reserve', {
                method: 'POST',
                body: { asset_name: assetName, duration_hours: duration }
            });

            if (res.status === 'success') {
                alert(`SUCCESS: ${assetName} reserved for ${duration}h.\nCost: ${res.cost} AT`);
                this.fetchData(); // Refresh UI
            } else {
                alert("Reservation Failed: " + res.message);
            }
        } catch (e) {
            alert("Reservation Error: " + e.message);
        }
    },

    applyTemplate: async function () {
        const template = document.getElementById('template-select').value;
        if (!template) return alert("Select a template first.");

        if (!confirm(`CAUTION: Applying ${template} will override node configurations. Proceed?`)) return;

        try {
            const res = await window.apiFetch('/api/nodes/apply_template', {
                method: 'POST',
                body: { template: template }
            });

            if (res.status === 'success') {
                alert(`Node configuration updated via template: ${template}`);
                location.reload(); // Reload to apply all role/config changes
            }
        } catch (e) {
            alert("Apply Template Error: " + e.message);
        }
    },

    submitMilestone: function () {
        const desc = document.getElementById('milestone-desc').value;
        if (!desc) return;
        alert("Milestone submitted to Oracle for validation. Reward will be minted upon consensus.");
        document.getElementById('milestone-desc').value = '';
    }
};

// Auto-init tab visibility when state changes
if (window.appState) {
    Founders.updateTabVisibility();
}

/**
 * Gaia Hardware Monitor Module
 * Visualizes real-time status and yield from infrastructure sensors.
 */

(function () {
    window.initHardwareMonitor = function () {
        const container = document.getElementById('hardware-monitor-container');
        if (!container) return;

        // Build the HUD
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <!-- Solar Gauge -->
                <div class="glass-panel" style="text-align: center; border-top: 3px solid #FBBF24;">
                    <div style="font-size: 2.5rem;">☀️</div>
                    <div id="solar-value" style="font-family: 'JetBrains Mono', monospace; font-size: 2rem; color: #FBBF24; margin: 10px 0;">0.00 W</div>
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;">Solar Array 01</div>
                    <div class="xp-bar-premium" style="height: 6px; margin-top: 15px;">
                        <div id="solar-fill" class="xp-fill-premium" style="width: 0%; background: #FBBF24; box-shadow: 0 0 10px rgba(251, 191, 36, 0.5);"></div>
                    </div>
                </div>

                <!-- Water Gauge -->
                <div class="glass-panel" style="text-align: center; border-top: 3px solid #3B82F6;">
                    <div style="font-size: 2.5rem;">💧</div>
                    <div id="water-value" style="font-family: 'JetBrains Mono', monospace; font-size: 2rem; color: #3B82F6; margin: 10px 0;">0.00 GPM</div>
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;">Main Pump</div>
                     <div class="xp-bar-premium" style="height: 6px; margin-top: 15px;">
                        <div id="water-fill" class="xp-fill-premium" style="width: 0%; background: #3B82F6; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);"></div>
                    </div>
                </div>

                <!-- Security Cluster -->
                <div class="glass-panel" style="text-align: center; border-top: 3px solid #EF4444;">
                    <div style="font-size: 2.5rem;">🛡️</div>
                    <div id="security-status" style="font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; color: #94a3b8; margin: 15px 0;">STANDBY</div>
                    <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;">Workshop PIR</div>
                    <div id="motion-dot" style="width: 12px; height: 12px; border-radius: 50%; background: #475569; margin: 10px auto; transition: all 0.3s;"></div>
                </div>
            </div>

            <!-- Incident Ledger -->
            <div class="glass-panel" style="margin-top: 20px;">
                <div class="section-header">
                    <h3>🛠️ Infrastructure Logs</h3>
                    <span class="badge" id="hardware-count">0 Pulse Events</span>
                </div>
                <div id="hardware-logs" class="terminal-view" style="max-height: 250px;">
                    <div class="log-entry">Awaiting telemetry handshake...</div>
                </div>
            </div>
        `;

        startTelemetryPolling();
    };

    function startTelemetryPolling() {
        if (window.telemetryPoller) clearInterval(window.telemetryPoller);

        window.telemetryPoller = setInterval(() => {
            fetch('/api/graph')
                .then(r => r.json())
                .then(blocks => {
                    if (!Array.isArray(blocks)) {
                        console.warn("[HARDWARE] /api/graph returned invalid data:", blocks);
                        return;
                    }
                    const hwBlocks = blocks.filter(b => b.data && b.data.block_type === 'HARDWARE_PROOF')
                        .sort((a, b) => b.timestamp - a.timestamp);

                    updateHUD(hwBlocks);
                    renderLogs(hwBlocks.slice(0, 10));
                });
        }, 5000);
    }

    function updateHUD(blocks) {
        if (blocks.length === 0) return;

        // Find latest for each type
        const solar = blocks.find(b => b.data.sensor_type === 'SOLAR_GEN');
        const water = blocks.find(b => b.data.sensor_type === 'WATER_PUMP');
        const security = blocks.find(b => b.data.sensor_type === 'WORKSHOP_PRESENCE');

        if (solar) {
            const watts = solar.data.raw_data.power_w;
            document.getElementById('solar-value').innerText = `${watts.toFixed(2)} W`;
            const percent = Math.min(100, (watts / 500) * 100);
            document.getElementById('solar-fill').style.width = `${percent}%`;
        }

        if (water) {
            const gpm = water.data.raw_data.flow_rate_gpm || water.data.raw_data.gallons;
            document.getElementById('water-value').innerText = `${gpm.toFixed(2)} GPM`;
            const percent = Math.min(100, (gpm / 100) * 100);
            document.getElementById('water-fill').style.width = `${percent}%`;
        }

        if (security) {
            const motion = security.data.raw_data.hours > 0;
            const statusEl = document.getElementById('security-status');
            const dotEl = document.getElementById('motion-dot');

            if (motion) {
                statusEl.innerText = "ACTIVE";
                statusEl.style.color = "#EF4444";
                dotEl.style.background = "#EF4444";
                dotEl.style.boxShadow = "0 0 15px #EF4444";
            } else {
                statusEl.innerText = "STANDBY";
                statusEl.style.color = "#94a3b8";
                dotEl.style.background = "#475569";
                dotEl.style.boxShadow = "none";
            }
        }

        document.getElementById('hardware-count').innerText = `${blocks.length} Pulse Events`;
    }

    function renderLogs(blocks) {
        const logContainer = document.getElementById('hardware-logs');
        if (!logContainer) return;

        logContainer.innerHTML = blocks.map(b => `
            <div class="log-entry">
                <span style="color:#10B981;">[ telemetry ]</span> 
                <strong>${b.data.task}</strong>
                <div class="meta">${new Date(b.timestamp * 1000).toLocaleTimeString()} | Hash: ${b.hash.substring(0, 8)}</div>
            </div>
        `).join('');
    }
})();

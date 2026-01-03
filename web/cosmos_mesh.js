/**
 * Mesh Visualizer - Ark OS
 * Force-directed graph for village node topology.
 */

const canvas = document.getElementById('mesh-canvas');
const ctx = canvas.getContext('2d');
const peerCountEl = document.getElementById('peer-count');

let width, height;
let nodes = [];
let links = [];

const simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(150))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter());

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    simulation.force("center").x(width / 2).y(height / 2);
}

window.addEventListener('resize', resize);
resize();

// Simulation Node Data - Polling from API
async function refreshSimulation() {
    try {
        const response = await fetch('/api/federation/peers');
        const peers = await response.json();

        if (!Array.isArray(peers)) return;

        // Transform peers to nodes
        const newNodes = [
            { id: "Ark_Prime", type: "prime", label: "Ark Prime", status: "online" },
            ...peers.map(p => ({
                id: p.village_id || p.id,
                type: "node",
                label: p.name,
                status: p.status.toLowerCase()
            }))
        ];

        // Simple Links: All connected to Prime for now (Star Topology)
        const newLinks = peers.map(p => ({
            source: "Ark_Prime",
            target: p.village_id || p.id
        }));

        // Update Simulation
        nodes = newNodes;
        links = newLinks;

        if (peerCountEl) peerCountEl.textContent = nodes.length;

        simulation.nodes(nodes);
        simulation.force("link").links(links);
        simulation.alpha(0.3).restart();

    } catch (e) {
        console.warn("[MESH] Peer fetch failed:", e);
    }
}

// Start Polling
function initSimulation() {
    // Initial state
    nodes = [{ id: "Ark_Prime", type: "prime", label: "Ark Prime", status: "online" }];
    links = [];

    simulation.nodes(nodes);
    simulation.force("link").links(links);
    simulation.on("tick", render);

    refreshSimulation();
    setInterval(refreshSimulation, 10000); // Poll every 10s
}

window.renderCosmicMesh = function () {
    resize();
    simulation.alpha(1).restart();
};

initSimulation();

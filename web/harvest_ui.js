/**
 * Harvest Marketplace UI
 * Handles rendering produce, seeds, and plants.
 */

const HarvestUI = {
    init() {
        console.log("🥬 Harvest UI Initialized");
        this.fetchListings();
    },

    async fetchListings() {
        const container = document.getElementById('harvest-listings-container');
        if (!container) return;

        try {
            // In a real app, this calls /api/harvest/available
            // For now, we use our mock seeds.json + some generated produce
            const response = await fetch('seeds.json');
            const seeds = await response.json();

            const produce = [
                { id: 'h1', title: 'Organic Lemons', quantity: '5 lbs', price_at: 0.5, seller: 'Dagny', category: 'fruits' },
                { id: 'h2', title: 'Farm Fresh Eggs', quantity: '1 dozen', price_at: 1.0, seller: 'Rudy', category: 'eggs' }
            ];

            const allListings = [...seeds, ...produce];
            this.renderListings(allListings);
        } catch (e) {
            container.innerHTML = `<div class="pip-box" style="color: red;">Error loading marketplace: ${e.message}</div>`;
        }
    },

    renderListings(listings) {
        const container = document.getElementById('harvest-listings-container');
        if (!container) return;

        container.innerHTML = listings.map(item => `
            <div class="pip-box" style="border-style: dashed; position: relative;">
                <div style="position: absolute; top: 5px; right: 5px; font-size: 0.8rem; color: var(--pip-dim);">${item.category || 'seeds'}</div>
                <h4 style="margin: 0; color: var(--pip-green);">${item.title || item.name}</h4>
                <p style="margin: 5px 0; font-size: 0.9rem;">${item.description || item.variety || ''}</p>
                <div class="pip-stat-row">
                    <span>QTY: ${item.quantity}</span>
                    <span style="font-weight: bold;">${item.price_at || item.price} AT</span>
                </div>
                <div class="pip-stat-row" style="font-size: 0.8rem; opacity: 0.7;">
                    <span>BY: ${item.seller || item.provider}</span>
                </div>
                <button class="btn-pip" style="width: 100%; margin-top: 10px;" onclick="window.buyHarvestItem('${item.id}')">BARTER</button>
            </div>
        `).join('');
    }
};

window.buyHarvestItem = (id) => {
    alert(`Barter initiated for item ${id}. Check your Radio for pickup instructions!`);
};

window.renderPostHarvestModal = () => {
    alert("Listing Creation: Select Category [Seeds/Plants/Produce]...");
};

// Initialize when tab is clicked
window.switchPipTabHook = (tab) => {
    if (tab === 'harvest') {
        HarvestUI.init();
    }
};

window.HarvestUI = HarvestUI;

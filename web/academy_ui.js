/**
 * OSE Academy UI - Handles Skill Tree and Wisdom Synthesis.
 */

const AcademyUI = {
    init() {
        console.log("🎓 OSE Academy Initialized");
        this.loadSkillTree();
        this.loadWisdom();
    },

    async loadSkillTree() {
        const container = document.getElementById('academy-skill-tree');
        if (!container) return;

        try {
            const res = await fetch('/api/academy/tree');
            const data = await res.json();

            // Render Mermaid (assuming mermaid is loaded in index.html)
            if (window.mermaid) {
                container.innerHTML = `<div class="mermaid">${data.data.mermaid}</div>`;
                window.mermaid.contentLoaded();
            } else {
                container.innerHTML = "<pre>" + data.data.mermaid + "</pre>";
            }
        } catch (e) {
            console.error("Failed to load skill tree", e);
        }
    },

    async loadWisdom() {
        const snippetEl = document.getElementById('academy-wisdom-snippet');
        if (!snippetEl) return;

        try {
            const res = await fetch('/api/academy/wisdom');
            const data = await res.json();
            const wisdom = data.data;

            snippetEl.innerHTML = `
                <div class="pip-box" style="border-color: var(--pip-green);">
                    <div style="font-size: 0.8rem; color: var(--pip-dim); text-transform: uppercase;">Source: ${wisdom.source}</div>
                    <p style="font-size: 1.2rem; margin: 10px 0;">${wisdom.text}</p>
                    <button class="btn-pip" onclick="AcademyUI.showSynthesisModal('${wisdom.text}', '${wisdom.source}')">PROVE SYNTHESIS</button>
                </div>
            `;
        } catch (e) {
            console.error("Failed to load wisdom", e);
        }
    },

    showSynthesisModal(text, source) {
        const synthesis = prompt(`SYNTHESIS LOG:\n\nTopic: ${source}\n\nSummarize how this ideal accelerates your future autonomy:`);
        if (synthesis) {
            this.submitSynthesis(synthesis, source);
        }
    },

    async submitSynthesis(text, source) {
        try {
            const res = await fetch('/api/academy/synthesis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('ark_token')}`
                },
                body: JSON.stringify({ text, source })
            });
            const result = await res.json();
            if (result.status === 'success') {
                alert(`SYNTHESIS VALIDATED. +${result.data.reward} AT Minted.`);
                this.loadWisdom(); // Load next snippet
                if (window.refreshBalance) window.refreshBalance();
            }
        } catch (e) {
            alert("Synthesis failed: " + e.message);
        }
    }
};

// Global hook for tab switching
window.switchPipTabHook = (tab) => {
    if (tab === 'academy') {
        AcademyUI.init();
    }
    // Handle other hooks (Harvest, etc.) if they exist
    if (window.HarvestUI && tab === 'harvest') HarvestUI.init();
};

window.AcademyUI = AcademyUI;

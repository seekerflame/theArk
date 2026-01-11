
const PassportUI = {
    render: async () => {
        const container = document.getElementById('passport-container');
        if (!container) return;

        try {
            const resp = await apiFetch('/api/ark/passport/status');
            const data = resp.data;

            if (data.status === "PENDING" || !data.passport_id) {
                container.innerHTML = `
                    <div class="passport-pending">
                        <h3>NO ACTIVE PASSPORT</h3>
                        <p>Citizenship Status: <b>UNVERIFIED</b></p>
                        <button onclick="PassportUI.request()">REQUEST PASSPORT</button>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="passport-issued">
                        <div class="passport-header">ARK PASSPORT</div>
                        <div class="passport-id">${data.passport_id}</div>
                        <div class="passport-body">
                            <p>NAME: ${data.username}</p>
                            <p>LEVEL: ${data.level}</p>
                            <p>ISSUED: ${new Date(data.issued_at * 1000).toLocaleDateString()}</p>
                        </div>
                        <div class="passport-footer">PROOF OF PERSONHOOD VERIFIED</div>
                        <button class="attest-btn" onclick="PassportUI.showAttestDialog()">ATTEST FOR PEER</button>
                    </div>
                `;
            }
        } catch (err) {
            container.innerHTML = `<p class="error">Failed to load passport status.</p>`;
        }
    },

    request: async () => {
        const resp = await apiFetch('/api/ark/passport/request', { method: 'POST' });
        alert(resp.data.message);
        PassportUI.render();
    },

    showAttestDialog: async () => {
        const target = prompt("Target Username to Attest:");
        if (!target) return;

        // Get Presence Token first (Scan local environment)
        try {
            const pResp = await apiFetch('/api/ark/passport/at_token', { method: 'POST' });
            const token = pResp.data.presence_token;

            const resp = await apiFetch('/api/ark/passport/attest', {
                method: 'POST',
                body: JSON.stringify({ target, presence_token: token })
            });

            if (resp.status === "success") {
                alert(`SUCCESS: Attestation recorded for ${target}.`);
            } else {
                alert(`ERROR: ${resp.message}`);
            }
        } catch (err) {
            alert("Sensing failure: Presence token unreachable.");
        }
    }
};

window.renderPassport = PassportUI.render;

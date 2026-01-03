// LIVE ACTIVITY FEED - Social Proof System
// Shows real-time village activity to create FOMO and engagement

window.activityFeed = [];

window.logActivity = function (type, user, data) {
    const activity = {
        type: type, // 'MINT', 'PURCHASE', 'JOIN_PARTY', 'ACHIEVEMENT'
        user: user,
        data: data,
        timestamp: Date.now()
    };

    activityFeed.unshift(activity);
    if (activityFeed.length > 50) activityFeed.pop(); // Keep last 50

    updateActivityFeed();

    // Save to localStorage
    localStorage.setItem('activityFeed', JSON.stringify(activityFeed));
};

function updateActivityFeed() {
    const feedEl = document.getElementById('activity-feed');
    if (!feedEl) return;

    const icons = {
        'MINT': '💰',
        'PURCHASE': '🛒',
        'JOIN_PARTY': '🤝',
        'ACHIEVEMENT': '🏆',
        'QUEST_COMPLETE': '✅',
        'HARDWARE_PROOF': '⚡',
        'LORA_SYNC': '📡',
        'MESSAGE': '💬'
    };

    const messages = {
        'MINT': (a) => `minted ${a.data.hours}h (${a.data.at} AT)`,
        'PURCHASE': (a) => `bought ${a.data.item} for ${a.data.at} AT`,
        'JOIN_PARTY': (a) => `joined party for "${a.data.quest}"`,
        'ACHIEVEMENT': (a) => `unlocked ${a.data.name}`,
        'QUEST_COMPLETE': (a) => `completed "${a.data.quest}"`,
        'HARDWARE_PROOF': (a) => `sensor ${a.data.sensor_id}: ${a.data.at_earned} AT`,
        'LORA_SYNC': (a) => `synced block from ${a.data.village}`,
        'MESSAGE': (a) => `[${a.data.channel}] ${a.data.content?.substring(0, 50)}...`
    };

    feedEl.innerHTML = activityFeed.slice(0, 10).map(a => {
        const timeAgo = getTimeAgo(a.timestamp);
        const icon = icons[a.type] || '📣';
        const msg = messages[a.type] ? messages[a.type](a) : 'did something';

        return `
            <div style="padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem;">
                <span style="opacity: 0.7; font-size: 0.75rem;">${timeAgo}</span> - 
                <span style="color: var(--primary); font-weight: 600;">${a.user}</span> 
                ${icon} ${msg}
            </div>
        `;
    }).join('') || '<div style="text-align:center; color: #64748b; padding: 20px;">No recent activity</div>';
}

function getTimeAgo(timestamp) {
    const diff = Date.now() - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
}

// Load from localStorage on init
try {
    const saved = localStorage.getItem('activityFeed');
    if (saved) window.activityFeed = JSON.parse(saved);
} catch (e) { }

// Auto-refresh every 10 seconds
setInterval(updateActivityFeed, 10000);

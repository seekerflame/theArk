// ENGAGEMENT SYSTEM: Sovereign Incentives v2.0
// This transforms "operating a node" into "ascending civilization"

window.quickMint = function (hours, taskId) {
    const user = window.window.appState.currentUser;
    if (!user || user.name === 'Guest') {
        alert("🔒 Sovereign Identity required for labor claims.");
        return;
    }

    fetch('/api/mint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: user.name,
            task: taskId || "General Labor",
            hours: hours
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.status === "success" || data.status === "queued") {
                const xpGain = hours * 25;
                const atGain = hours * 10;

                showCelebration(`+${atGain} AT Earned!`);
                showXPFloat(xpGain);

                window.appState.xp += xpGain;
                checkAchievements('FIRST_MINT');

                if (window.appState.streak > 0) window.appState.xp += 10; // Streak bonus

                saveState();
                updateUI();
                syncWithLedger();
            } else {
                alert(data.message);
            }
        });
};

const ACHIEVEMENTS = {
    FIRST_SEED: { name: "🌱 Genesis Node", desc: "Identity established on the mesh.", at_reward: 5, xp_reward: 100 },
    FIRST_MINT: { name: "💰 Labor Proof", desc: "Successfully minted your first labor block.", at_reward: 10, xp_reward: 200 },
    TEAM_PLAYER: { name: "🤝 Federation Link", desc: "Collaborated on a sovereign quest.", at_reward: 15, xp_reward: 250 },
    MERCHANT: { name: "🛒 Trade Route", desc: "Listed an item in the Mycelium.", at_reward: 20, xp_reward: 300 },
    STREAK_3: { name: "🔥 Momentum", desc: "3-day consistent operational streak.", at_reward: 25, xp_reward: 500 },
    STREAK_7: { name: "🔥🔥 Civilization Builder", desc: "7-day continuous mission advancement.", at_reward: 100, xp_reward: 1500 }
};

window.checkAchievements = function (achievementId) {
    if (!window.appState.achievements) window.appState.achievements = [];
    if (window.appState.achievements.includes(achievementId)) return;

    const ach = ACHIEVEMENTS[achievementId];
    if (ach) {
        window.appState.achievements.push(achievementId);
        window.appState.balance += ach.at_reward;
        window.appState.xp += ach.xp_reward;

        showAchievementPopup(ach);
        logToTerminal(`[EVOLUTION] ${ach.name} unlocked! (+${ach.at_reward} AT, +${ach.xp_reward} XP)`);
        saveState();
        updateUI();
    }
};

function showAchievementPopup(achievement) {
    const popup = document.createElement('div');
    popup.className = 'achievement-popup';
    popup.innerHTML = `
        <div style="font-size: 64px; margin-bottom: 20px;">${achievement.name.split(' ')[0]}</div>
        <div style="font-size: 24px; font-weight: 800; color: #fff; margin-bottom: 8px; letter-spacing: -0.02em;">${achievement.name}</div>
        <div style="font-size: 16px; color: var(--text-muted); margin-bottom: 24px;">${achievement.desc}</div>
        <div style="display: flex; gap: 12px; justify-content: center;">
            <div style="background: rgba(16, 185, 129, 0.1); color: var(--primary); padding: 10px 20px; border-radius: 12px; font-weight: 800; border: 1px solid var(--primary-glow);">
                +${achievement.at_reward} AT
            </div>
            <div style="background: rgba(139, 92, 246, 0.1); color: var(--secondary); padding: 10px 20px; border-radius: 12px; font-weight: 800; border: 1px solid var(--secondary-glow);">
                +${achievement.xp_reward} XP
            </div>
        </div>
    `;
    document.body.appendChild(popup);

    setTimeout(() => {
        popup.style.opacity = '0';
        popup.style.transform = 'translate(-50%, -60%) scale(0.9)';
        popup.style.transition = 'all 0.5s ease';
        setTimeout(() => popup.remove(), 500);
    }, 4000);
}

window.showXPFloat = function (amount) {
    const float = document.createElement('div');
    float.className = 'xp-float';
    float.style.left = '50%';
    float.style.top = '40%';
    float.textContent = `+${amount} XP`;
    document.body.appendChild(float);
    setTimeout(() => float.remove(), 2000);
};

window.updateStreak = function () {
    const today = new Date().toDateString();
    const lastActive = window.appState.lastActiveDate || "";
    const yesterday = new Date(Date.now() - 86400000).toDateString();

    if (lastActive === today) return;

    if (lastActive === yesterday) {
        window.appState.streak = (window.appState.streak || 0) + 1;
    } else {
        window.appState.streak = 1;
    }

    window.appState.lastActiveDate = today;
    saveState();

    if (window.appState.streak === 3) checkAchievements('STREAK_3');
    if (window.appState.streak === 7) checkAchievements('STREAK_7');

    updateStreakUI();
};

function updateStreakUI() {
    const streakEl = document.getElementById('streak-display');
    if (streakEl) {
        const streak = window.appState.streak || 0;
        const fires = streak >= 7 ? '🔥🔥🔥' : (streak >= 3 ? '🔥🔥' : '🔥');
        streakEl.innerHTML = `<span style="color: var(--warning); font-weight: 800;">${fires} ${streak} DAY MISSION STREAK</span>`;
    }
}

function showCelebration(message) {
    const cel = document.createElement('div');
    cel.className = 'xp-float';
    cel.style.color = 'var(--primary)';
    cel.style.fontSize = '32px';
    cel.style.left = '50%';
    cel.style.top = '30%';
    cel.textContent = message;
    document.body.appendChild(cel);
    setTimeout(() => cel.remove(), 2000);
}

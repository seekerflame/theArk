/**
 * Focus Mode - Inspired by MATLAB "FocusApp"
 * Handles Deep Work sessions with Liveness Tracking and Staking.
 */

const FocusMode = {
    timer: null,
    duration: 25 * 60, // Default 25 mins
    remaining: 0,
    idleTime: 0,
    lastActivity: Date.now(),
    isActive: false,
    sessionStart: null,

    init() {
        console.log("🧘 Focus Mode Initialized");
        this.bindEvents();
    },

    bindEvents() {
        // Track liveness (Mouse/Keyboard)
        window.addEventListener('mousemove', () => this.recordActivity());
        window.addEventListener('keydown', () => this.recordActivity());
    },

    recordActivity() {
        if (this.isActive) {
            this.lastActivity = Date.now();
        }
    },

    async start(mins = 25) {
        if (this.isActive) return;

        this.duration = mins * 60;
        this.remaining = this.duration;
        this.idleTime = 0;
        this.isActive = true;
        this.sessionStart = Date.now();

        // Optional: Stake tokens (would require API call)
        // const success = await this.stakeTokens(5); 

        this.timer = setInterval(() => this.tick(), 1000);
        this.updateUI();

        // Notify System
        System.notify("Focus Started", `Good luck with your ${mins}m session.`);
    },

    tick() {
        if (this.remaining <= 0) {
            this.complete();
            return;
        }

        this.remaining--;

        // Idle detection (inspired by MATLAB code)
        const now = Date.now();
        if (now - this.lastActivity > 2000) { // 2 seconds of stillness
            this.idleTime++;
        }

        this.updateUI();
    },

    async stop() {
        if (!this.isActive) return;

        clearInterval(this.timer);
        this.isActive = false;

        const reflection = prompt("Why did you stop early? (Reflection is required to keep your progress)");

        if (reflection) {
            await this.logSession(reflection, "stopped_early");
            System.notify("Focus Stopped", "Reflection recorded.");
        } else {
            System.notify("Focus Failed", "No reflection provided. Progress lost.");
        }

        this.updateUI();
    },

    async complete() {
        clearInterval(this.timer);
        this.isActive = false;

        const focusScore = ((this.duration - this.idleTime) / this.duration * 100).toFixed(2);

        System.notify("Focus Complete! ✨", `Focus Score: ${focusScore}%. Minting 1 AT...`);

        await this.logSession("Complete", "completed", focusScore);

        // Mint reward (Call API)
        try {
            await API.post('/api/mint', { amount: 1, memo: `Deep Work (${this.duration / 60}m)` });
        } catch (e) {
            console.error("Failed to mint focus reward", e);
        }

        this.updateUI();
    },

    async logSession(reflection, status, score = 0) {
        const data = {
            duration: this.duration,
            idleTime: this.idleTime,
            status: status,
            reflection: reflection,
            score: score,
            timestamp: Date.now()
        };
        console.log("Saving Focus Log:", data);
        // await API.post('/api/focus/log', data);
    },

    updateUI() {
        const el = document.getElementById('focus-timer');
        if (!el) return;

        const mins = Math.floor(this.remaining / 60);
        const secs = this.remaining % 60;
        el.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        const statusEl = document.getElementById('focus-status');
        if (statusEl) {
            statusEl.innerText = this.isActive ? "🧘 ACTIVE" : "💤 IDLE";
        }

        // Update SVG circle (440 is approx circumference for r=70)
        const circle = document.getElementById('focus-progress-circle');
        if (circle) {
            const circumference = 440;
            const offset = circumference * (this.remaining / this.duration);
            circle.style.strokeDashoffset = offset || 0;
        }

        // Random quotes (MATLAB style) - only update on init or complete
        if (!this.isActive && (this.remaining === 0 || this.remaining === this.duration)) {
            const quotes = [
                "Consistency is key.",
                "Rest is productive.",
                "Stay focused, you got this.",
                "Small steps make big changes."
            ];
            const qEl = document.getElementById('focus-quote');
            if (qEl) qEl.innerText = `"${quotes[Math.floor(Math.random() * quotes.length)]}"`;
        }
    }
};

// Auto-init
FocusMode.init();

window.FocusMode = FocusMode;
export default FocusMode;

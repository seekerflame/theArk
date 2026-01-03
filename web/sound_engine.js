// Civilization OS - Sonic Architecture (Sovereign Sound Engine)
// Synthesizes UI sounds using Web Audio API to avoid external asset dependencies.

// Guard against duplicate declarations
if (typeof window.AudioEngine === 'undefined') {
    window.AudioEngine = {
        ctx: null,

        init: function () {
            if (!this.ctx) {
                this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            }
        },

        // Standard UI Click (Mechanical/Sharp)
        playClick: function () {
            if (!this.ctx) this.init();
            const t = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.type = 'square';
            osc.frequency.setValueAtTime(800, t);
            osc.frequency.exponentialRampToValueAtTime(300, t + 0.05);

            gain.gain.setValueAtTime(0.05, t);
            gain.gain.exponentialRampToValueAtTime(0.01, t + 0.05);

            osc.start(t);
            osc.stop(t + 0.05);
        },

        // Hover Effect (Subtle High-Tech Blip)
        playHover: function () {
            if (!this.ctx) this.init();
            if (this.ctx.state === 'suspended') this.ctx.resume();

            const t = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.type = 'sine';
            osc.frequency.setValueAtTime(1200, t);
            osc.frequency.linearRampToValueAtTime(1800, t + 0.03);

            gain.gain.setValueAtTime(0.02, t);
            gain.gain.linearRampToValueAtTime(0, t + 0.03);

            osc.start(t);
            osc.stop(t + 0.03);
        },

        // Success/Mint (Positive Chord)
        playSuccess: function () {
            if (!this.ctx) this.init();
            const t = this.ctx.currentTime;
            const notes = [440, 554, 659]; // A Major

            notes.forEach((freq, i) => {
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, t + (i * 0.05));

                gain.gain.setValueAtTime(0.1, t);
                gain.gain.exponentialRampToValueAtTime(0.001, t + 0.5);

                osc.start(t);
                osc.stop(t + 0.6);
            });
        },

        // Notification (Soft Ping)
        playPing: function () {
            if (!this.ctx) this.init();
            const t = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, t);

            gain.gain.setValueAtTime(0.1, t);
            gain.gain.exponentialRampToValueAtTime(0.001, t + 0.4);

            osc.start(t);
            osc.stop(t + 0.4);
        }
    };

    // Auto-Bind to UI Elements
    document.addEventListener('DOMContentLoaded', () => {
        // Buttons
        document.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('mouseenter', () => window.AudioEngine.playHover());
            btn.addEventListener('click', () => window.AudioEngine.playClick());
        });

        // Inputs
        document.querySelectorAll('input').forEach(inp => {
            inp.addEventListener('focus', () => window.AudioEngine.playHover());
        });
    });
} // End AudioEngine guard

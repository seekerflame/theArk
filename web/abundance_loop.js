
const AbundanceLoop = {
    init: function () {
        this.render();
        setInterval(() => this.update(), 5000); // Pulse every 5s
    },

    render: function () {
        const container = document.getElementById('view-stat');
        if (!container) return;

        // Check if loop-container already exists
        if (document.getElementById('abundance-loop-svg')) return;

        const loopBox = document.createElement('div');
        loopBox.className = 'pip-box';
        loopBox.style.marginTop = '20px';
        loopBox.style.borderColor = '#FBBF24';
        loopBox.innerHTML = `
            <h3 style="color: #FBBF24; margin: 0; border-bottom: 1px solid #FBBF24;">THE ABUNDANCE LOOP</h3>
            <div id="abundance-loop-viz" style="width: 100%; height: 120px; display: flex; align-items: center; justify-content: space-around; position: relative; overflow: hidden;">
                <!-- SVG Viz Injected Here -->
            </div>
            <div id="abundance-loop-stats" style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #FBBF24; font-family: 'VT323';">
                <span>SUN: <span id="loop-sun-val">--</span>W</span>
                <span>BATTERY: <span id="loop-bat-val">--</span>%</span>
                <span>MINTING: <span id="loop-mint-val">--</span> AT</span>
            </div>
        `;

        container.appendChild(loopBox);
        this.drawSVG();
    },

    drawSVG: function () {
        const viz = document.getElementById('abundance-loop-viz');
        const width = viz.clientWidth;
        const height = 120;

        const svg = d3.select("#abundance-loop-viz")
            .append("svg")
            .attr("id", "abundance-loop-svg")
            .attr("width", width)
            .attr("height", height);

        const nodes = [
            { id: 'sun', x: 40, y: 60, icon: '☀️' },
            { id: 'bat', x: width / 3, y: 60, icon: '🔋' },
            { id: 'srv', x: (width / 3) * 2, y: 60, icon: '🖥️' },
            { id: 'at', x: width - 40, y: 60, icon: '💰' }
        ];

        // Draw connections
        svg.selectAll("line")
            .data([
                { s: nodes[0], t: nodes[1] },
                { s: nodes[1], t: nodes[2] },
                { s: nodes[2], t: nodes[3] }
            ])
            .enter()
            .append("line")
            .attr("x1", d => d.s.x + 10)
            .attr("y1", d => d.s.y)
            .attr("x2", d => d.t.x - 10)
            .attr("y2", d => d.t.y)
            .attr("stroke", "var(--pip-dim)")
            .attr("stroke-width", 2)
            .attr("stroke-dasharray", "5,5")
            .attr("id", d => `link-${d.s.id}-${d.t.id}`);

        // Draw nodes
        const g = svg.selectAll("g")
            .data(nodes)
            .enter()
            .append("g")
            .attr("transform", d => `translate(${d.x}, ${d.y})`);

        g.append("circle")
            .attr("r", 20)
            .attr("fill", "#000")
            .attr("stroke", d => d.id === 'at' ? '#FBBF24' : 'var(--pip-green)')
            .attr("stroke-width", 2);

        g.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", ".35em")
            .attr("font-size", "1.2rem")
            .text(d => d.icon);
    },

    update: async function () {
        try {
            // Simulate data for now or fetch from real hardware_monitor.js
            const sun = Math.floor(Math.random() * 400);
            const bat = Math.floor(Math.random() * 100);
            const mint = (sun * 0.01).toFixed(2);

            document.getElementById('loop-sun-val').innerText = sun;
            document.getElementById('loop-bat-val').innerText = bat;
            document.getElementById('loop-mint-val').innerText = mint;

            // Animate pulses along links
            if (sun > 0) this.pulse('sun', 'bat');
            if (bat > 5) this.pulse('bat', 'srv');
            if (sun > 50) this.pulse('srv', 'at');

        } catch (e) { }
    },

    pulse: function (s, t) {
        const svg = d3.select("#abundance-loop-svg");
        const link = document.getElementById(`link-${s}-${t}`);
        if (!link) return;

        const x1 = parseFloat(link.getAttribute('x1'));
        const y1 = parseFloat(link.getAttribute('y1'));
        const x2 = parseFloat(link.getAttribute('x2'));
        const y2 = parseFloat(link.getAttribute('y2'));

        svg.append("circle")
            .attr("r", 3)
            .attr("fill", "#FBBF24")
            .attr("cx", x1)
            .attr("cy", y1)
            .transition()
            .duration(1500)
            .attr("cx", x2)
            .attr("cy", y2)
            .remove();
    }
};

window.AbundanceLoop = AbundanceLoop;

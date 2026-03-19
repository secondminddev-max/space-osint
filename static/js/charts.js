/* ============================================================
   Space OSINT — Chart rendering (Chart.js)
   ============================================================ */

let kpChart = null;

function initKpChart() {
    const ctx = document.getElementById('kp-chart');
    if (!ctx) return;

    kpChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [],
                borderRadius: 2,
                barPercentage: 0.85,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(8,13,28,0.95)',
                    titleColor: '#00c8ff',
                    bodyColor: '#e0e8f0',
                    borderColor: 'rgba(0,200,255,0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: (ctx) => `Kp: ${ctx.parsed.y.toFixed(1)}`
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        color: 'rgba(200,215,230,0.3)',
                        font: { size: 8, family: 'JetBrains Mono' },
                        maxRotation: 0,
                        maxTicksLimit: 8,
                    },
                    grid: { display: false },
                    border: { display: false },
                },
                y: {
                    display: true,
                    min: 0,
                    max: 9,
                    ticks: {
                        color: 'rgba(200,215,230,0.3)',
                        font: { size: 8, family: 'JetBrains Mono' },
                        stepSize: 3,
                    },
                    grid: {
                        color: 'rgba(0,200,255,0.05)',
                        drawBorder: false,
                    },
                    border: { display: false },
                }
            }
        }
    });
}

function kpColor(val) {
    if (val < 4) return '#00ff88';
    if (val < 6) return '#ffd700';
    if (val < 8) return '#ff8c00';
    return '#ff3355';
}

function updateKpChart(history) {
    if (!kpChart || !history || !history.length) return;

    // Show last 16 entries
    const recent = history.slice(-16);
    kpChart.data.labels = recent.map(h => {
        const t = h.time || '';
        return t.substring(11, 16); // HH:MM
    });
    kpChart.data.datasets[0].data = recent.map(h => h.kp);
    kpChart.data.datasets[0].backgroundColor = recent.map(h => kpColor(h.kp));
    kpChart.update('none');
}

// Init on load
document.addEventListener('DOMContentLoaded', initKpChart);

/* ============================================================
   FVEY SDA — Chart Rendering (Chart.js)
   Military Command Centre Display
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
                barPercentage: 0.9,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#000',
                    titleColor: '#FFB000',
                    bodyColor: '#FFFFFF',
                    borderColor: 'rgba(255,176,0,0.3)',
                    borderWidth: 1,
                    titleFont: { family: "'Share Tech Mono'" },
                    bodyFont: { family: "'Share Tech Mono'" },
                    callbacks: {
                        label: (ctx) => `Kp: ${ctx.parsed.y.toFixed(1)}`
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        color: 'rgba(200,210,220,0.25)',
                        font: { size: 7, family: "'Share Tech Mono'" },
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
                        color: 'rgba(200,210,220,0.25)',
                        font: { size: 7, family: "'Share Tech Mono'" },
                        stepSize: 3,
                    },
                    grid: {
                        color: 'rgba(255,176,0,0.05)',
                        drawBorder: false,
                    },
                    border: { display: false },
                }
            }
        }
    });
}

function kpColor(val) {
    if (val < 4) return '#20FF60';
    if (val < 6) return '#FFD700';
    if (val < 8) return '#FF8C00';
    return '#FF2020';
}

function updateKpChart(history) {
    if (!kpChart || !history || !history.length) return;

    const recent = history.slice(-16);
    kpChart.data.labels = recent.map(h => {
        const t = h.time || '';
        return t.substring(11, 16);
    });
    kpChart.data.datasets[0].data = recent.map(h => h.kp);
    kpChart.data.datasets[0].backgroundColor = recent.map(h => kpColor(h.kp));
    kpChart.update('none');
}

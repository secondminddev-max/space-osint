/* ============================================================
   FVEY SDA — SPA Router & System Engine
   Combined Space Operations Center Display
   ============================================================ */

let currentPage = 'cmd';

// ---- UTC Clock ----
function updateClock() {
    const now = new Date();
    const t = now.toISOString().substring(11, 19) + 'Z';
    const d = now.toISOString().substring(0, 10);
    const epoch = Math.floor(now.getTime() / 1000);
    const el1 = document.getElementById('utc-clock');
    const el2 = document.getElementById('utc-date');
    const el3 = document.getElementById('epoch-time');
    if (el1) el1.textContent = t;
    if (el2) el2.textContent = d;
    if (el3) el3.textContent = epoch;
}
setInterval(updateClock, 1000);
updateClock();

// ---- Page routing ----
const pageTitles = {
    cmd: 'COMMAND OVERVIEW',
    adversary: 'ADVERSARY PROFILES',
    orbital: 'ORBITAL THREATS',
    launches: 'LAUNCH MONITOR',
    ground: 'GROUND INFRASTRUCTURE',
    missile: 'ASAT INTELLIGENCE',
    fvey: 'FVEY POSTURE',
    strategy: 'STRATEGIC ANALYSIS',
};

function navigateTo(page) {
    if (!Pages[page]) return;

    // Clean up intervals
    if (window._pageIntervals) {
        window._pageIntervals.forEach(id => clearInterval(id));
    }
    window._pageIntervals = [];

    // Destroy any existing Leaflet maps
    if (typeof satMap !== 'undefined' && satMap) {
        satMap.remove();
        satMap = null;
        satMarkers = [];
    }

    // Destroy any extra maps stored globally
    if (window._extraMaps) {
        window._extraMaps.forEach(m => { try { m.remove(); } catch(e) {} });
        window._extraMaps = [];
    }

    currentPage = page;
    window.location.hash = page;

    // Update tabs
    document.querySelectorAll('.tab').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page);
    });

    // Render page
    const content = document.getElementById('content');
    content.scrollTop = 0;
    Pages[page](content);
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    // Tab click handlers
    document.querySelectorAll('.tab[data-page]').forEach(el => {
        el.addEventListener('click', () => navigateTo(el.dataset.page));
    });

    // Load threat level
    fetch('/api/threat/overview')
        .then(r => r.json())
        .then(d => {
            const badge = document.getElementById('threat-badge');
            if (badge && d.overall_threat_level) {
                const lvl = d.overall_threat_level.toLowerCase();
                badge.textContent = d.overall_threat_level.toUpperCase();
                badge.className = 'sl-val threat-' + lvl;
            }
            const fs = document.getElementById('feed-status');
            if (fs) { fs.textContent = 'ACTIVE'; fs.style.color = 'var(--green)'; }
        })
        .catch(() => {
            const fs = document.getElementById('feed-status');
            if (fs) { fs.textContent = 'DEGRADED'; fs.style.color = 'var(--red)'; }
        });

    // Route from hash or default
    const hash = window.location.hash.replace('#', '');
    navigateTo(hash && Pages[hash] ? hash : 'cmd');

    console.log('[FVEY SDA] Combined Space Operations Center initialized');
});

// Handle back/forward
window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash && Pages[hash] && hash !== currentPage) {
        navigateTo(hash);
    }
});

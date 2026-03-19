/* ============================================================
   Space OSINT — Main Dashboard Application
   Polls API endpoints and updates all dashboard panels
   ============================================================ */

// ---- UTC Clock ----
function updateClock() {
    const now = new Date();
    document.getElementById('utc-clock').textContent =
        now.toUTCString().split(' ')[4] + ' UTC';
}
setInterval(updateClock, 1000);
updateClock();

// ---- Helpers ----
function timeAgo(dateStr) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
}

function countdown(dateStr) {
    const diff = new Date(dateStr).getTime() - Date.now();
    if (diff <= 0) return 'NOW';
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    return `${m}m ${s}s`;
}

function kpColorClass(val) {
    if (val < 4) return 'green';
    if (val < 6) return 'yellow';
    if (val < 8) return 'orange';
    return 'red';
}

function scaleColor(val) {
    val = parseInt(val) || 0;
    if (val === 0) return 'var(--accent-green)';
    if (val <= 2) return 'var(--accent-yellow)';
    if (val <= 3) return 'var(--accent-orange)';
    return 'var(--accent-red)';
}

// ---- Data Fetchers ----

async function fetchJSON(url) {
    try {
        const r = await fetch(url);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return await r.json();
    } catch (e) {
        console.warn(`Fetch failed: ${url}`, e);
        return null;
    }
}

// ---- Panel Updaters ----

async function updateSatellites() {
    const data = await fetchJSON('/api/satellites?group=stations');
    if (data) {
        updateSatelliteMarkers(data);  // from satellite.js — renamed to avoid conflict
    }
}

// Alias for satellite.js function
function updateSatelliteMarkers(data) {
    if (typeof updateSatellites_map === 'function') {
        updateSatellites_map(data);
    } else if (typeof updateSatellites !== 'undefined' && satMap) {
        // Direct call to satellite.js function
        window._satData = data;
    }
}

async function updateStats() {
    const data = await fetchJSON('/api/satellites/stats');
    if (data) {
        document.getElementById('m-tracked').textContent = (data.total_tracked || 0).toLocaleString();
        document.getElementById('m-payloads').textContent = (data.active_payloads || 0).toLocaleString();
        document.getElementById('m-debris').textContent = (data.debris || 0).toLocaleString();
    }
}

async function updateWeather() {
    const data = await fetchJSON('/api/weather');
    if (!data) return;

    // Kp
    const kp = data.kp_current;
    const kpEl = document.getElementById('w-kp');
    const mKp = document.getElementById('m-kp');
    if (kp !== null) {
        kpEl.textContent = kp.toFixed(1);
        kpEl.style.color = `var(--accent-${kpColorClass(kp)})`;
        mKp.textContent = kp.toFixed(1);
        mKp.className = `metric-value ${kpColorClass(kp)}`;
    }

    // Solar wind
    if (data.solar_wind_speed !== null) {
        document.getElementById('w-wind').textContent = Math.round(data.solar_wind_speed);
        document.getElementById('m-wind').textContent = Math.round(data.solar_wind_speed);
    }

    // Bt / Bz
    if (data.bt !== null) document.getElementById('w-bt').textContent = data.bt.toFixed(1);
    if (data.bz !== null) {
        const bzEl = document.getElementById('w-bz');
        bzEl.textContent = data.bz.toFixed(1);
        bzEl.style.color = data.bz < 0 ? 'var(--accent-red)' : 'var(--accent-green)';
    }

    // SFI
    if (data.sfi !== null) document.getElementById('w-sfi').textContent = Math.round(data.sfi);

    // Scales
    if (data.scales) {
        for (const key of ['R', 'S', 'G']) {
            const el = document.getElementById(`scale-${key.toLowerCase()}`);
            const val = data.scales[key]?.Scale || 0;
            el.innerHTML = `${val}<span class="scale-label">${key === 'R' ? 'Radio' : key === 'S' ? 'Solar' : 'Geomag'}</span>`;
            el.style.color = scaleColor(val);
            el.style.borderColor = scaleColor(val);
        }
    }

    // Kp history chart
    if (data.kp_history) {
        updateKpChart(data.kp_history);
    }

    document.getElementById('weather-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
}

async function updateFlares() {
    const data = await fetchJSON('/api/donki/flares');
    if (data && data.length > 0) {
        const latest = data[data.length - 1];
        document.getElementById('w-flare').textContent = latest.class_type || '--';
        const flareEl = document.getElementById('w-flare');
        if (latest.class_type && latest.class_type.startsWith('X')) {
            flareEl.style.color = 'var(--accent-red)';
        } else if (latest.class_type && latest.class_type.startsWith('M')) {
            flareEl.style.color = 'var(--accent-orange)';
        } else {
            flareEl.style.color = 'var(--accent-green)';
        }
    }
}

let _launchData = [];

async function updateLaunches() {
    const data = await fetchJSON('/api/launches');
    if (!data) return;
    _launchData = data;

    document.getElementById('m-launches').textContent = data.length;
    renderLaunches();
    document.getElementById('launches-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
}

function renderLaunches() {
    const body = document.getElementById('launches-body');
    if (!_launchData.length) {
        body.innerHTML = '<div class="error-overlay">NO DATA</div>';
        return;
    }

    body.innerHTML = _launchData.slice(0, 8).map(l => {
        const abbrev = (l.status?.abbrev || 'TBD').toUpperCase();
        let statusClass = 'tbd';
        if (abbrev === 'GO') statusClass = 'go';
        else if (abbrev === 'TBC') statusClass = 'tbc';
        else if (abbrev === 'SUCCESS') statusClass = 'success';
        else if (['HOLD', 'FAILURE'].includes(abbrev)) statusClass = 'hold';

        return `
            <div class="launch-item">
                <div class="launch-name">${l.name || 'Unknown Mission'}</div>
                <div class="launch-provider">${l.provider} &middot; ${l.pad_location || ''}</div>
                <div class="launch-meta">
                    <span class="launch-countdown">${l.net ? countdown(l.net) : 'TBD'}</span>
                    <span class="launch-status ${statusClass}">${abbrev}</span>
                </div>
            </div>
        `;
    }).join('');
}

async function updateNEO() {
    const data = await fetchJSON('/api/neo');
    if (!data) return;

    document.getElementById('m-neo').textContent = data.length;

    const body = document.getElementById('neo-body');
    if (!data.length) {
        body.innerHTML = '<div class="error-overlay">NO CLOSE APPROACHES</div>';
        return;
    }

    const rows = data.slice(0, 15).map(n => {
        const hazClass = n.is_hazardous ? 'hazardous' : '';
        const icon = n.is_hazardous ? '<span class="hazard-icon">&#9888;</span>' : '<span class="safe-icon">&#10003;</span>';
        const distColor = n.miss_distance_lunar < 1 ? 'var(--accent-red)' :
                          n.miss_distance_lunar < 10 ? 'var(--accent-yellow)' : 'var(--accent-green)';

        return `<tr class="${hazClass}">
            <td>${icon} ${n.name}</td>
            <td>${n.close_approach_date ? n.close_approach_date.substring(0, 10) : '--'}</td>
            <td style="color:${distColor}">${n.miss_distance_lunar.toFixed(1)} LD</td>
            <td>${Math.round(n.diameter_max_m)}m</td>
            <td>${n.velocity_kms.toFixed(1)}</td>
        </tr>`;
    }).join('');

    body.innerHTML = `
        <table class="neo-table">
            <thead><tr>
                <th>Object</th>
                <th>Date</th>
                <th>Miss Dist</th>
                <th>Size</th>
                <th>Vel km/s</th>
            </tr></thead>
            <tbody>${rows}</tbody>
        </table>
    `;

    document.getElementById('neo-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
}

async function updateAlerts() {
    const [weather, cme] = await Promise.all([
        fetchJSON('/api/weather'),
        fetchJSON('/api/donki/cme'),
    ]);

    const body = document.getElementById('alerts-body');
    let html = '';

    // SWPC Alerts
    if (weather?.alerts?.length) {
        weather.alerts.slice(-8).reverse().forEach(a => {
            const isCritical = a.message?.includes('Warning') || a.message?.includes('WATCH');
            html += `
                <div class="alert-item ${isCritical ? 'warning' : ''}">
                    <div class="alert-time">${a.issue_datetime || ''} &middot; ${a.product_id || ''}</div>
                    <div class="alert-text">${(a.message || '').substring(0, 200)}</div>
                </div>
            `;
        });
    }

    // CME Events
    if (cme?.length) {
        cme.slice(-5).reverse().forEach(c => {
            html += `
                <div class="alert-item cme">
                    <div class="alert-time">${c.time || ''} &middot; CME</div>
                    <div class="alert-text">
                        ${c.source_location ? 'Source: ' + c.source_location + ' &middot; ' : ''}
                        ${c.speed ? 'Speed: ' + c.speed + ' km/s &middot; ' : ''}
                        ${c.type || ''}
                    </div>
                </div>
            `;
        });
    }

    if (!html) html = '<div class="error-overlay">NO ACTIVE ALERTS</div>';
    body.innerHTML = html;
    document.getElementById('alerts-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
}

async function updateNews() {
    const data = await fetchJSON('/api/news');
    if (!data) return;

    const body = document.getElementById('news-body');
    body.innerHTML = data.slice(0, 10).map(n => `
        <a href="${n.url}" target="_blank" rel="noopener" class="news-item" style="text-decoration:none;color:inherit;">
            ${n.image_url ? `<img src="${n.image_url}" class="news-thumb" alt="" loading="lazy" onerror="this.style.display='none'">` : ''}
            <div class="news-content">
                <div class="news-title">${n.title}</div>
                <div class="news-meta">${n.news_site} &middot; ${n.published_at ? timeAgo(n.published_at) : ''}</div>
            </div>
        </a>
    `).join('');

    document.getElementById('news-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
}

async function updateAstronauts() {
    const data = await fetchJSON('/api/astronauts');
    if (!data) return;

    document.getElementById('m-astro').textContent = data.count || 0;

    const grid = document.getElementById('astronaut-grid');
    grid.innerHTML = (data.people || []).map(p => {
        const initials = p.name.split(' ').map(n => n[0]).join('').substring(0, 2);
        const craftClass = p.craft?.toLowerCase().includes('iss') ? 'iss' :
                          p.craft?.toLowerCase().includes('tiangong') ? 'tiangong' : 'other';
        return `
            <div class="astronaut-card">
                <div class="astronaut-avatar ${craftClass}">${initials}</div>
                <div>
                    <div class="astronaut-name">${p.name}</div>
                    <div class="astronaut-craft">${p.craft}</div>
                </div>
            </div>
        `;
    }).join('');

    document.getElementById('astro-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
}

// ---- Satellite data bridge ----
// satellite.js exposes updateSatellites() globally, but we renamed to avoid collision
async function fetchAndRenderSatellites() {
    const data = await fetchJSON('/api/satellites?group=stations');
    if (data && typeof updateSatellites === 'function') {
        // updateSatellites is from satellite.js
    }
    // Directly call the satellite.js render function
    if (data && satMap) {
        // Remove old, add new — delegated to satellite.js globals
        updateSatellitesOnMap(data);
    }
}

function updateSatellitesOnMap(data) {
    // Delegate to the satellite.js updateSatellites function
    if (typeof window.updateSatellites_render !== 'undefined') {
        window.updateSatellites_render(data);
    }
}

// ---- Initialization & Polling ----

document.addEventListener('DOMContentLoaded', async () => {
    console.log('[OSINT] Dashboard initializing...');

    // Initial data fetch — staggered to avoid hammering
    await Promise.all([
        updateWeather(),
        updateLaunches(),
        updateNews(),
    ]);

    // Slightly delayed second batch
    setTimeout(async () => {
        await Promise.all([
            updateNEO(),
            updateAstronauts(),
            updateAlerts(),
            updateFlares(),
            updateStats(),
        ]);
    }, 1000);

    // Fetch satellites (may take longer due to SGP4 propagation)
    setTimeout(async () => {
        const data = await fetchJSON('/api/satellites?group=stations');
        if (data && typeof updateSatellites !== 'undefined') {
            // Call satellite.js function directly
            window._pendingSatData = data;
            if (satMap) {
                updateSatellitesFromData(data);
            }
        }
    }, 2000);

    // ---- Polling intervals ----
    setInterval(updateWeather, 60000);         // 60s
    setInterval(updateLaunches, 120000);       // 2min
    setInterval(renderLaunches, 1000);         // 1s countdown refresh
    setInterval(updateNews, 300000);           // 5min
    setInterval(updateNEO, 600000);            // 10min
    setInterval(updateAstronauts, 600000);     // 10min
    setInterval(updateAlerts, 120000);         // 2min
    setInterval(updateFlares, 600000);         // 10min
    setInterval(updateStats, 60000);           // 60s

    // Satellite refresh
    setInterval(async () => {
        const data = await fetchJSON('/api/satellites?group=stations');
        if (data) updateSatellitesFromData(data);
    }, 30000);

    console.log('[OSINT] Dashboard live.');
});

// Bridge function to call satellite.js
function updateSatellitesFromData(data) {
    if (typeof updateSatellites === 'function' && satMap) {
        // The function in satellite.js is called updateSatellites
        // but we have a naming collision — satellite.js uses a different name
    }
    // Direct access to satellite.js internals
    if (satMap && data) {
        // Clear old markers
        satMarkers.forEach(m => satMap.removeLayer(m));
        satMarkers = [];

        data.forEach(sat => {
            const isISS = sat.norad_id === 25544;
            const isCSS = sat.norad_id === 48274;

            let color = '#00c8ff';
            let radius = 4;
            let opacity = 0.7;

            if (isISS) { color = '#00ff88'; radius = 8; opacity = 1; }
            else if (isCSS) { color = '#ffd700'; radius = 7; opacity = 1; }
            else if (sat.object_type === 'DEBRIS') { color = '#ff3355'; radius = 2; opacity = 0.3; }
            else if (sat.object_type === 'ROCKET BODY') { color = '#ff8c00'; radius = 3; opacity = 0.4; }

            const marker = L.circleMarker([sat.lat, sat.lng], {
                radius, fillColor: color, fillOpacity: opacity,
                color, weight: isISS || isCSS ? 2 : 0, opacity: isISS || isCSS ? 0.8 : 0,
            }).addTo(satMap);

            marker.bindPopup(`
                <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#e0e8f0;background:#0a0f1e;padding:8px;border-radius:6px;min-width:180px;">
                    <div style="color:#00c8ff;font-weight:700;margin-bottom:6px;">${sat.name}</div>
                    <div>NORAD: ${sat.norad_id}</div>
                    <div>Alt: ${sat.alt_km?.toFixed(0) || '?'} km</div>
                    <div>Inc: ${sat.inclination?.toFixed(1) || '?'}&deg;</div>
                    <div>Period: ${sat.period_min || '?'} min</div>
                </div>
            `, { className: 'sat-popup', closeButton: false });

            satMarkers.push(marker);
        });

        // ISS ground track
        fetchISSTrack();
        document.getElementById('map-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
    }
}

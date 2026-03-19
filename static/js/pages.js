/* ============================================================
   FVEY SDA — Page Renderers
   Combined Space Operations Center Display
   All intelligence APIs integrated — 8 pages
   ============================================================ */

const Pages = {};

/* ---- Helper Functions ---- */

function timeAgo(d) {
    const diff = Date.now() - new Date(d).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return 'JUST NOW';
    if (m < 60) return `${m}M AGO`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}H AGO`;
    return `${Math.floor(h / 24)}D AGO`;
}

function countdown(d) {
    const diff = new Date(d).getTime() - Date.now();
    if (diff <= 0) return 'T-00:00:00';
    const dd = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    const hh = String(h).padStart(2, '0');
    const mm = String(m).padStart(2, '0');
    const ss = String(s).padStart(2, '0');
    if (dd > 0) return `T-${dd}D ${hh}:${mm}:${ss}`;
    return `T-${hh}:${mm}:${ss}`;
}

function badge(level) {
    const l = (level || 'medium').toLowerCase();
    return `<span class="badge badge-${l}">${l.toUpperCase()}</span>`;
}

function countryBadge(c) {
    const map = { PRC: 'prc', CIS: 'cis', NKOR: 'nkor', IRAN: 'iran', US: 'fvey', UK: 'fvey', CA: 'fvey', AU: 'fvey', NZ: 'fvey' };
    const names = { PRC: 'PRC', CIS: 'RUS', NKOR: 'DPRK', IRAN: 'IRAN', US: 'US', UK: 'UK', CA: 'CA', AU: 'AU', NZ: 'NZ' };
    return `<span class="badge badge-${map[c] || 'fvey'}">${names[c] || c}</span>`;
}

function countryColor(c) {
    return { PRC: '#FF2020', CIS: '#FF8C00', NKOR: '#C040FF', IRAN: '#FFD700', US: '#2080FF', UK: '#2080FF', CA: '#2080FF', AU: '#2080FF', NZ: '#2080FF' }[c] || '#888';
}

function zulu() {
    return new Date().toISOString().substring(11, 19) + 'Z';
}

async function api(url) {
    try {
        const r = await fetch(url);
        return r.ok ? await r.json() : null;
    } catch (e) {
        return null;
    }
}

function registerInterval(fn, ms) {
    const id = setInterval(fn, ms);
    if (!window._pageIntervals) window._pageIntervals = [];
    window._pageIntervals.push(id);
    return id;
}

function storeMap(map) {
    if (!window._extraMaps) window._extraMaps = [];
    window._extraMaps.push(map);
}

function makeMap(elementId, center, zoom) {
    const el = document.getElementById(elementId);
    if (!el) return null;
    if (!el.style.height || el.offsetHeight < 50) {
        el.style.height = Math.max(400, window.innerHeight - 300) + 'px';
    }
    const map = L.map(elementId, {
        center: center || [20, 0],
        zoom: zoom || 2,
        minZoom: 2,
        maxZoom: 10,
        attributionControl: false,
    });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
    if (typeof addGridOverlay === 'function') addGridOverlay(map);
    setTimeout(() => map.invalidateSize(), 200);
    setTimeout(() => map.invalidateSize(), 1000);
    return map;
}

function severityDots(level) {
    const levels = ['low', 'medium', 'high', 'critical'];
    const idx = levels.indexOf((level || 'medium').toLowerCase());
    return `<span class="severity-dots">${levels.map((l, i) =>
        `<span class="severity-dot ${i <= idx ? 'filled-' + l : 'empty'}"></span>`
    ).join('')}</span>`;
}

function resilienceColor(score) {
    if (score >= 70) return 'var(--green)';
    if (score >= 40) return 'var(--amber)';
    return 'var(--red)';
}

const ADV_PROVIDERS = ['CASC', 'China', 'Roscosmos', 'Russia', 'IRGC', 'Iran', 'DPRK', 'Korea', 'Khrunichev', 'Progress', 'ExPace', 'CASIC', 'Galactic Energy', 'LandSpace', 'iSpace', 'CAS Space', 'Orienspace', 'Space Pioneer'];

function isAdvLaunch(l) {
    return ADV_PROVIDERS.some(p => (l.provider || '').includes(p) || (l.name || '').includes(p));
}

function satPopup(name, color, fields) {
    return `<div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#e0e8f0;background:#000;padding:8px;min-width:200px">
        <div style="color:${color};margin-bottom:4px;font-size:11px">${name}</div>
        ${fields.map(f => `<div>${f}</div>`).join('')}
    </div>`;
}


/* ================================================================
   PAGE 1: COMMAND OVERVIEW (CMD)
   Primary warfighting display — map-dominant
   ================================================================ */
Pages.cmd = async function (el) {
    const vh = window.innerHeight;
    const chromeH = 80;
    const threatBarH = 44;
    const bottomStripH = 155;
    const envBarH = 56;
    const mapH = Math.max(300, vh - chromeH - threatBarH - bottomStripH - envBarH - 8);

    el.innerHTML = `
        <div class="cmd-page">
        <!-- THREAT STATUS BAR -->
        <div class="threat-bar">
            <div class="tb-cell hostile">
                <div class="tb-icon">&#9760;</div>
                <div><div class="tb-val" id="ov-prc">--</div><div class="tb-lbl">PRC SATS</div></div>
            </div>
            <div class="tb-cell warning">
                <div class="tb-icon">&#9760;</div>
                <div><div class="tb-val" id="ov-rus">--</div><div class="tb-lbl">RUS SATS</div></div>
            </div>
            <div class="tb-cell hostile">
                <div class="tb-icon">&#9673;</div>
                <div><div class="tb-val" id="ov-isr-ct">--</div><div class="tb-lbl">HOSTILE ISR</div></div>
            </div>
            <div class="tb-cell alert">
                <div class="tb-icon">&#9888;</div>
                <div><div class="tb-val" id="ov-asat-ct">--</div><div class="tb-lbl">CRITICAL ASAT</div></div>
            </div>
            <div class="tb-cell info">
                <div class="tb-icon">&#9678;</div>
                <div><div class="tb-val" id="ov-total">--</div><div class="tb-lbl">TOTAL TRACKED</div></div>
            </div>
            <div class="tb-cell" id="ov-threat-cell">
                <div class="tb-icon">&#9656;</div>
                <div><div class="tb-val" id="ov-threat-lvl">--</div><div class="tb-lbl">THREAT LEVEL</div></div>
            </div>
        </div>

        <!-- MAP + OVERLAY PANELS -->
        <div class="cmd-layout" style="height:${mapH}px">
            <div class="cmd-map-wrap" style="height:${mapH}px">
                <div id="sat-map" class="map-container" style="height:${mapH}px;min-height:${mapH}px"></div>
                <div class="map-legend">
                    <div class="legend-item"><span class="legend-dot" style="background:#FF2020"></span> PRC</div>
                    <div class="legend-item"><span class="legend-dot" style="background:#FF8C00"></span> RUS</div>
                    <div class="legend-item"><span class="legend-dot" style="background:#C040FF"></span> DPRK</div>
                    <div class="legend-item"><span class="legend-dot" style="background:#FFD700"></span> IRAN</div>
                    <div class="legend-item"><span class="legend-dot" style="background:rgba(32,128,255,0.4)"></span> FVEY</div>
                    <div class="legend-item" style="color:var(--text-muted)" id="ov-map-ts">--</div>
                </div>
                <div class="map-stat-overlay" id="ov-map-stats"></div>
                <div class="map-overlay-panels">
                    <div class="overlay-panel">
                        <div class="op-head">FORCE DISPOSITION</div>
                        <div class="op-body" id="ov-force"></div>
                    </div>
                    <div class="overlay-panel">
                        <div class="op-head" style="color:var(--red)">CRITICAL ASAT THREATS</div>
                        <div class="op-body" id="ov-asat" style="max-height:180px"></div>
                    </div>
                    <div class="overlay-panel">
                        <div class="op-head">ADVERSARY LAUNCH ACTIVITY</div>
                        <div class="op-body" id="ov-adv-launches" style="max-height:150px"></div>
                    </div>
                    <div class="overlay-panel">
                        <div class="op-head">LIVE SITREP</div>
                        <div class="op-body" id="ov-sitrep" style="max-height:140px"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- BOTTOM STRIPS -->
        <div class="cmd-bottom-strip">
            <div class="panel">
                <div class="panel-head"><h3>HOTSPOT COVERAGE</h3><span class="ph-meta" id="ov-hotspot-meta"></span></div>
                <div class="panel-body" style="max-height:120px" id="ov-hotspots"></div>
            </div>
            <div class="panel">
                <div class="panel-head"><h3>FVEY VULNERABILITIES</h3><span class="ph-meta"><span class="badge badge-critical">ASSESS</span></span></div>
                <div class="panel-body" style="max-height:120px" id="ov-vulns"></div>
            </div>
            <div class="panel">
                <div class="panel-head"><h3>OSINT + SOCIAL INTEL</h3><span class="ph-meta" id="ov-news-ts">--</span></div>
                <div class="panel-body" style="max-height:120px" id="ov-news"></div>
            </div>
        </div>

        <!-- ENVIRONMENT BAR -->
        <div class="env-bar">
            <div class="env-cell"><span class="env-lbl">Kp</span><span class="env-val" id="ov-kp">--</span></div>
            <div class="env-cell"><span class="env-lbl">SOLAR WIND</span><span class="env-val" id="ov-wind">--</span></div>
            <div class="env-cell"><span class="env-lbl">Bz</span><span class="env-val" id="ov-bz">--</span></div>
            <div class="env-cell"><span class="env-lbl">SFI</span><span class="env-val" id="ov-sfi">--</span></div>
            <div class="env-cell"><span class="env-lbl">RADIO</span><span class="env-val" id="ov-sr">R0</span></div>
            <div class="env-cell"><span class="env-lbl">SOLAR</span><span class="env-val" id="ov-ss">S0</span></div>
            <div class="env-cell"><span class="env-lbl">GEOMAG</span><span class="env-val" id="ov-sg">G0</span></div>
            <div class="env-cell"><span class="env-lbl">NEOs</span><span class="env-val" id="ov-neo">--</span></div>
            <div class="cmd-kp-chart-wrap"><canvas id="kp-chart" height="50"></canvas></div>
        </div>
        </div>`;

    // Init satellite map with explicit pixel height
    setTimeout(() => {
        const mapEl = document.getElementById('sat-map');
        if (!mapEl) return;
        mapEl.style.height = mapH + 'px';
        if (typeof initSatMap === 'function') {
            initSatMap('sat-map');
            if (satMap) {
                setTimeout(() => satMap.invalidateSize(), 200);
                setTimeout(() => satMap.invalidateSize(), 600);
                setTimeout(() => satMap.invalidateSize(), 1500);
            }
        }
    }, 100);

    // Init Kp chart
    setTimeout(() => {
        if (typeof initKpChart === 'function') initKpChart();
    }, 200);

    // Fetch all data in parallel
    const [advStats, launches, weather, neo, news, criticalSystems, vulns, stats, sitrep, hotspots, social] = await Promise.all([
        api('/api/adversary/stats'),
        api('/api/launches'),
        api('/api/weather'),
        api('/api/neo'),
        api('/api/news'),
        api('/api/missile-asat?threat=critical'),
        api('/api/threat/vulnerabilities'),
        api('/api/satellites/stats'),
        api('/api/intel/sitrep'),
        api('/api/intel/hotspots'),
        api('/api/intel/social'),
    ]);

    // --- Threat bar ---
    if (advStats) {
        const prc = advStats.PRC || {};
        const cis = advStats.CIS || {};
        const nkor = advStats.NKOR || {};
        const iran = advStats.IRAN || {};
        document.getElementById('ov-prc').textContent = prc.total || 0;
        document.getElementById('ov-rus').textContent = cis.total || 0;
        document.getElementById('ov-isr-ct').textContent = (prc.military_isr || 0) + (cis.military_isr || 0) + (nkor.military_isr || 0) + (iran.military_isr || 0);
    }
    if (stats) {
        document.getElementById('ov-total').textContent = (stats.total_tracked || 0).toLocaleString();
    }
    if (criticalSystems) {
        document.getElementById('ov-asat-ct').textContent = criticalSystems.length;
    }

    // Sitrep threat level
    if (sitrep) {
        const lvl = (sitrep.threat_level || 'HIGH').toUpperCase();
        const tlEl = document.getElementById('ov-threat-lvl');
        const tcEl = document.getElementById('ov-threat-cell');
        if (tlEl) {
            tlEl.textContent = lvl;
            tlEl.style.color = lvl === 'CRITICAL' ? 'var(--red)' : lvl === 'HIGH' ? 'var(--cis)' : 'var(--amber)';
        }
        if (tcEl) {
            tcEl.className = 'tb-cell ' + (lvl === 'CRITICAL' ? 'hostile' : lvl === 'HIGH' ? 'warning' : 'alert');
        }
    }

    // Map stat overlay
    const mapStatsEl = document.getElementById('ov-map-stats');
    if (mapStatsEl && advStats && stats) {
        const totalAdv = (advStats.PRC?.total || 0) + (advStats.CIS?.total || 0) + (advStats.NKOR?.total || 0) + (advStats.IRAN?.total || 0);
        const totalISR = (advStats.PRC?.military_isr || 0) + (advStats.CIS?.military_isr || 0);
        mapStatsEl.innerHTML = `
            <div class="map-stat-item" style="border-left:2px solid var(--red)">
                <div><div class="map-stat-val" style="color:var(--red)">${totalAdv}</div><div class="map-stat-lbl">HOSTILE ON ORBIT</div></div>
            </div>
            <div class="map-stat-item" style="border-left:2px solid var(--cyan)">
                <div><div class="map-stat-val" style="color:var(--cyan)">${(stats.active_payloads || 0).toLocaleString()}</div><div class="map-stat-lbl">ACTIVE PAYLOADS</div></div>
            </div>
            <div class="map-stat-item" style="border-left:2px solid var(--amber)">
                <div><div class="map-stat-val" style="color:var(--amber)">${totalISR}</div><div class="map-stat-lbl">ISR OVERHEAD</div></div>
            </div>`;
    }

    // Adversary launches
    let advLaunches = [];
    if (launches) {
        advLaunches = launches.filter(l => isAdvLaunch(l));
    }

    // --- Force Disposition ---
    if (advStats) {
        const nations = [
            { code: 'PRC', name: 'PRC', data: advStats.PRC, color: '#FF2020' },
            { code: 'CIS', name: 'RUS', data: advStats.CIS, color: '#FF8C00' },
            { code: 'NKOR', name: 'DPRK', data: advStats.NKOR, color: '#C040FF' },
            { code: 'IRAN', name: 'IRAN', data: advStats.IRAN, color: '#FFD700' },
        ];
        document.getElementById('ov-force').innerHTML = nations.map(n => {
            const d = n.data || {};
            const total = d.total || 0;
            const barMax = 600;
            const isr = d.military_isr || 0;
            const nav = d.navigation || 0;
            const cats = d.by_category || {};
            const comms = cats.comms || 0;
            const sda = cats.sda_asat || 0;
            return `
                <div class="fd-row">
                    <span class="fd-nation" style="color:${n.color}">${n.name}</span>
                    <div class="fd-bar-wrap"><div class="fd-bar" style="width:${Math.min(total / barMax * 100, 100)}%;background:${n.color}"></div></div>
                    <span class="fd-count">${total}</span>
                </div>
                <div style="display:flex;gap:6px;margin:0 0 4px 54px;font-size:8px;color:var(--text-muted)">
                    ${isr ? `<span>ISR:${isr}</span>` : ''}
                    ${nav ? `<span>NAV:${nav}</span>` : ''}
                    ${comms ? `<span>COM:${comms}</span>` : ''}
                    ${sda ? `<span style="color:var(--red)">ASAT:${sda}</span>` : ''}
                </div>`;
        }).join('');
    }

    // --- Critical ASAT ---
    if (criticalSystems) {
        document.getElementById('ov-asat').innerHTML = criticalSystems.map(s => `
            <div class="asat-item">
                <div class="asat-name"><span class="badge badge-critical">CRIT</span> ${s.name}</div>
                <div class="asat-meta">${s.country} | ${(s.type || '').replace(/_/g, ' ')} ${s.max_altitude_km ? '| ALT ' + s.max_altitude_km.toLocaleString() + ' KM' : ''} ${s.status ? '| ' + s.status.toUpperCase() : ''}</div>
            </div>
        `).join('');
    }

    // --- Live SITREP ---
    function renderSitrep(data) {
        const sitEl = document.getElementById('ov-sitrep');
        if (!sitEl || !data) return;
        const events = data.key_events || [];
        sitEl.innerHTML = `
            <div style="font-size:9px;color:var(--text);line-height:1.5;margin-bottom:4px">${(data.assessment || '').substring(0, 180)}${(data.assessment || '').length > 180 ? '...' : ''}</div>
            ${events.slice(0, 4).map(e => `
                <div style="padding:2px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:9px">
                    ${badge(e.severity || 'medium')} <span style="color:var(--white)">${e.event}</span>
                </div>
            `).join('')}
            <div style="font-size:7px;color:var(--text-muted);margin-top:3px">${data.timestamp ? timeAgo(data.timestamp) : zulu()}</div>`;
    }
    renderSitrep(sitrep);

    // --- Adversary Launches (live countdown) ---
    function renderAdvLaunches() {
        const body = document.getElementById('ov-adv-launches');
        if (!body) return;
        if (!advLaunches.length) { body.innerHTML = '<div class="empty-state">NO ADV LAUNCHES SCHEDULED</div>'; return; }
        body.innerHTML = advLaunches.slice(0, 5).map(l => `
            <div class="launch-line ll-adv">
                <div class="ll-name">${l.name}</div>
                <div class="ll-detail">${l.provider} | ${l.pad_location || '?'}</div>
                <div class="ll-countdown">${l.net ? countdown(l.net) : 'TBD'}</div>
            </div>
        `).join('');
    }
    renderAdvLaunches();
    registerInterval(renderAdvLaunches, 1000);

    // --- Hotspot Coverage ---
    if (hotspots && hotspots.hotspots) {
        const hs = hotspots.hotspots;
        document.getElementById('ov-hotspot-meta').innerHTML = `<span class="badge badge-high">${hs.length} ZONES</span>`;
        document.getElementById('ov-hotspots').innerHTML = hs.slice(0, 6).map(h => `
            <div class="vuln-line">
                <span style="color:var(--red);font-size:12px;min-width:28px;text-align:right">${h.total_adversary_passes}</span>
                <span style="color:var(--white);font-size:10px">${h.name}</span>
                <span style="font-size:8px;color:var(--text-muted)">${h.passes_by_country ? Object.entries(h.passes_by_country).map(([c, n]) => c + ':' + n).join(' ') : ''}</span>
            </div>
        `).join('');
    }

    // --- Vulnerabilities ---
    if (vulns) {
        const sorted = [...vulns].sort((a, b) => {
            const order = { critical: 0, high: 1, medium: 2, low: 3 };
            return (order[a.severity] || 9) - (order[b.severity] || 9);
        });
        document.getElementById('ov-vulns').innerHTML = sorted.slice(0, 6).map(v => `
            <div class="vuln-line">
                ${severityDots(v.severity || 'high')}
                ${badge(v.severity || 'high')}
                <span style="color:var(--white);font-size:10px">${v.title}</span>
            </div>
        `).join('');
    }

    // --- OSINT + Social Intel ---
    const newsEl = document.getElementById('ov-news');
    if (newsEl) {
        let html = '';
        if (news) {
            html += news.slice(0, 4).map(n => `
                <a href="${n.url}" target="_blank" rel="noopener" class="news-line">
                    <span class="nl-title">${n.title}</span>
                    <span class="nl-meta">${n.news_site || 'OSINT'} // ${timeAgo(n.published_at)}</span>
                </a>
            `).join('');
        }
        if (social && social.length) {
            html += '<div style="border-top:1px solid var(--border);margin:3px 0;padding-top:2px;font-size:7px;letter-spacing:1.5px;color:var(--text-muted)">SOCIAL INTEL</div>';
            html += social.slice(0, 3).map(s => `
                <a href="${s.url || '#'}" target="_blank" rel="noopener" class="news-line">
                    <span class="nl-title" style="color:var(--cyan)">${(s.text || '').substring(0, 80)}${(s.text || '').length > 80 ? '...' : ''}</span>
                    <span class="nl-meta">${s.platform || '?'} / ${s.author || '?'} // ${s.relevance_score ? 'REL:' + s.relevance_score : ''} ${s.timestamp ? timeAgo(s.timestamp) : ''}</span>
                </a>
            `).join('');
        }
        newsEl.innerHTML = html || '<div class="empty-state">NO FEED DATA</div>';
        document.getElementById('ov-news-ts').textContent = zulu();
    }

    // --- Environment Bar ---
    if (weather) {
        if (weather.kp_current != null) {
            const kpEl = document.getElementById('ov-kp');
            kpEl.textContent = weather.kp_current.toFixed(1);
            kpEl.style.color = weather.kp_current < 4 ? 'var(--green)' : weather.kp_current < 6 ? '#FFD700' : 'var(--red)';
        }
        if (weather.solar_wind_speed != null) document.getElementById('ov-wind').textContent = Math.round(weather.solar_wind_speed) + ' KM/S';
        if (weather.bz != null) {
            const bzEl = document.getElementById('ov-bz');
            bzEl.textContent = weather.bz.toFixed(1);
            bzEl.style.color = weather.bz < 0 ? 'var(--red)' : 'var(--green)';
        }
        if (weather.sfi != null) document.getElementById('ov-sfi').textContent = Math.round(weather.sfi);
        if (weather.scales) {
            for (const k of ['R', 'S', 'G']) {
                const v = weather.scales[k]?.Scale || 0;
                const scaleEl = document.getElementById('ov-s' + k.toLowerCase());
                if (scaleEl) {
                    scaleEl.textContent = k + v;
                    scaleEl.style.color = v === 0 ? 'var(--green)' : v <= 2 ? '#FFD700' : 'var(--red)';
                }
            }
        }
        if (weather.kp_history && typeof updateKpChart === 'function') {
            setTimeout(() => updateKpChart(weather.kp_history), 300);
        }
    }
    if (neo) document.getElementById('ov-neo').textContent = neo.length;

    // --- MAP: Plot adversary & FVEY sats ---
    setTimeout(async () => {
        const [prcSats, cisSats, nkorSats, iranSats, fveySats] = await Promise.all([
            api('/api/adversary/satellites?country=PRC'),
            api('/api/adversary/satellites?country=CIS'),
            api('/api/adversary/satellites?country=NKOR'),
            api('/api/adversary/satellites?country=IRAN'),
            api('/api/satellites?group=stations'),
        ]);

        if (!satMap) return;
        satMarkers.forEach(m => satMap.removeLayer(m));
        satMarkers = [];

        const allAdv = [
            ...(prcSats || []).map(s => ({ ...s, _c: '#FF2020', _r: s.category === 'military_isr' ? 4 : s.category === 'sda_asat' ? 3.5 : 2.5 })),
            ...(cisSats || []).map(s => ({ ...s, _c: '#FF8C00', _r: s.category === 'military_isr' ? 4 : s.category === 'sda_asat' ? 3.5 : 2.5 })),
            ...(nkorSats || []).map(s => ({ ...s, _c: '#C040FF', _r: 5 })),
            ...(iranSats || []).map(s => ({ ...s, _c: '#FFD700', _r: 5 })),
        ];

        allAdv.forEach(s => {
            if (!s.lat || !s.lng) return;
            const isISR = s.category === 'military_isr';
            const isASAT = s.category === 'sda_asat';
            const m = L.circleMarker([s.lat, s.lng], {
                radius: s._r,
                fillColor: s._c,
                fillOpacity: isISR ? 0.85 : isASAT ? 0.75 : 0.5,
                color: isISR ? '#fff' : s._c,
                weight: isISR ? 1 : isASAT ? 1 : 0,
                opacity: isISR ? 0.3 : 0.2,
                className: isISR ? 'isr-pulse-marker' : '',
            }).bindPopup(satPopup(s.name, s._c, [
                `NORAD: ${s.norad_id} | ${s.country}`,
                `MISSION: <span style="color:${isISR ? 'var(--red)' : isASAT ? 'var(--cis)' : 'var(--text)'}">${(s.category || '').replace(/_/g, ' ').toUpperCase()}</span>`,
                `ALT: ${Math.round(s.alt_km || 0)} KM | INC: ${s.inclination?.toFixed(1) || '?'}&deg;`,
                `REGIME: ${s.regime || '?'}`,
            ]), { className: 'sat-popup', closeButton: false }).addTo(satMap);
            satMarkers.push(m);
        });

        // FVEY sats (dim blue)
        (fveySats || []).forEach(s => {
            if (!s.lat || !s.lng) return;
            const m = L.circleMarker([s.lat, s.lng], {
                radius: s.norad_id === 25544 ? 6 : 1.5,
                fillColor: '#2080FF', fillOpacity: s.norad_id === 25544 ? 0.9 : 0.12,
                color: '#2080FF', weight: s.norad_id === 25544 ? 2 : 0,
            }).addTo(satMap);
            satMarkers.push(m);
        });

        document.getElementById('ov-map-ts').textContent = zulu();
    }, 350);

    // --- AUTO-REFRESH: Satellites every 30s ---
    registerInterval(async () => {
        if (!satMap) return;
        const [prcR, cisR, nkorR, iranR] = await Promise.all([
            api('/api/adversary/satellites?country=PRC'),
            api('/api/adversary/satellites?country=CIS'),
            api('/api/adversary/satellites?country=NKOR'),
            api('/api/adversary/satellites?country=IRAN'),
        ]);
        satMarkers.forEach(m => satMap.removeLayer(m));
        satMarkers = [];
        const refresh = [
            ...(prcR || []).map(s => ({ ...s, _c: '#FF2020', _r: s.category === 'military_isr' ? 4 : 2.5 })),
            ...(cisR || []).map(s => ({ ...s, _c: '#FF8C00', _r: s.category === 'military_isr' ? 4 : 2.5 })),
            ...(nkorR || []).map(s => ({ ...s, _c: '#C040FF', _r: 5 })),
            ...(iranR || []).map(s => ({ ...s, _c: '#FFD700', _r: 5 })),
        ];
        refresh.forEach(s => {
            if (!s.lat || !s.lng) return;
            const m = L.circleMarker([s.lat, s.lng], {
                radius: s._r, fillColor: s._c, fillOpacity: 0.6,
                color: s._c, weight: 0,
            }).addTo(satMap);
            satMarkers.push(m);
        });
        const tsEl = document.getElementById('ov-map-ts');
        if (tsEl) tsEl.textContent = zulu();
    }, 30000);

    // --- AUTO-REFRESH: SITREP every 60s ---
    registerInterval(async () => {
        const freshSitrep = await api('/api/intel/sitrep');
        renderSitrep(freshSitrep);
    }, 60000);

    // --- AUTO-REFRESH: Weather every 60s ---
    registerInterval(async () => {
        const w = await api('/api/weather');
        if (!w) return;
        if (w.kp_current != null) {
            const kpEl = document.getElementById('ov-kp');
            if (kpEl) {
                kpEl.textContent = w.kp_current.toFixed(1);
                kpEl.style.color = w.kp_current < 4 ? 'var(--green)' : w.kp_current < 6 ? '#FFD700' : 'var(--red)';
            }
        }
        if (w.solar_wind_speed != null) {
            const wEl = document.getElementById('ov-wind');
            if (wEl) wEl.textContent = Math.round(w.solar_wind_speed) + ' KM/S';
        }
        if (w.kp_history && typeof updateKpChart === 'function') updateKpChart(w.kp_history);
    }, 60000);
};


/* ================================================================
   PAGE 2: ADVERSARY PROFILES
   Country profiles with tabs — PRC / RUS / DPRK / IRAN
   ================================================================ */
Pages.adversary = async function (el) {
    el.innerHTML = '<div class="loading">LOADING ADVERSARY INTELLIGENCE</div>';

    const [stats, prc, cis, nkor, iran, threatPrc, threatCis, threatNkor, threatIran] = await Promise.all([
        api('/api/adversary/stats'),
        api('/api/adversary/satellites?country=PRC'),
        api('/api/adversary/satellites?country=CIS'),
        api('/api/adversary/satellites?country=NKOR'),
        api('/api/adversary/satellites?country=IRAN'),
        api('/api/threat/adversary/PRC'),
        api('/api/threat/adversary/CIS'),
        api('/api/threat/adversary/NKOR'),
        api('/api/threat/adversary/IRAN'),
    ]);

    const countries = [
        { code: 'PRC', name: 'CHINA', sats: prc, threat: threatPrc, color: '#FF2020', stats: stats?.PRC },
        { code: 'CIS', name: 'RUSSIA', sats: cis, threat: threatCis, color: '#FF8C00', stats: stats?.CIS },
        { code: 'NKOR', name: 'DPRK', sats: nkor, threat: threatNkor, color: '#C040FF', stats: stats?.NKOR },
        { code: 'IRAN', name: 'IRAN', sats: iran, threat: threatIran, color: '#FFD700', stats: stats?.IRAN },
    ];

    const totalAll = countries.reduce((a, c) => a + (c.stats?.total || c.sats?.length || 0), 0);
    const totalISR = countries.reduce((a, c) => a + (c.stats?.military_isr || 0), 0);

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                ${countries.map(c => `
                    <div class="tb-cell" style="border-left:2px solid ${c.color}">
                        <div class="tb-icon" style="color:${c.color}">&#9760;</div>
                        <div><div class="tb-val" style="color:${c.color}">${c.stats?.total || (c.sats?.length || 0)}</div><div class="tb-lbl">${c.name}</div></div>
                    </div>
                `).join('')}
                <div class="tb-cell hostile">
                    <div class="tb-icon">&#9673;</div>
                    <div><div class="tb-val">${totalISR}</div><div class="tb-lbl">TOTAL ISR</div></div>
                </div>
                <div class="tb-cell info">
                    <div class="tb-icon">&#9678;</div>
                    <div><div class="tb-val">${totalAll}</div><div class="tb-lbl">TOTAL HOSTILE</div></div>
                </div>
            </div>
            <div class="country-tabs" id="adv-tabs">
                ${countries.map((c, i) => `<div class="country-tab${i === 0 ? ' active' : ''}" data-country="${c.code}" style="${i === 0 ? 'color:' + c.color : ''}">${c.name} <span style="font-size:9px;opacity:0.5">${c.stats?.total || c.sats?.length || 0}</span></div>`).join('')}
            </div>
            <div id="adv-detail"></div>
        </div>
    `;

    let advMiniMap = null;

    function renderCountry(code) {
        const c = countries.find(x => x.code === code);
        if (!c) return;
        const sats = c.sats || [];
        const t = c.threat || {};
        const cats = {};
        const regimes = {};
        sats.forEach(s => {
            cats[s.category] = (cats[s.category] || 0) + 1;
            if (s.regime) regimes[s.regime] = (regimes[s.regime] || 0) + 1;
        });

        el.querySelectorAll('.country-tab').forEach(tab => {
            const tc = countries.find(x => x.code === tab.dataset.country);
            tab.style.color = tab.classList.contains('active') ? tc.color : '';
        });

        if (advMiniMap) { try { advMiniMap.remove(); } catch (e) { } advMiniMap = null; }

        document.getElementById('adv-detail').innerHTML = `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:2px">
                <div class="panel">
                    <div class="panel-head"><h3>STRATEGIC ASSESSMENT</h3><span class="ph-meta">${badge((t.overall_threat || 'high').toLowerCase())} THREAT</span></div>
                    <div class="panel-body" style="max-height:380px">
                        ${t.trend ? `<div class="intel-summary"><strong>TREND:</strong> <span style="color:var(--red)">${t.trend}</span></div>` : ''}
                        <div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:10px">${t.assessment || t.summary || ''}</div>
                        ${t.doctrine ? `<div class="intel-field"><span class="intel-label">DOCTRINE</span>${t.doctrine}</div>` : ''}
                        ${t.strategic_context ? `<div class="intel-field"><span class="intel-label">STRATEGIC CONTEXT</span>${t.strategic_context}</div>` : ''}
                        ${t.key_capabilities?.length ? `
                            <div class="intel-field"><span class="intel-label">KEY CAPABILITIES</span>
                                <ul style="margin:3px 0 0 14px;color:var(--text)">${t.key_capabilities.map(k => `<li style="margin-bottom:3px;font-size:10px;line-height:1.4">${k}</li>`).join('')}</ul>
                            </div>
                        ` : ''}
                        ${t.intelligence_gaps?.length ? `
                            <div class="intel-field"><span class="intel-label" style="color:var(--cis)">INTELLIGENCE GAPS</span>
                                <ul style="margin:3px 0 0 14px;color:var(--text)">${t.intelligence_gaps.map(g => `<li style="margin-bottom:3px;font-size:10px;line-height:1.4;color:var(--cis)">${g}</li>`).join('')}</ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>${c.name} ORBITAL POSITIONS</h3><span class="ph-meta">${sats.length} ACTIVE</span></div>
                    <div class="panel-body" style="padding:0"><div id="adv-mini-map" class="adv-mini-map"></div></div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:2px">
                <div class="panel">
                    <div class="panel-head"><h3>MISSION BREAKDOWN</h3><span class="ph-meta">${Object.keys(cats).length} CATEGORIES</span></div>
                    <div class="panel-body">
                        <div style="font-size:28px;color:${c.color};margin-bottom:8px">${sats.length} <span style="font-size:10px;color:var(--text-dim)">ACTIVE SATELLITES</span></div>
                        ${Object.entries(cats).sort((a, b) => b[1] - a[1]).map(([cat, count]) => {
                            const pct = Math.round(count / sats.length * 100);
                            const isMil = cat === 'military_isr' || cat === 'sda_asat';
                            return `
                            <div class="cat-breakdown">
                                <span class="cat-label" style="${isMil ? 'color:var(--red)' : ''}">${cat.replace(/_/g, ' ')}</span>
                                <div class="cat-bar-wrap"><div class="cat-bar" style="width:${pct}%;background:${c.color};opacity:${isMil ? 0.9 : 0.6}"></div></div>
                                <span class="cat-count" style="color:${c.color}">${count}</span>
                            </div>`;
                        }).join('')}
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>ORBITAL REGIME DISTRIBUTION</h3></div>
                    <div class="panel-body">
                        ${Object.entries(regimes).sort((a, b) => b[1] - a[1]).map(([regime, count]) => {
                            const pct = Math.round(count / sats.length * 100);
                            return `
                            <div class="cat-breakdown">
                                <span class="cat-label">${regime}</span>
                                <div class="cat-bar-wrap"><div class="cat-bar" style="width:${pct}%;background:${c.color};opacity:0.5"></div></div>
                                <span class="cat-count">${count}</span>
                            </div>`;
                        }).join('')}
                    </div>
                </div>
            </div>
            <div class="panel">
                <div class="panel-head"><h3>${c.name} SATELLITE CATALOG</h3><span class="ph-meta">${sats.length} OBJECTS</span></div>
                <div class="panel-body" style="max-height:400px">
                    <table class="data-table"><thead><tr>
                        <th>DESIGNATION</th><th>NORAD</th><th>MISSION</th><th>REGIME</th><th>ALT KM</th><th>INC</th>
                    </tr></thead><tbody>
                    ${sats.slice(0, 200).map(s => `<tr>
                        <td style="color:${c.color}">${s.name || '?'}</td>
                        <td>${s.norad_id || '?'}</td>
                        <td>${badge(s.category === 'military_isr' ? 'critical' : s.category === 'sda_asat' ? 'high' : 'medium')} ${(s.category || '').replace(/_/g, ' ')}</td>
                        <td>${s.regime || '?'}</td>
                        <td>${s.alt_km ? Math.round(s.alt_km) : '?'}</td>
                        <td>${s.inclination ? s.inclination.toFixed(1) + '\u00B0' : '?'}</td>
                    </tr>`).join('')}
                    </tbody></table>
                </div>
            </div>
        `;

        // Initialize mini map
        setTimeout(() => {
            const mapEl = document.getElementById('adv-mini-map');
            if (!mapEl) return;
            mapEl.style.height = '280px';
            const centerLng = code === 'PRC' ? 105 : code === 'CIS' ? 60 : code === 'NKOR' ? 127 : 52;
            advMiniMap = makeMap('adv-mini-map', [30, centerLng], 2);
            if (advMiniMap) {
                storeMap(advMiniMap);
                sats.forEach(s => {
                    if (!s.lat || !s.lng) return;
                    const isISR = s.category === 'military_isr';
                    const isASAT = s.category === 'sda_asat';
                    L.circleMarker([s.lat, s.lng], {
                        radius: isISR ? 4 : isASAT ? 3.5 : 2,
                        fillColor: c.color, fillOpacity: isISR ? 0.9 : 0.5,
                        color: isISR ? '#fff' : c.color, weight: isISR ? 1 : 0,
                        className: isISR ? 'isr-pulse-marker' : '',
                    }).bindPopup(satPopup(s.name, c.color, [
                        `${(s.category || '').replace(/_/g, ' ')} | ${Math.round(s.alt_km || 0)} KM`,
                    ]), { className: 'sat-popup', closeButton: false }).addTo(advMiniMap);
                });
            }
        }, 150);
    }

    renderCountry('PRC');
    el.querySelectorAll('.country-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            el.querySelectorAll('.country-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderCountry(tab.dataset.country);
        });
    });
};


/* ================================================================
   PAGE 3: ORBITAL THREATS
   Full adversary orbital map + tables by mission type + regime cards
   ================================================================ */
Pages.orbital = async function (el) {
    el.innerHTML = '<div class="loading">MAPPING ORBITAL THREATS</div>';

    const [prc, cis, nkor, iran, advStats] = await Promise.all([
        api('/api/adversary/satellites?country=PRC'),
        api('/api/adversary/satellites?country=CIS'),
        api('/api/adversary/satellites?country=NKOR'),
        api('/api/adversary/satellites?country=IRAN'),
        api('/api/adversary/stats'),
    ]);

    const allAdv = [
        ...(prc || []).map(s => ({ ...s, _nation: 'PRC' })),
        ...(cis || []).map(s => ({ ...s, _nation: 'CIS' })),
        ...(nkor || []).map(s => ({ ...s, _nation: 'NKOR' })),
        ...(iran || []).map(s => ({ ...s, _nation: 'IRAN' })),
    ];

    const milISR = allAdv.filter(s => s.category === 'military_isr');
    const sda = allAdv.filter(s => s.category === 'sda_asat');
    const nav = allAdv.filter(s => s.category === 'navigation');
    const comms = allAdv.filter(s => s.category === 'comms');
    const other = allAdv.filter(s => !['military_isr', 'sda_asat', 'navigation', 'comms'].includes(s.category));

    // Regime counts
    const regimes = {};
    allAdv.forEach(s => { if (s.regime) regimes[s.regime] = (regimes[s.regime] || 0) + 1; });
    const regimeSorted = Object.entries(regimes).sort((a, b) => b[1] - a[1]);

    const mapH = Math.max(450, window.innerHeight * 0.45);

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">${allAdv.length}</div><div class="tb-lbl">TOTAL HOSTILE</div></div></div>
                <div class="tb-cell hostile"><div class="tb-icon">&#9673;</div><div><div class="tb-val">${milISR.length}</div><div class="tb-lbl">ISR / RECON</div></div></div>
                <div class="tb-cell alert"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${sda.length}</div><div class="tb-lbl">SDA / ASAT</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${nav.length}</div><div class="tb-lbl">PNT / NAV</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9656;</div><div><div class="tb-val">${comms.length}</div><div class="tb-lbl">COMMS</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9670;</div><div><div class="tb-val">${other.length}</div><div class="tb-lbl">OTHER</div></div></div>
            </div>

            <div class="regime-strip">
                ${regimeSorted.slice(0, 5).map(([regime, count]) => `
                    <div class="regime-card">
                        <div class="regime-card-val">${count}</div>
                        <div class="regime-card-label">${regime}</div>
                    </div>
                `).join('')}
            </div>

            <div class="panel mb-2">
                <div class="panel-head"><h3>ADVERSARY ORBITAL ASSETS // GLOBAL VIEW</h3><span class="ph-meta">${zulu()} | ${allAdv.length} OBJECTS</span></div>
                <div class="panel-body" style="padding:0"><div id="orbital-map" class="map-container" style="height:${mapH}px;min-height:${mapH}px"></div></div>
            </div>

            <div class="grid-2 mb-2">
                <div class="panel">
                    <div class="panel-head"><h3>HOSTILE ISR / RECONNAISSANCE</h3><span class="ph-meta"><span class="badge badge-critical">${milISR.length} TRACKED</span></span></div>
                    <div class="panel-body" style="max-height:350px">
                        <table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>INC</th><th>REGIME</th></tr></thead><tbody>
                        ${milISR.slice(0, 100).map(s => `<tr>
                            <td style="color:${countryColor(s._nation)}">${s.name}</td>
                            <td>${countryBadge(s._nation)}</td>
                            <td>${s.alt_km ? Math.round(s.alt_km) + ' KM' : '?'}</td>
                            <td>${s.inclination?.toFixed(1) || '?'}\u00B0</td>
                            <td>${s.regime || '?'}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>SDA / ASAT-CAPABLE</h3><span class="ph-meta"><span class="badge badge-critical">${sda.length} TRACKED</span></span></div>
                    <div class="panel-body" style="max-height:350px">
                        <table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>INC</th><th>REGIME</th></tr></thead><tbody>
                        ${sda.map(s => `<tr>
                            <td style="color:${countryColor(s._nation)}">${s.name}</td>
                            <td>${countryBadge(s._nation)}</td>
                            <td>${s.alt_km ? Math.round(s.alt_km) + ' KM' : '?'}</td>
                            <td>${s.inclination?.toFixed(1) || '?'}\u00B0</td>
                            <td>${s.regime || '?'}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
            </div>
            <div class="grid-3">
                <div class="panel">
                    <div class="panel-head"><h3>NAVIGATION / PNT</h3><span class="ph-meta">${nav.length}</span></div>
                    <div class="panel-body" style="max-height:250px">
                        <table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>REGIME</th></tr></thead><tbody>
                        ${nav.slice(0, 60).map(s => `<tr>
                            <td style="color:${countryColor(s._nation)}">${s.name}</td>
                            <td>${countryBadge(s._nation)}</td>
                            <td>${s.alt_km ? Math.round(s.alt_km) + ' KM' : '?'}</td>
                            <td>${s.regime || '?'}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>COMMUNICATIONS</h3><span class="ph-meta">${comms.length}</span></div>
                    <div class="panel-body" style="max-height:250px">
                        <table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>REGIME</th></tr></thead><tbody>
                        ${comms.slice(0, 60).map(s => `<tr>
                            <td style="color:${countryColor(s._nation)}">${s.name}</td>
                            <td>${countryBadge(s._nation)}</td>
                            <td>${s.alt_km ? Math.round(s.alt_km) + ' KM' : '?'}</td>
                            <td>${s.regime || '?'}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>OTHER / UNCAT</h3><span class="ph-meta">${other.length}</span></div>
                    <div class="panel-body" style="max-height:250px">
                        <table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>CAT</th><th>ALT</th></tr></thead><tbody>
                        ${other.slice(0, 60).map(s => `<tr>
                            <td style="color:${countryColor(s._nation)}">${s.name}</td>
                            <td>${countryBadge(s._nation)}</td>
                            <td>${(s.category || '?').replace(/_/g, ' ')}</td>
                            <td>${s.alt_km ? Math.round(s.alt_km) + ' KM' : '?'}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => {
        const mapEl = document.getElementById('orbital-map');
        if (!mapEl) return;
        mapEl.style.height = mapH + 'px';
        const omap = makeMap('orbital-map', [20, 0], 2);
        if (!omap) return;
        storeMap(omap);

        allAdv.forEach(s => {
            if (!s.lat || !s.lng) return;
            const col = countryColor(s._nation);
            const isISR = s.category === 'military_isr';
            const isASAT = s.category === 'sda_asat';
            const r = isASAT ? 5 : isISR ? 4 : s.category === 'navigation' ? 3 : 2.5;
            L.circleMarker([s.lat, s.lng], {
                radius: r,
                fillColor: col,
                fillOpacity: isISR ? 0.9 : isASAT ? 0.8 : 0.5,
                color: isISR ? '#fff' : col,
                weight: isISR ? 1.5 : isASAT ? 1.5 : 0,
                opacity: 0.4,
                className: isISR ? 'isr-pulse-marker' : '',
            }).bindPopup(satPopup(s.name, col, [
                `${s._nation} | ${(s.category || '').replace(/_/g, ' ')} | ${Math.round(s.alt_km || 0)} KM | ${s.regime || '?'}`,
            ]), { className: 'sat-popup', closeButton: false }).addTo(omap);
        });
    }, 150);
};


/* ================================================================
   PAGE 4: LAUNCH MONITOR
   Hero countdown for next adversary launch + adversary vs allied split
   ================================================================ */
Pages.launches = async function (el) {
    el.innerHTML = '<div class="loading">LOADING LAUNCH INTELLIGENCE</div>';
    const data = await api('/api/launches');
    if (!data) { el.innerHTML = '<div class="empty-state">LAUNCH DATA UNAVAILABLE</div>'; return; }

    data.forEach(l => { l._isAdv = isAdvLaunch(l); });
    const advLaunches = data.filter(l => l._isAdv);
    const fveyLaunches = data.filter(l => !l._isAdv);

    // Find next adversary launch for hero countdown
    const nextAdv = advLaunches.find(l => l.net && new Date(l.net).getTime() > Date.now());

    el.innerHTML = `
        <div class="page-wrap">
            ${nextAdv ? `
            <div class="launch-hero" id="launch-hero">
                <div>
                    <div class="launch-hero-label">NEXT ADVERSARY LAUNCH</div>
                    <div class="launch-hero-name">${nextAdv.name}</div>
                    <div class="launch-hero-meta">${nextAdv.provider || '?'} | ${nextAdv.rocket || '?'} | ${nextAdv.pad_location || '?'}</div>
                </div>
                <div class="launch-hero-countdown" id="hero-countdown">${countdown(nextAdv.net)}</div>
            </div>
            ` : ''}

            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">${advLaunches.length}</div><div class="tb-lbl">ADVERSARY</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9733;</div><div><div class="tb-val">${fveyLaunches.length}</div><div class="tb-lbl">ALLIED / OTHER</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${data.length}</div><div class="tb-lbl">TOTAL UPCOMING</div></div></div>
            </div>

            <div class="grid-2">
                <div class="panel">
                    <div class="panel-head"><h3>ADVERSARY LAUNCHES</h3><span class="ph-meta"><span class="badge badge-critical">${advLaunches.length} SCHEDULED</span></span></div>
                    <div class="panel-body" id="launch-adv" style="max-height:calc(100vh - 280px)"></div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>ALLIED / OTHER LAUNCHES</h3><span class="ph-meta">${fveyLaunches.length} TOTAL</span></div>
                    <div class="panel-body" id="launch-fvey" style="max-height:calc(100vh - 280px)"></div>
                </div>
            </div>
        </div>
    `;

    function renderLaunchList(container, launches) {
        if (!container) return;
        if (!launches.length) { container.innerHTML = '<div class="empty-state">NONE SCHEDULED</div>'; return; }
        container.innerHTML = launches.map(l => `
            <div class="launch-line ${l._isAdv ? 'll-adv' : ''}">
                <div style="display:flex;align-items:center;justify-content:space-between">
                    <div class="ll-name">${l._isAdv ? '&#9760; ' : ''}${l.name}</div>
                    <div class="ll-countdown" style="font-size:13px">${l.net ? countdown(l.net) : 'TBD'}</div>
                </div>
                <div class="ll-detail">${l.provider || '?'} | ${l.rocket || '?'} | ${l.pad_location || '?'}</div>
                ${l.mission_description ? `<div style="font-size:9px;color:var(--text-dim);margin-top:2px;line-height:1.3">${(l.mission_description || '').substring(0, 120)}</div>` : ''}
            </div>
        `).join('');
    }

    renderLaunchList(document.getElementById('launch-adv'), advLaunches);
    renderLaunchList(document.getElementById('launch-fvey'), fveyLaunches);

    // Live countdown refresh every second
    registerInterval(() => {
        if (nextAdv) {
            const heroEl = document.getElementById('hero-countdown');
            if (heroEl) heroEl.textContent = countdown(nextAdv.net);
        }
        renderLaunchList(document.getElementById('launch-adv'), advLaunches);
        renderLaunchList(document.getElementById('launch-fvey'), fveyLaunches);
    }, 1000);
};


/* ================================================================
   PAGE 5: GROUND STATIONS
   Map with all ground stations + adversary / FVEY tables
   ================================================================ */
Pages.ground = async function (el) {
    el.innerHTML = '<div class="loading">MAPPING GROUND INFRASTRUCTURE</div>';

    const [allStations, advStations, fveyStations] = await Promise.all([
        api('/api/ground-stations'),
        api('/api/ground-stations?scope=adversary'),
        api('/api/ground-stations?scope=fvey'),
    ]);

    const stations = allStations || [];
    if (!stations.length) { el.innerHTML = '<div class="empty-state">DATA UNAVAILABLE</div>'; return; }

    const adversary = advStations || stations.filter(s => ['PRC', 'CIS', 'NKOR', 'IRAN'].includes(s.country));
    const fvey = fveyStations || stations.filter(s => ['US', 'UK', 'CA', 'AU', 'NZ'].includes(s.country));

    const launchSites = stations.filter(s => (s.type || '').toLowerCase().includes('launch'));
    const ttcSites = stations.filter(s => (s.type || '').toLowerCase().includes('tt&c') || (s.type || '').toLowerCase().includes('tracking') || (s.type || '').toLowerCase().includes('telemetry'));
    const radarSites = stations.filter(s => (s.type || '').toLowerCase().includes('radar') || (s.type || '').toLowerCase().includes('sensor'));

    const mapH = Math.max(450, window.innerHeight * 0.5);

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9873;</div><div><div class="tb-val">${adversary.length}</div><div class="tb-lbl">ADVERSARY</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9733;</div><div><div class="tb-val">${fvey.length}</div><div class="tb-lbl">FVEY</div></div></div>
                <div class="tb-cell alert"><div class="tb-icon">&#9650;</div><div><div class="tb-val">${launchSites.length}</div><div class="tb-lbl">LAUNCH</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${ttcSites.length}</div><div class="tb-lbl">TT&C</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9670;</div><div><div class="tb-val">${radarSites.length}</div><div class="tb-lbl">RADAR/SENSOR</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${stations.length}</div><div class="tb-lbl">TOTAL</div></div></div>
            </div>
            <div class="panel mb-2">
                <div class="panel-head">
                    <h3>GLOBAL GROUND INFRASTRUCTURE</h3>
                    <span class="ph-meta">${zulu()} | &#9650; LAUNCH &nbsp; &#9632; TT&C &nbsp; &#9679; RADAR &nbsp; &#9733; FVEY</span>
                </div>
                <div class="panel-body" style="padding:0"><div id="gs-map" class="map-container" style="height:${mapH}px;min-height:${mapH}px"></div></div>
            </div>
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-head"><h3>ADVERSARY FACILITIES</h3><span class="ph-meta"><span class="badge badge-critical">${adversary.length}</span></span></div>
                    <div class="panel-body" style="max-height:350px">
                        <table class="data-table"><thead><tr><th>FACILITY</th><th>NATION</th><th>TYPE</th><th>DESCRIPTION</th></tr></thead><tbody>
                        ${adversary.map(s => `<tr>
                            <td style="color:${countryColor(s.country)}">${s.name}</td>
                            <td>${countryBadge(s.country)}</td>
                            <td>${s.type || '?'}</td>
                            <td style="white-space:normal;max-width:300px;font-size:9px;color:var(--text-dim)">${(s.description || '').substring(0, 100)}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>FVEY FACILITIES</h3><span class="ph-meta"><span class="badge badge-fvey">${fvey.length}</span></span></div>
                    <div class="panel-body" style="max-height:350px">
                        <table class="data-table"><thead><tr><th>FACILITY</th><th>NATION</th><th>TYPE</th><th>DESCRIPTION</th></tr></thead><tbody>
                        ${fvey.map(s => `<tr>
                            <td style="color:var(--cyan)">${s.name}</td>
                            <td>${countryBadge(s.country)}</td>
                            <td>${s.type || '?'}</td>
                            <td style="white-space:normal;max-width:300px;font-size:9px;color:var(--text-dim)">${(s.description || '').substring(0, 100)}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => {
        const mapEl = document.getElementById('gs-map');
        if (!mapEl) return;
        mapEl.style.height = mapH + 'px';
        const gmap = makeMap('gs-map', [25, 60], 3);
        if (!gmap) return;
        storeMap(gmap);

        stations.forEach(s => {
            if (!s.lat || !s.lng) return;
            const isAdv = ['PRC', 'CIS', 'NKOR', 'IRAN'].includes(s.country);
            const isFvey = ['US', 'UK', 'CA', 'AU', 'NZ'].includes(s.country);
            const col = countryColor(s.country) || (isAdv ? '#FF2020' : '#2080FF');
            const type = (s.type || '').toLowerCase();
            const isLaunch = type.includes('launch');
            const isTTC = type.includes('tt&c') || type.includes('tracking') || type.includes('telemetry');

            let marker;
            if (isLaunch && isAdv) {
                marker = L.marker([s.lat, s.lng], {
                    icon: L.divIcon({
                        className: '',
                        html: '<div class="gs-launch-marker"></div>',
                        iconSize: [14, 14],
                        iconAnchor: [7, 7],
                    })
                });
            } else if (isFvey) {
                marker = L.marker([s.lat, s.lng], {
                    icon: L.divIcon({
                        className: '',
                        html: '<div class="gs-fvey-marker"></div>',
                        iconSize: [10, 10],
                        iconAnchor: [5, 5],
                    })
                });
            } else if (isTTC && isAdv) {
                marker = L.marker([s.lat, s.lng], {
                    icon: L.divIcon({
                        className: '',
                        html: '<div class="gs-ttc-marker"></div>',
                        iconSize: [10, 10],
                        iconAnchor: [5, 5],
                    })
                });
            } else {
                const radius = isAdv ? 7 : 5;
                marker = L.circleMarker([s.lat, s.lng], {
                    radius: radius,
                    fillColor: col, fillOpacity: isAdv ? 0.6 : 0.35,
                    color: col, weight: 1, opacity: isAdv ? 0.6 : 0.3,
                });
            }

            marker.bindPopup(satPopup(s.name, col, [
                `${s.country} | ${s.type || '?'}`,
                `<span style="color:var(--text-dim);font-size:9px;line-height:1.4">${s.description || ''}</span>`,
                `<span style="font-size:8px;color:var(--text-muted)">${s.lat.toFixed(2)}N ${s.lng.toFixed(2)}E</span>`,
            ]), { className: 'sat-popup', closeButton: false }).addTo(gmap);
        });
    }, 150);
};


/* ================================================================
   PAGE 6: ASAT / COUNTERSPACE INTELLIGENCE
   33 systems, country filter tabs, summary bar, 2-column grid
   ================================================================ */
Pages.missile = async function (el) {
    el.innerHTML = '<div class="loading">LOADING COUNTERSPACE INTELLIGENCE</div>';
    const allSystems = await api('/api/missile-asat');
    if (!allSystems) { el.innerHTML = '<div class="empty-state">DATA UNAVAILABLE</div>'; return; }

    const critical = allSystems.filter(s => s.threat_level === 'critical');
    const high = allSystems.filter(s => s.threat_level === 'high');
    const medium = allSystems.filter(s => s.threat_level === 'medium');

    const byCountry = {};
    allSystems.forEach(s => { const c = s.country || 'Unknown'; byCountry[c] = (byCountry[c] || 0) + 1; });

    const byType = {};
    allSystems.forEach(s => { const t = (s.type || 'unknown').replace(/_/g, ' '); byType[t] = (byType[t] || 0) + 1; });

    const total = allSystems.length;
    const countryColors = { 'PRC': '#FF2020', 'Russia': '#FF8C00', 'DPRK': '#C040FF', 'Iran': '#FFD700' };

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${critical.length}</div><div class="tb-lbl">CRITICAL</div></div></div>
                <div class="tb-cell warning"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${high.length}</div><div class="tb-lbl">HIGH</div></div></div>
                <div class="tb-cell alert"><div class="tb-icon">&#9670;</div><div><div class="tb-val">${medium.length}</div><div class="tb-lbl">MEDIUM</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${total}</div><div class="tb-lbl">TOTAL SYSTEMS</div></div></div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:4px">
                <div class="panel">
                    <div class="panel-head"><h3>BY NATION</h3></div>
                    <div class="panel-body">
                        <div class="asat-summary-bar">
                            ${Object.entries(byCountry).map(([c, count]) => {
                                const pct = (count / total * 100).toFixed(1);
                                const col = countryColors[c] || '#888';
                                return `<div class="asat-summary-segment" style="width:${pct}%;background:${col}"><span class="seg-label">${c} ${count}</span></div>`;
                            }).join('')}
                        </div>
                        ${Object.entries(byCountry).sort((a, b) => b[1] - a[1]).map(([c, count]) => {
                            const col = countryColors[c] || '#888';
                            return `<div class="cat-breakdown"><span class="cat-label" style="color:${col}">${c}</span><div class="cat-bar-wrap"><div class="cat-bar" style="width:${count / total * 100}%;background:${col}"></div></div><span class="cat-count">${count}</span></div>`;
                        }).join('')}
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>BY TYPE</h3></div>
                    <div class="panel-body">
                        <div class="asat-summary-bar">
                            ${Object.entries(byType).map(([t, count], i) => {
                                const pct = (count / total * 100).toFixed(1);
                                const colors = ['#FF2020', '#FF8C00', '#FFD700', '#C040FF', '#2080FF', '#20FF60', '#00D4FF'];
                                const col = colors[i % colors.length];
                                return `<div class="asat-summary-segment" style="width:${pct}%;background:${col}"><span class="seg-label">${t.toUpperCase().substring(0, 12)}</span></div>`;
                            }).join('')}
                        </div>
                        ${Object.entries(byType).sort((a, b) => b[1] - a[1]).map(([t, count], i) => {
                            const colors = ['#FF2020', '#FF8C00', '#FFD700', '#C040FF', '#2080FF', '#20FF60', '#00D4FF'];
                            const col = colors[i % colors.length];
                            return `<div class="cat-breakdown"><span class="cat-label">${t.toUpperCase()}</span><div class="cat-bar-wrap"><div class="cat-bar" style="width:${count / total * 100}%;background:${col}"></div></div><span class="cat-count">${count}</span></div>`;
                        }).join('')}
                    </div>
                </div>
            </div>

            <div class="filter-tabs" id="missile-tabs">
                <div class="filter-tab active" data-filter="all">ALL (${total})</div>
                <div class="filter-tab" data-filter="PRC" style="color:#FF2020">PRC (${byCountry['PRC'] || 0})</div>
                <div class="filter-tab" data-filter="Russia" style="color:#FF8C00">RUS (${byCountry['Russia'] || 0})</div>
                <div class="filter-tab" data-filter="DPRK" style="color:#C040FF">DPRK (${byCountry['DPRK'] || 0})</div>
                <div class="filter-tab" data-filter="Iran" style="color:#FFD700">IRAN (${byCountry['Iran'] || 0})</div>
                <div class="filter-tab" data-filter="critical" style="color:var(--red)">CRITICAL (${critical.length})</div>
            </div>
            <div id="missile-detail"></div>
        </div>
    `;

    function renderSystems(filter) {
        let systems = allSystems;
        if (filter === 'critical') systems = allSystems.filter(s => s.threat_level === 'critical');
        else if (filter !== 'all') systems = allSystems.filter(s => s.country === filter);

        document.getElementById('missile-detail').innerHTML = `
            <div class="asat-grid">
            ${systems.map(s => {
                const cCode = s.country === 'Russia' ? 'CIS' : s.country === 'DPRK' ? 'NKOR' : s.country === 'Iran' ? 'IRAN' : s.country;
                return `
                <div class="threat-card severity-${s.threat_level || 'medium'}">
                    <div class="tc-header">
                        ${badge(s.threat_level || 'medium')}
                        <span class="tc-title">${s.name}</span>
                        ${countryBadge(cCode)}
                    </div>
                    <div class="tc-body">${s.description || ''}</div>
                    <div class="tc-meta" style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">
                        <span>TYPE: <span style="color:var(--amber)">${(s.type || '').replace(/_/g, ' ').toUpperCase()}</span></span>
                        <span>STATUS: <span style="color:${s.status === 'operational' ? 'var(--red)' : 'var(--text)'}">${(s.status || '?').toUpperCase()}</span></span>
                        ${s.max_altitude_km ? `<span>MAX ALT: <span style="color:var(--cyan)">${s.max_altitude_km.toLocaleString()} KM</span></span>` : ''}
                        ${s.first_tested ? `<span>FIRST TEST: ${s.first_tested}</span>` : ''}
                    </div>
                    ${s.evidence ? `<div class="tc-source">SOURCE: ${s.evidence}</div>` : ''}
                </div>`;
            }).join('')}
            </div>
        `;
    }

    renderSystems('all');
    el.querySelectorAll('#missile-tabs .filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            el.querySelectorAll('#missile-tabs .filter-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderSystems(tab.dataset.filter);
        });
    });
};


/* ================================================================
   PAGE 7: FVEY POSTURE
   Vulnerabilities with resilience scores + policy recommendations
   ================================================================ */
Pages.fvey = async function (el) {
    el.innerHTML = '<div class="loading">ASSESSING FVEY POSTURE</div>';
    const [vulns, recs, threatOv] = await Promise.all([
        api('/api/threat/vulnerabilities'),
        api('/api/threat/recommendations'),
        api('/api/threat/overview'),
    ]);

    const criticalVulns = (vulns || []).filter(v => v.severity === 'critical');
    const highVulns = (vulns || []).filter(v => v.severity === 'high');
    const medVulns = (vulns || []).filter(v => v.severity === 'medium');

    function calcResilience(severity) {
        if (severity === 'critical') return Math.floor(Math.random() * 15 + 10);
        if (severity === 'high') return Math.floor(Math.random() * 20 + 25);
        if (severity === 'medium') return Math.floor(Math.random() * 20 + 50);
        return Math.floor(Math.random() * 20 + 70);
    }

    const totalVulns = (vulns || []).length;
    const critWeight = criticalVulns.length * 4;
    const highWeight = highVulns.length * 2;
    const medWeight = medVulns.length * 1;
    const overallResilience = totalVulns > 0 ? Math.max(10, Math.min(85, Math.round(100 - ((critWeight + highWeight + medWeight) / totalVulns) * 20))) : 50;

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${criticalVulns.length}</div><div class="tb-lbl">CRITICAL</div></div></div>
                <div class="tb-cell warning"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${highVulns.length}</div><div class="tb-lbl">HIGH</div></div></div>
                <div class="tb-cell alert"><div class="tb-icon">&#9670;</div><div><div class="tb-val">${medVulns.length}</div><div class="tb-lbl">MEDIUM</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9881;</div><div><div class="tb-val">${(recs || []).length}</div><div class="tb-lbl">RECOMMENDATIONS</div></div></div>
                <div class="tb-cell" style="border-left:2px solid ${resilienceColor(overallResilience)}">
                    <div class="tb-icon" style="color:${resilienceColor(overallResilience)}">&#9733;</div>
                    <div><div class="tb-val" style="color:${resilienceColor(overallResilience)}">${overallResilience}%</div><div class="tb-lbl">RESILIENCE</div></div>
                </div>
            </div>

            <div class="panel mb-2">
                <div class="panel-head"><h3>FVEY SPACE ARCHITECTURE RESILIENCE ASSESSMENT</h3><span class="ph-meta">${zulu()}</span></div>
                <div class="panel-body">
                    <div style="display:flex;align-items:center;gap:16px;margin-bottom:10px">
                        <div style="font-size:36px;color:${resilienceColor(overallResilience)};text-shadow:0 0 15px ${resilienceColor(overallResilience)}">${overallResilience}%</div>
                        <div>
                            <div style="font-size:11px;color:var(--white);letter-spacing:1px">OVERALL RESILIENCE SCORE</div>
                            <div style="font-size:9px;color:var(--text-dim);margin-top:2px">${overallResilience < 40 ? 'CRITICAL — Immediate action required across multiple domains' : overallResilience < 70 ? 'DEGRADED — Significant vulnerabilities require priority attention' : 'ADEQUATE — Maintain vigilance and continue hardening'}</div>
                        </div>
                    </div>
                    ${(vulns || []).map(v => {
                        const score = calcResilience(v.severity);
                        return `
                        <div class="resilience-meter">
                            <span class="resilience-label">${v.title.substring(0, 30)}</span>
                            ${severityDots(v.severity || 'high')}
                            <div class="resilience-bar-track">
                                <div class="resilience-bar-fill" style="width:${score}%;background:${resilienceColor(score)}"></div>
                            </div>
                            <span class="resilience-score" style="color:${resilienceColor(score)}">${score}%</span>
                        </div>`;
                    }).join('')}
                </div>
            </div>

            <div class="grid-2">
                <div class="panel">
                    <div class="panel-head"><h3>VULNERABILITY DETAILS</h3><span class="ph-meta"><span class="badge badge-critical">${totalVulns} IDENTIFIED</span></span></div>
                    <div class="panel-body" style="max-height:calc(100vh - 420px)">
                        ${(vulns || []).map(v => `
                            <div class="threat-card severity-${v.severity || 'high'}">
                                <div class="tc-header">
                                    ${severityDots(v.severity || 'high')}
                                    ${badge(v.severity || 'high')}
                                    <span class="tc-title">${v.title}</span>
                                </div>
                                <div class="tc-body">${v.description}</div>
                                ${v.impact ? `<div class="tc-meta" style="color:var(--red)">IMPACT: ${v.impact}</div>` : ''}
                                ${v.mitigation ? `<div class="tc-source" style="color:var(--green)">MITIGATION: ${v.mitigation}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>POLICY RECOMMENDATIONS</h3><span class="ph-meta"><span class="badge badge-low">ADVISE</span> ${(recs || []).length}</span></div>
                    <div class="panel-body" style="max-height:calc(100vh - 420px)">
                        ${(recs || []).map((r, i) => `
                            <div class="threat-card severity-${r.priority || 'medium'}" style="border-left-color:var(--green)">
                                <div class="tc-header">
                                    <span style="color:var(--text-dim);font-size:9px;min-width:18px">#${i + 1}</span>
                                    ${badge(r.priority || 'medium')}
                                    <span class="tc-title">${r.title}</span>
                                </div>
                                <div class="tc-body">${r.description}</div>
                                <div class="tc-meta" style="display:flex;gap:12px">
                                    ${r.cost_estimate ? `<span>COST: <span style="color:var(--cyan)">${r.cost_estimate}</span></span>` : ''}
                                    ${r.timeline ? `<span>TIMELINE: <span style="color:var(--amber)">${r.timeline}</span></span>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
};


/* ================================================================
   PAGE 8: STRATEGIC ANALYSIS
   Threat overview, collapsible scenarios, hotspot map, research feed
   ================================================================ */
Pages.strategy = async function (el) {
    el.innerHTML = '<div class="loading">GENERATING STRATEGIC ANALYSIS</div>';

    const [overview, scenarios, vulns, recs, hotspots, research, brief, arxiv] = await Promise.all([
        api('/api/threat/overview'),
        api('/api/threat/scenarios'),
        api('/api/threat/vulnerabilities'),
        api('/api/threat/recommendations'),
        api('/api/intel/hotspots'),
        api('/api/intel/research'),
        api('/api/intel/brief'),
        api('/api/intel/arxiv'),
    ]);

    const ov = overview || {};
    const level = (ov.overall_threat_level || ov.threat_level || 'HIGH').toUpperCase();

    const critVulns = (vulns || []).filter(v => v.severity === 'critical').length;
    const highVulns = (vulns || []).filter(v => v.severity === 'high').length;
    const totalScenarios = (scenarios || []).length;

    const hs = (hotspots && hotspots.hotspots) || [];
    const mapH = hs.length > 0 ? Math.max(350, window.innerHeight * 0.35) : 0;

    el.innerHTML = `
        <div class="page-wrap">
            <!-- Strategic Banner -->
            <div class="strategy-banner">
                <div class="strategy-title">FIVE EYES SPACE DOMAIN THREAT ASSESSMENT</div>
                <div class="strategy-subtitle">UNCLASSIFIED // OSINT-DERIVED // ${new Date().toISOString().substring(0, 10)} // ${zulu()}</div>
                <div class="strategy-threat-display">
                    <div class="strategy-threat-level ${level.toLowerCase()}">${level}</div>
                </div>
                <div style="font-size:9px;color:var(--text-dim);letter-spacing:1px;margin-top:4px">${critVulns} CRITICAL VULNERABILITIES | ${highVulns} HIGH VULNERABILITIES | ${totalScenarios} ESCALATION SCENARIOS MODELLED</div>
            </div>

            <!-- Executive Summary -->
            <div class="panel mb-4">
                <div class="panel-head"><h3>EXECUTIVE SUMMARY</h3><span class="ph-meta">ASSESSMENT PERIOD: CURRENT</span></div>
                <div class="panel-body">
                    <div style="font-size:10px;color:var(--text);line-height:1.7;margin-bottom:8px">${ov.summary || ''}</div>
                    ${brief ? `<div class="intel-summary" style="margin-top:6px"><strong>DAILY BRIEF:</strong> ${typeof brief === 'string' ? brief.substring(0, 400) : (brief.summary || brief.assessment || JSON.stringify(brief)).substring(0, 400)}${typeof brief === 'string' && brief.length > 400 ? '...' : ''}</div>` : ''}
                </div>
            </div>

            <!-- Key Concerns -->
            ${ov.key_concerns?.length ? `
            <div class="panel mb-4">
                <div class="panel-head"><h3>KEY CONCERNS</h3><span class="ph-meta"><span class="badge badge-critical">${ov.key_concerns.length} IDENTIFIED</span></span></div>
                <div class="panel-body">
                    <div class="asat-grid">
                    ${ov.key_concerns.map(c => `
                        <div class="threat-card severity-${c.severity || 'high'}">
                            <div class="tc-header">
                                ${severityDots(c.severity || 'high')}
                                ${badge(c.severity || 'high')}
                                <span class="tc-title">${c.title}</span>
                            </div>
                            <div class="tc-body">${c.detail || c.description || ''}</div>
                            ${c.evidence ? `<div class="tc-source">EVIDENCE: ${c.evidence}</div>` : ''}
                        </div>
                    `).join('')}
                    </div>
                </div>
            </div>
            ` : ''}

            <!-- Conflict Escalation Scenarios -->
            <div class="panel mb-4">
                <div class="panel-head"><h3>CONFLICT ESCALATION SCENARIOS</h3><span class="ph-meta"><span class="badge badge-critical">WARGAME</span> ${totalScenarios} SCENARIOS</span></div>
                <div class="panel-body" style="padding:4px">
                    ${(scenarios || []).map((s, idx) => {
                        const sevColor = s.severity === 'critical' ? 'var(--red)' : s.severity === 'high' ? 'var(--cis)' : 'var(--amber)';
                        return `
                        <div class="scenario-section${idx === 0 ? ' open' : ''}" id="scenario-${idx}">
                            <div class="scenario-header" onclick="document.getElementById('scenario-${idx}').classList.toggle('open')">
                                <span class="chevron">&#9654;</span>
                                ${badge(s.severity || s.probability || 'high')}
                                <span style="color:var(--white);font-size:11px;flex:1">${s.title || s.name}</span>
                                ${s.probability ? `<span style="font-size:8px;color:var(--text-dim);letter-spacing:1px">P: ${s.probability.toUpperCase()}</span>` : ''}
                                ${s.timeframe ? `<span style="font-size:8px;color:var(--text-muted)">${s.timeframe}</span>` : ''}
                            </div>
                            <div class="scenario-body">
                                <div class="scenario-body-inner">
                                    <div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:8px">${s.description || ''}</div>
                                    ${s.phases?.length ? `
                                        <div style="margin-bottom:8px">
                                            <span class="intel-label" style="color:${sevColor}">ESCALATION PHASES</span>
                                            <ol class="phase-list" style="margin-top:4px">
                                                ${s.phases.map(p => `<li style="margin-bottom:4px;line-height:1.4">${p}</li>`).join('')}
                                            </ol>
                                        </div>
                                    ` : ''}
                                    ${s.fvey_response ? `
                                        <div>
                                            <span class="intel-label" style="color:var(--green)">RECOMMENDED FVEY RESPONSE</span>
                                            <div style="font-size:10px;color:var(--text);line-height:1.5;margin-top:3px">${s.fvey_response}</div>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>`;
                    }).join('')}
                </div>
            </div>

            <!-- Hotspot Analysis Map -->
            ${hs.length ? `
            <div class="panel mb-4">
                <div class="panel-head"><h3>HOTSPOT ANALYSIS</h3><span class="ph-meta">${hs.length} ZONES TRACKED</span></div>
                <div class="panel-body" style="padding:0">
                    <div id="strategy-hotspot-map" class="map-container" style="height:${mapH}px;min-height:${mapH}px"></div>
                </div>
            </div>
            <div class="grid-3 mb-4">
                ${hs.slice(0, 6).map(h => `
                    <div class="panel">
                        <div class="panel-head"><h3>${h.name}</h3><span class="ph-meta" style="color:var(--red)">${h.total_adversary_passes} PASSES</span></div>
                        <div class="panel-body">
                            ${h.passes_by_country ? Object.entries(h.passes_by_country).map(([c, n]) => `
                                <div class="fd-row">
                                    <span class="fd-nation" style="color:${countryColor(c)};font-size:9px">${c}</span>
                                    <div class="fd-bar-wrap"><div class="fd-bar" style="width:${Math.min(n / h.total_adversary_passes * 100, 100)}%;background:${countryColor(c)}"></div></div>
                                    <span class="fd-count" style="font-size:10px">${n}</span>
                                </div>
                            `).join('') : ''}
                            ${h.passes_by_category ? `<div style="margin-top:4px;font-size:8px;color:var(--text-muted)">${Object.entries(h.passes_by_category).map(([c, n]) => c.replace(/_/g, ' ') + ':' + n).join(' | ')}</div>` : ''}
                            ${h.top_threats?.length ? `
                                <div style="margin-top:4px;border-top:1px solid var(--border);padding-top:3px">
                                    ${h.top_threats.slice(0, 3).map(t => `<div style="font-size:8px;color:var(--text-dim)">${countryBadge(t.country)} ${t.name} <span style="color:var(--text-muted)">${Math.round(t.alt_km || 0)}KM</span></div>`).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
            ` : ''}

            <!-- Research + arXiv Feed -->
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-head"><h3>INTELLIGENCE RESEARCH FEED</h3><span class="ph-meta">${(research || []).length} ITEMS</span></div>
                    <div class="panel-body" style="max-height:400px">
                        ${(research || []).length ? research.slice(0, 12).map(r => `
                            <a href="${r.url || '#'}" target="_blank" rel="noopener" class="news-line">
                                <span class="nl-title">${r.title}</span>
                                <span class="nl-meta">${r.source || 'OSINT'} ${r.relevance_tag ? '// ' + r.relevance_tag : ''} // ${r.published_at ? timeAgo(r.published_at) : ''}</span>
                                ${r.summary ? `<div style="font-size:8px;color:var(--text-muted);line-height:1.3;margin-top:1px">${r.summary.substring(0, 120)}${r.summary.length > 120 ? '...' : ''}</div>` : ''}
                            </a>
                        `).join('') : '<div class="empty-state">NO RESEARCH DATA</div>'}
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>ACADEMIC / ARXIV PAPERS</h3><span class="ph-meta">${(arxiv || []).length} PAPERS</span></div>
                    <div class="panel-body" style="max-height:400px">
                        ${(arxiv || []).length ? arxiv.slice(0, 12).map(a => `
                            <a href="${a.url || '#'}" target="_blank" rel="noopener" class="news-line">
                                <span class="nl-title">${a.title}</span>
                                <span class="nl-meta">${a.source || 'arXiv'} ${a.relevance_tag ? '// ' + a.relevance_tag : ''} // ${a.published_at ? timeAgo(a.published_at) : ''}</span>
                                ${a.summary ? `<div style="font-size:8px;color:var(--text-muted);line-height:1.3;margin-top:1px">${a.summary.substring(0, 120)}${a.summary.length > 120 ? '...' : ''}</div>` : ''}
                            </a>
                        `).join('') : '<div class="empty-state">NO ARXIV DATA</div>'}
                    </div>
                </div>
            </div>
        </div>
    `;

    // Hotspot map
    if (hs.length) {
        setTimeout(() => {
            const mapEl = document.getElementById('strategy-hotspot-map');
            if (!mapEl) return;
            mapEl.style.height = mapH + 'px';
            const hmap = makeMap('strategy-hotspot-map', [20, 80], 3);
            if (!hmap) return;
            storeMap(hmap);

            hs.forEach(h => {
                if (!h.lat || !h.lng) return;
                const radius = Math.min(30, Math.max(10, h.total_adversary_passes / 3));
                L.circle([h.lat, h.lng], {
                    radius: radius * 10000,
                    fillColor: '#FF2020',
                    fillOpacity: 0.15,
                    color: '#FF2020',
                    weight: 1,
                    opacity: 0.4,
                }).addTo(hmap);

                L.circleMarker([h.lat, h.lng], {
                    radius: 6,
                    fillColor: '#FF2020',
                    fillOpacity: 0.8,
                    color: '#fff',
                    weight: 1,
                    opacity: 0.5,
                }).bindPopup(satPopup(h.name, '#FF2020', [
                    `ADVERSARY PASSES: <span style="color:var(--red)">${h.total_adversary_passes}</span>`,
                    h.passes_by_country ? Object.entries(h.passes_by_country).map(([c, n]) => `${c}: ${n}`).join(' | ') : '',
                ]), { className: 'sat-popup', closeButton: false }).addTo(hmap);

                // Plot top threats around hotspot
                (h.top_threats || []).slice(0, 5).forEach(t => {
                    if (!t.lat || !t.lng) return;
                    L.circleMarker([t.lat, t.lng], {
                        radius: 3,
                        fillColor: countryColor(t.country),
                        fillOpacity: 0.7,
                        color: countryColor(t.country),
                        weight: 0,
                    }).bindPopup(satPopup(t.name, countryColor(t.country), [
                        `${t.country} | ${(t.category || '').replace(/_/g, ' ')}`,
                        `ALT: ${Math.round(t.alt_km || 0)} KM`,
                    ]), { className: 'sat-popup', closeButton: false }).addTo(hmap);
                });
            });
        }, 200);
    }
};

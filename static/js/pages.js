/* ============================================================
   FVEY SDA — Page Renderers
   Combined Space Operations Center Display
   ECHELON VANTAGE — 14 Pages — Full Intelligence Dashboard
   v3.0 — Final Polish Pass
   ============================================================ */

const Pages = {};

/* ---- Helper Functions ---- */

function timeAgo(d) {
    const diff = Date.now() - new Date(d).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return 'JUST NOW';
    if (m < 60) return m + 'M AGO';
    const h = Math.floor(m / 60);
    if (h < 24) return h + 'H AGO';
    return Math.floor(h / 24) + 'D AGO';
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
    if (dd > 0) return 'T-' + dd + 'D ' + hh + ':' + mm + ':' + ss;
    return 'T-' + hh + ':' + mm + ':' + ss;
}

function badge(level) {
    var l = (level || 'medium').toLowerCase();
    return '<span class="badge badge-' + l + '">' + l.toUpperCase() + '</span>';
}

function countryBadge(c) {
    var map = { PRC: 'prc', CIS: 'cis', NKOR: 'nkor', IRAN: 'iran', US: 'fvey', UK: 'fvey', CA: 'fvey', AU: 'fvey', NZ: 'fvey' };
    var names = { PRC: 'PRC', CIS: 'RUS', NKOR: 'DPRK', IRAN: 'IRAN', US: 'US', UK: 'UK', CA: 'CA', AU: 'AU', NZ: 'NZ' };
    return '<span class="badge badge-' + (map[c] || 'fvey') + '">' + (names[c] || c) + '</span>';
}

function countryColor(c) {
    return { PRC: '#FF2020', CIS: '#FF8C00', NKOR: '#C040FF', IRAN: '#FFD700', US: '#2080FF', UK: '#2080FF', CA: '#2080FF', AU: '#2080FF', NZ: '#2080FF' }[c] || '#888';
}

function zulu() {
    return new Date().toISOString().substring(11, 19) + 'Z';
}

function zuluFull() {
    return new Date().toISOString().substring(0, 19).replace('T', ' ') + 'Z';
}

async function api(url) {
    try {
        var r = await fetch(url);
        return r.ok ? await r.json() : null;
    } catch (e) {
        return null;
    }
}

function registerInterval(fn, ms) {
    var id = setInterval(fn, ms);
    if (!window._pageIntervals) window._pageIntervals = [];
    window._pageIntervals.push(id);
    return id;
}

function storeMap(map) {
    if (!window._extraMaps) window._extraMaps = [];
    window._extraMaps.push(map);
}

function makeMap(elementId, center, zoom) {
    var el = document.getElementById(elementId);
    if (!el) return null;
    if (!el.style.height || el.offsetHeight < 50) {
        el.style.height = Math.max(400, window.innerHeight - 300) + 'px';
    }
    var map = L.map(elementId, {
        center: center || [20, 0],
        zoom: zoom || 2,
        minZoom: 2,
        maxZoom: 10,
        attributionControl: false,
    });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
    if (typeof addGridOverlay === 'function') addGridOverlay(map);
    setTimeout(function() { map.invalidateSize(); }, 200);
    setTimeout(function() { map.invalidateSize(); }, 1000);
    return map;
}

function severityDots(level) {
    var levels = ['low', 'medium', 'high', 'critical'];
    var idx = levels.indexOf((level || 'medium').toLowerCase());
    var html = '<span class="severity-dots">';
    for (var i = 0; i < levels.length; i++) {
        html += '<span class="severity-dot ' + (i <= idx ? 'filled-' + levels[i] : 'empty') + '"></span>';
    }
    html += '</span>';
    return html;
}

function resilienceColor(score) {
    if (score >= 70) return 'var(--green)';
    if (score >= 40) return 'var(--amber)';
    return 'var(--red)';
}

function resilienceLabel(score) {
    if (score >= 70) return 'ADEQUATE';
    if (score >= 40) return 'DEGRADED';
    return 'CRITICAL';
}

function overmatchColor(score) {
    if (score > 20) return 'var(--green)';
    if (score > -20) return 'var(--amber)';
    return 'var(--red)';
}

function overmatchVerdict(score) {
    if (score > 20) return { text: 'FVEY ADVANTAGE', cls: 'fvey-adv' };
    if (score > -20) return { text: 'CONTESTED', cls: 'contested' };
    return { text: 'ADVERSARY ADVANTAGE', cls: 'adv-adv' };
}

function livePulse(label, cls) {
    return '<span class="live-pulse ' + (cls || '') + '">' + (label || 'LIVE') + '</span>';
}

function liveIndicator(label) {
    return '<span class="live-indicator"><span class="live-indicator-dot"></span>' + (label || 'LIVE') + '</span>';
}

var ADV_PROVIDERS = ['CASC', 'China', 'Roscosmos', 'Russia', 'IRGC', 'Iran', 'DPRK', 'Korea', 'Khrunichev', 'Progress', 'ExPace', 'CASIC', 'Galactic Energy', 'LandSpace', 'iSpace', 'CAS Space', 'Orienspace', 'Space Pioneer'];

function isAdvLaunch(l) {
    return ADV_PROVIDERS.some(function(p) { return (l.provider || '').includes(p) || (l.name || '').includes(p); });
}

function satPopup(name, color, fields) {
    var html = '<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#e0e8f0;background:#000;padding:8px;min-width:200px">';
    html += '<div style="color:' + color + ';margin-bottom:4px;font-size:11px;letter-spacing:0.5px">' + name + '</div>';
    for (var i = 0; i < fields.length; i++) {
        html += '<div>' + fields[i] + '</div>';
    }
    html += '</div>';
    return html;
}

function buildOvermatchBar(label, score) {
    var color = overmatchColor(score);
    var absScore = Math.abs(score);
    var pct = (absScore / 100) * 50;
    var isPositive = score >= 0;
    var fillStyle = 'width:' + pct + '%;background:' + color + ';';
    if (!isPositive) fillStyle += 'right:auto;left:calc(50% - ' + pct + '%);';
    return '<div class="overmatch-bar-container">' +
        '<span class="overmatch-bar-label">' + label + '</span>' +
        '<div class="overmatch-bar-track">' +
        '<div class="overmatch-bar-fill ' + (isPositive ? 'positive' : 'negative') + '" style="' + fillStyle + '"></div>' +
        '</div>' +
        '<span class="overmatch-bar-score" style="color:' + color + '">' + (score > 0 ? '+' : '') + score + '</span>' +
        '</div>';
}

function buildHotspotBar(label, value, max, color) {
    var pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
    return '<div class="hotspot-bar-row">' +
        '<span class="hotspot-bar-label">' + label + '</span>' +
        '<div class="hotspot-bar-track">' +
        '<div class="hotspot-bar-fill" style="width:' + pct + '%;background:' + (color || 'var(--red)') + '"></div>' +
        '</div>' +
        '<span class="hotspot-bar-val">' + value + '</span>' +
        '</div>';
}

function buildResilienceBar(label, score, sevBadge) {
    var col = resilienceColor(score);
    var lbl = resilienceLabel(score);
    return '<div class="resilience-meter">' +
        '<span class="resilience-label">' + label + '</span>' +
        (sevBadge || '') +
        '<div class="resilience-bar-track">' +
        '<div class="resilience-bar-fill" style="width:' + score + '%;background:' + col + '"></div>' +
        '</div>' +
        '<span class="resilience-score" style="color:' + col + '">' + score + '%</span>' +
        '<span class="resilience-status" style="color:' + col + '">' + lbl + '</span>' +
        '</div>';
}


/* ================================================================
   PAGE 1: COMMAND OVERVIEW (CMD)
   Primary warfighting display -- map-dominant
   ================================================================ */
Pages.cmd = async function (el) {
    var vh = window.innerHeight;
    var chromeH = 80;
    var threatBarH = 44;
    var bottomStripH = 155;
    var envBarH = 56;
    var mapH = Math.max(300, vh - chromeH - threatBarH - bottomStripH - envBarH - 8);

    el.innerHTML = '<div class="cmd-page">' +
        '<!-- THREAT STATUS BAR -->' +
        '<div class="threat-bar">' +
            '<div class="tb-cell hostile">' +
                '<div class="tb-icon">&#9760;</div>' +
                '<div><div class="tb-val" id="ov-prc">--</div><div class="tb-lbl">PRC SATS</div></div>' +
            '</div>' +
            '<div class="tb-cell warning">' +
                '<div class="tb-icon">&#9760;</div>' +
                '<div><div class="tb-val" id="ov-rus">--</div><div class="tb-lbl">RUS SATS</div></div>' +
            '</div>' +
            '<div class="tb-cell hostile">' +
                '<div class="tb-icon">&#9673;</div>' +
                '<div><div class="tb-val" id="ov-isr-ct">--</div><div class="tb-lbl">HOSTILE ISR</div></div>' +
            '</div>' +
            '<div class="tb-cell alert">' +
                '<div class="tb-icon">&#9888;</div>' +
                '<div><div class="tb-val" id="ov-asat-ct">--</div><div class="tb-lbl">CRITICAL ASAT</div></div>' +
            '</div>' +
            '<div class="tb-cell info">' +
                '<div class="tb-icon">&#9678;</div>' +
                '<div><div class="tb-val" id="ov-total">--</div><div class="tb-lbl">TOTAL TRACKED</div></div>' +
            '</div>' +
            '<div class="tb-cell" id="ov-threat-cell">' +
                '<div class="tb-icon">&#9656;</div>' +
                '<div><div class="tb-val" id="ov-threat-lvl">--</div><div class="tb-lbl">THREAT LEVEL</div></div>' +
            '</div>' +
        '</div>' +

        '<!-- MAP + OVERLAY PANELS -->' +
        '<div class="cmd-layout" style="height:' + mapH + 'px">' +
            '<div class="cmd-map-wrap" style="height:' + mapH + 'px">' +
                '<div id="sat-map" class="map-container" style="height:' + mapH + 'px;min-height:' + mapH + 'px"></div>' +
                '<div class="map-legend">' +
                    '<div class="legend-item"><span class="legend-dot" style="background:#FF2020"></span> PRC</div>' +
                    '<div class="legend-item"><span class="legend-dot" style="background:#FF8C00"></span> RUS</div>' +
                    '<div class="legend-item"><span class="legend-dot" style="background:#C040FF"></span> DPRK</div>' +
                    '<div class="legend-item"><span class="legend-dot" style="background:#FFD700"></span> IRAN</div>' +
                    '<div class="legend-item"><span class="legend-dot" style="background:rgba(32,128,255,0.4)"></span> FVEY</div>' +
                    '<div class="legend-item" style="color:var(--text-muted)" id="ov-map-ts">--</div>' +
                '</div>' +
                '<div class="map-stat-overlay" id="ov-map-stats"></div>' +
                '<div class="map-overlay-panels">' +
                    '<div class="overlay-panel">' +
                        '<div class="op-head">FORCE DISPOSITION ' + liveIndicator('') + '</div>' +
                        '<div class="op-body" id="ov-force"></div>' +
                    '</div>' +
                    '<div class="overlay-panel">' +
                        '<div class="op-head">LIVE SITREP ' + liveIndicator('60S') + '</div>' +
                        '<div class="op-body" id="ov-sitrep" style="max-height:140px"></div>' +
                    '</div>' +
                    '<div class="overlay-panel" id="prox-panel">' +
                        '<div class="op-head" style="color:var(--red)">PROXIMITY ALERTS ' + livePulse('120S', 'red') + '</div>' +
                        '<div class="op-body" id="ov-proximity" style="max-height:130px"></div>' +
                    '</div>' +
                    '<div class="overlay-panel">' +
                        '<div class="op-head">ADVERSARY LAUNCH ACTIVITY ' + liveIndicator('1S') + '</div>' +
                        '<div class="op-body" id="ov-adv-launches" style="max-height:130px"></div>' +
                    '</div>' +
                    '<div class="overlay-panel" id="deductions-panel">' +
                        '<div class="op-head" style="color:var(--cyan)">TOP DEDUCTIONS ' + livePulse('120S', '') + '</div>' +
                        '<div class="op-body" id="ov-deductions" style="max-height:160px"><div class="empty-state">LOADING DEDUCTIONS</div></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +

        '<!-- BOTTOM STRIPS -->' +
        '<div class="cmd-bottom-strip">' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>HOTSPOT COVERAGE</h3><span class="ph-meta" id="ov-hotspot-meta"></span></div>' +
                '<div class="panel-body" style="max-height:120px" id="ov-hotspots"></div>' +
            '</div>' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>FVEY VULNERABILITIES</h3><span class="ph-meta"><span class="badge badge-critical">ASSESS</span></span></div>' +
                '<div class="panel-body" style="max-height:120px" id="ov-vulns"></div>' +
            '</div>' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>OSINT + SOCIAL INTEL</h3><span class="ph-meta" id="ov-news-ts">--</span></div>' +
                '<div class="panel-body" style="max-height:120px" id="ov-news"></div>' +
            '</div>' +
        '</div>' +

        '<!-- ENVIRONMENT BAR -->' +
        '<div class="env-bar">' +
            '<div class="env-cell"><span class="env-lbl">Kp</span><span class="env-val" id="ov-kp">--</span></div>' +
            '<div class="env-cell"><span class="env-lbl">SOLAR WIND</span><span class="env-val" id="ov-wind">--</span></div>' +
            '<div class="env-cell"><span class="env-lbl">Bz</span><span class="env-val" id="ov-bz">--</span></div>' +
            '<div class="env-cell"><span class="env-lbl">SFI</span><span class="env-val" id="ov-sfi">--</span></div>' +
            '<div class="env-cell"><span class="env-lbl">RADIO</span><span class="env-val" id="ov-sr">R0</span></div>' +
            '<div class="env-cell"><span class="env-lbl">SOLAR</span><span class="env-val" id="ov-ss">S0</span></div>' +
            '<div class="env-cell"><span class="env-lbl">GEOMAG</span><span class="env-val" id="ov-sg">G0</span></div>' +
            '<div class="env-cell"><span class="env-lbl">NEOs</span><span class="env-val" id="ov-neo">--</span></div>' +
            '<div class="env-cell"><span class="env-lbl">X-RAY</span><span class="env-val" id="ov-xray">--</span></div>' +
            '<div class="env-cell"><span class="env-lbl">AURORA</span><span class="env-val" id="ov-aurora">--</span></div>' +
            '<div class="env-cell"><span class="env-lbl">PROTON</span><span class="env-val" id="ov-proton">--</span></div>' +
            '<div class="cmd-kp-chart-wrap"><canvas id="kp-chart" height="50"></canvas></div>' +
        '</div>' +
        '</div>';

    // Init satellite map with explicit pixel height
    setTimeout(function() {
        var mapEl = document.getElementById('sat-map');
        if (!mapEl) return;
        mapEl.style.height = mapH + 'px';
        if (typeof initSatMap === 'function') {
            initSatMap('sat-map');
            if (satMap) {
                setTimeout(function() { satMap.invalidateSize(); }, 200);
                setTimeout(function() { satMap.invalidateSize(); }, 600);
                setTimeout(function() { satMap.invalidateSize(); }, 1500);
            }
        }
    }, 100);

    // Init Kp chart
    setTimeout(function() {
        if (typeof initKpChart === 'function') initKpChart();
    }, 200);

    // Fetch all data in parallel
    var results = await Promise.all([
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
        api('/api/intel/proximity'),
    ]);

    var advStats = results[0];
    var launches = results[1];
    var weather = results[2];
    var neo = results[3];
    var news = results[4];
    var criticalSystems = results[5];
    var vulns = results[6];
    var stats = results[7];
    var sitrep = results[8];
    var hotspots = results[9];
    var social = results[10];
    var proximity = results[11];

    // --- Threat bar ---
    if (advStats) {
        var prcS = advStats.PRC || {};
        var cisS = advStats.CIS || {};
        var nkorS = advStats.NKOR || {};
        var iranS = advStats.IRAN || {};
        document.getElementById('ov-prc').textContent = prcS.total || 0;
        document.getElementById('ov-rus').textContent = cisS.total || 0;
        document.getElementById('ov-isr-ct').textContent = (prcS.military_isr || 0) + (cisS.military_isr || 0) + (nkorS.military_isr || 0) + (iranS.military_isr || 0);
    }
    if (stats) {
        document.getElementById('ov-total').textContent = (stats.total_tracked || 0).toLocaleString();
    }
    if (criticalSystems) {
        document.getElementById('ov-asat-ct').textContent = criticalSystems.length;
    }

    // Sitrep threat level
    if (sitrep) {
        var lvl = (sitrep.threat_level || 'HIGH').toUpperCase();
        var tlEl = document.getElementById('ov-threat-lvl');
        var tcEl = document.getElementById('ov-threat-cell');
        if (tlEl) {
            tlEl.textContent = lvl;
            tlEl.style.color = lvl === 'CRITICAL' ? 'var(--red)' : lvl === 'HIGH' ? 'var(--cis)' : 'var(--amber)';
        }
        if (tcEl) {
            tcEl.className = 'tb-cell ' + (lvl === 'CRITICAL' ? 'hostile' : lvl === 'HIGH' ? 'warning' : 'alert');
        }
    }

    // Map stat overlay
    var mapStatsEl = document.getElementById('ov-map-stats');
    if (mapStatsEl && advStats && stats) {
        var totalAdv = (advStats.PRC ? advStats.PRC.total : 0) + (advStats.CIS ? advStats.CIS.total : 0) + (advStats.NKOR ? advStats.NKOR.total : 0) + (advStats.IRAN ? advStats.IRAN.total : 0);
        var totalISR = (advStats.PRC ? advStats.PRC.military_isr : 0) + (advStats.CIS ? advStats.CIS.military_isr : 0);
        mapStatsEl.innerHTML =
            '<div class="map-stat-item" style="border-left:2px solid var(--red)">' +
                '<div><div class="map-stat-val" style="color:var(--red)">' + totalAdv + '</div><div class="map-stat-lbl">HOSTILE ON ORBIT</div></div>' +
            '</div>' +
            '<div class="map-stat-item" style="border-left:2px solid var(--cyan)">' +
                '<div><div class="map-stat-val" style="color:var(--cyan)">' + (stats.active_payloads || 0).toLocaleString() + '</div><div class="map-stat-lbl">ACTIVE PAYLOADS</div></div>' +
            '</div>' +
            '<div class="map-stat-item" style="border-left:2px solid var(--amber)">' +
                '<div><div class="map-stat-val" style="color:var(--amber)">' + totalISR + '</div><div class="map-stat-lbl">ISR OVERHEAD</div></div>' +
            '</div>';
    }

    // Adversary launches
    var advLaunches = [];
    if (launches) {
        advLaunches = launches.filter(function(l) { return isAdvLaunch(l); });
    }

    // --- Force Disposition ---
    if (advStats) {
        var nations = [
            { code: 'PRC', name: 'PRC', data: advStats.PRC, color: '#FF2020' },
            { code: 'CIS', name: 'RUS', data: advStats.CIS, color: '#FF8C00' },
            { code: 'NKOR', name: 'DPRK', data: advStats.NKOR, color: '#C040FF' },
            { code: 'IRAN', name: 'IRAN', data: advStats.IRAN, color: '#FFD700' },
        ];
        var forceHtml = '';
        nations.forEach(function(n) {
            var d = n.data || {};
            var total = d.total || 0;
            var barMax = 600;
            var isr = d.military_isr || 0;
            var nav = d.navigation || 0;
            var cats = d.by_category || {};
            var comms = cats.comms || 0;
            var sdaAsat = cats.sda_asat || 0;
            forceHtml += '<div class="fd-row">' +
                '<span class="fd-nation" style="color:' + n.color + '">' + n.name + '</span>' +
                '<div class="fd-bar-wrap"><div class="fd-bar" style="width:' + Math.min(total / barMax * 100, 100) + '%;background:' + n.color + '"></div></div>' +
                '<span class="fd-count">' + total + '</span>' +
                '</div>' +
                '<div style="display:flex;gap:6px;margin:0 0 4px 54px;font-size:8px;color:var(--text-muted)">';
            if (isr) forceHtml += '<span>ISR:' + isr + '</span>';
            if (nav) forceHtml += '<span>NAV:' + nav + '</span>';
            if (comms) forceHtml += '<span>COM:' + comms + '</span>';
            if (sdaAsat) forceHtml += '<span style="color:var(--red)">ASAT:' + sdaAsat + '</span>';
            forceHtml += '</div>';
        });
        document.getElementById('ov-force').innerHTML = forceHtml;
    }

    // --- Live SITREP ---
    function renderSitrep(data) {
        var sitEl = document.getElementById('ov-sitrep');
        if (!sitEl || !data) return;
        var events = data.key_events || [];
        var html = '<div style="font-size:9px;color:var(--text);line-height:1.5;margin-bottom:4px">' + ((data.assessment || '').substring(0, 180)) + ((data.assessment || '').length > 180 ? '...' : '') + '</div>';
        events.slice(0, 4).forEach(function(e) {
            var desc = e.description || e.event || e.title || '';
            html += '<div style="padding:2px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:9px">' +
                badge(e.severity || 'medium') + ' <span style="color:var(--white)">' + desc + '</span></div>';
        });
        html += '<div style="font-size:7px;color:var(--text-muted);margin-top:3px">' + (data.timestamp ? timeAgo(data.timestamp) : zulu()) + '</div>';
        sitEl.innerHTML = html;
    }
    renderSitrep(sitrep);

    // --- Proximity Alerts ---
    function renderProximity(data) {
        var proxEl = document.getElementById('ov-proximity');
        var proxPanel = document.getElementById('prox-panel');
        if (!proxEl) return;
        if (!data || !data.alerts || !data.alerts.length) {
            proxEl.innerHTML = '<div style="font-size:9px;color:var(--green);text-align:center;padding:6px">NO ACTIVE PROXIMITY ALERTS</div>';
            if (proxPanel) proxPanel.classList.remove('proximity-flash');
            return;
        }
        // Flash animation on active alerts
        if (proxPanel) proxPanel.classList.add('proximity-flash');
        var html = '<div style="font-size:8px;color:var(--red);letter-spacing:1px;margin-bottom:3px;animation:blink-text 1.5s step-end infinite">' +
            '&#9888; ' + (data.total_alerts || data.alerts.length) + ' ACTIVE ALERTS</div>';
        data.alerts.slice(0, 5).forEach(function(a) {
            html += '<div class="prox-alert">' +
                '<div style="display:flex;justify-content:space-between;align-items:center">' +
                '<span style="color:var(--white);font-size:9px">' + (a.fvey_sat || '?') + '</span>' +
                '<span class="prox-alert-dist">' + (a.distance_km ? Math.round(a.distance_km) + ' KM' : '?') + '</span>' +
                '</div>' +
                '<div style="font-size:8px;color:var(--text-muted)">THREAT: ' + (a.adversary_sat || '?') + ' | ' + badge(a.classification || 'high') + '</div>' +
                '</div>';
        });
        html += '<div style="font-size:7px;color:var(--text-muted);margin-top:3px">' + zulu() + '</div>';
        proxEl.innerHTML = html;
    }
    renderProximity(proximity);

    // --- Adversary Launches (live countdown every second) ---
    function renderAdvLaunches() {
        var body = document.getElementById('ov-adv-launches');
        if (!body) return;
        if (!advLaunches.length) { body.innerHTML = '<div class="empty-state">NO ADV LAUNCHES SCHEDULED</div>'; return; }
        var html = '';
        advLaunches.slice(0, 5).forEach(function(l) {
            html += '<div class="launch-line ll-adv">' +
                '<div class="ll-name">&#9760; ' + l.name + '</div>' +
                '<div class="ll-detail">' + (l.provider || '?') + ' | ' + (l.rocket || '?') + ' | ' + (l.pad_location || '?') + '</div>' +
                '<div class="ll-countdown">' + (l.net ? countdown(l.net) : 'TBD') + '</div>' +
                '</div>';
        });
        body.innerHTML = html;
    }
    renderAdvLaunches();
    registerInterval(renderAdvLaunches, 1000);

    // --- Hotspot Coverage with colored bars ---
    if (hotspots && hotspots.hotspots) {
        var hs = hotspots.hotspots;
        var maxPasses = 1;
        hs.forEach(function(h) { if (h.total_adversary_passes > maxPasses) maxPasses = h.total_adversary_passes; });
        document.getElementById('ov-hotspot-meta').innerHTML = '<span class="badge badge-high">' + hs.length + ' ZONES</span>';
        var hotspotHtml = '';
        hs.slice(0, 6).forEach(function(h) {
            hotspotHtml += '<div class="hotspot-row">' +
                '<div style="display:flex;align-items:center;gap:6px;margin-bottom:2px">' +
                '<span style="color:var(--white);font-size:10px;flex:1">' + h.name + '</span>' +
                '<span style="color:var(--red);font-size:12px;font-weight:normal">' + h.total_adversary_passes + '</span>' +
                '</div>';
            // colored bar
            hotspotHtml += '<div class="hotspot-bar-track" style="margin-bottom:2px">' +
                '<div class="hotspot-bar-fill" style="width:' + (h.total_adversary_passes / maxPasses * 100) + '%;background:linear-gradient(90deg,var(--red),var(--cis))"></div>' +
                '</div>';
            // per-country mini bars
            if (h.passes_by_country) {
                hotspotHtml += '<div style="display:flex;gap:4px;margin-bottom:4px">';
                Object.keys(h.passes_by_country).forEach(function(c) {
                    var n = h.passes_by_country[c];
                    hotspotHtml += '<span style="font-size:7px;color:' + countryColor(c) + '">' + c + ':' + n + '</span>';
                });
                hotspotHtml += '</div>';
            }
            hotspotHtml += '</div>';
        });
        document.getElementById('ov-hotspots').innerHTML = hotspotHtml;
    }

    // --- Vulnerabilities ---
    if (vulns) {
        var sorted = vulns.slice().sort(function(a, b) {
            var order = { critical: 0, high: 1, medium: 2, low: 3 };
            return (order[a.severity] || 9) - (order[b.severity] || 9);
        });
        var vulnHtml = '';
        sorted.slice(0, 6).forEach(function(v) {
            vulnHtml += '<div class="vuln-line">' +
                severityDots(v.severity || 'high') + ' ' +
                badge(v.severity || 'high') + ' ' +
                '<span style="color:var(--white);font-size:10px">' + v.title + '</span>' +
                '</div>';
        });
        document.getElementById('ov-vulns').innerHTML = vulnHtml;
    }

    // --- OSINT + Social Intel ---
    var newsEl = document.getElementById('ov-news');
    if (newsEl) {
        var html = '';
        if (news) {
            news.slice(0, 4).forEach(function(n) {
                html += '<a href="' + n.url + '" target="_blank" rel="noopener" class="news-line">' +
                    '<span class="nl-title">' + n.title + '</span>' +
                    '<span class="nl-meta">' + (n.news_site || 'OSINT') + ' // ' + timeAgo(n.published_at) + '</span>' +
                    '</a>';
            });
        }
        if (social && social.length) {
            html += '<div style="border-top:1px solid var(--border);margin:3px 0;padding-top:2px;font-size:7px;letter-spacing:1.5px;color:var(--text-muted)">SOCIAL INTEL</div>';
            social.slice(0, 3).forEach(function(s) {
                var txt = (s.text || '').substring(0, 80);
                html += '<a href="' + (s.url || '#') + '" target="_blank" rel="noopener" class="news-line">' +
                    '<span class="nl-title" style="color:var(--cyan)">' + txt + (((s.text || '').length > 80) ? '...' : '') + '</span>' +
                    '<span class="nl-meta">' + (s.platform || '?') + ' / ' + (s.author || '?') + ' // ' + (s.relevance_score ? 'REL:' + s.relevance_score : '') + ' ' + (s.timestamp ? timeAgo(s.timestamp) : '') + '</span>' +
                    '</a>';
            });
        }
        newsEl.innerHTML = html || '<div class="empty-state">NO FEED DATA</div>';
        document.getElementById('ov-news-ts').textContent = zulu();
    }

    // --- Environment Bar ---
    if (weather) {
        if (weather.kp_current != null) {
            var kpEl = document.getElementById('ov-kp');
            kpEl.textContent = weather.kp_current.toFixed(1);
            kpEl.style.color = weather.kp_current < 4 ? 'var(--green)' : weather.kp_current < 6 ? '#FFD700' : 'var(--red)';
        }
        if (weather.solar_wind_speed != null) document.getElementById('ov-wind').textContent = Math.round(weather.solar_wind_speed) + ' KM/S';
        if (weather.bz != null) {
            var bzEl = document.getElementById('ov-bz');
            bzEl.textContent = weather.bz.toFixed(1);
            bzEl.style.color = weather.bz < 0 ? 'var(--red)' : 'var(--green)';
        }
        if (weather.sfi != null) document.getElementById('ov-sfi').textContent = Math.round(weather.sfi);
        if (weather.scales) {
            ['R', 'S', 'G'].forEach(function(k) {
                var v = (weather.scales[k] && weather.scales[k].Scale) || 0;
                var scaleEl = document.getElementById('ov-s' + k.toLowerCase());
                if (scaleEl) {
                    scaleEl.textContent = k + v;
                    scaleEl.style.color = v === 0 ? 'var(--green)' : v <= 2 ? '#FFD700' : 'var(--red)';
                }
            });
        }
        if (weather.kp_history && typeof updateKpChart === 'function') {
            setTimeout(function() { updateKpChart(weather.kp_history); }, 300);
        }
    }
    if (neo) document.getElementById('ov-neo').textContent = neo.length;

    // --- Enhanced env bar fields (X-ray, Aurora, Proton) ---
    function updateCmdEnvEnhanced(envData) {
        if (!envData) return;
        // X-ray level
        var goesD = envData.goes_instruments || {};
        var xrD = (goesD.xray || {}).latest || {};
        var xrKeys = Object.keys(xrD);
        if (xrKeys.length > 0) {
            var firstXr = xrD[xrKeys[0]];
            var fv = firstXr ? firstXr.flux : null;
            var xrEl = document.getElementById('ov-xray');
            if (xrEl && fv != null) {
                var lvl = 'A';
                var xc = 'var(--green)';
                if (fv >= 1e-4) { lvl = 'X'; xc = 'var(--red)'; }
                else if (fv >= 1e-5) { lvl = 'M'; xc = 'var(--cis)'; }
                else if (fv >= 1e-6) { lvl = 'C'; xc = 'var(--amber)'; }
                else if (fv >= 1e-7) { lvl = 'B'; xc = 'var(--green)'; }
                xrEl.textContent = lvl;
                xrEl.style.color = xc;
            }
        }
        // Aurora max probability
        var aurD = envData.aurora || {};
        var aurEl = document.getElementById('ov-aurora');
        if (aurEl && aurD.max_probability != null) {
            aurEl.textContent = aurD.max_probability + '%';
            aurEl.style.color = aurD.max_probability >= 50 ? 'var(--red)' : aurD.max_probability >= 25 ? 'var(--amber)' : 'var(--green)';
        }
        // Proton alert
        var prD = (goesD.protons || {}).latest || {};
        var prKeys = Object.keys(prD);
        var prEl = document.getElementById('ov-proton');
        if (prEl) {
            var prStatus = 'OK';
            var prColor = 'var(--green)';
            for (var prI = 0; prI < prKeys.length; prI++) {
                if (prKeys[prI].indexOf('10') >= 0) {
                    var prFlux = prD[prKeys[prI]] ? prD[prKeys[prI]].flux : null;
                    if (prFlux != null && prFlux >= 10) {
                        prStatus = 'S1+';
                        prColor = 'var(--red)';
                    }
                    break;
                }
            }
            prEl.textContent = prStatus;
            prEl.style.color = prColor;
        }
    }

    // Initial fetch for enhanced env bar
    api('/api/environment/enhanced').then(function(envData) {
        updateCmdEnvEnhanced(envData);
    });

    // --- MAP: Plot adversary & FVEY sats ---
    setTimeout(async function() {
        var satResults = await Promise.all([
            api('/api/adversary/satellites?country=PRC'),
            api('/api/adversary/satellites?country=CIS'),
            api('/api/adversary/satellites?country=NKOR'),
            api('/api/adversary/satellites?country=IRAN'),
            api('/api/satellites?group=stations'),
        ]);

        var prcSats = satResults[0];
        var cisSats = satResults[1];
        var nkorSats = satResults[2];
        var iranSats = satResults[3];
        var fveySats = satResults[4];

        if (!satMap) return;
        satMarkers.forEach(function(m) { satMap.removeLayer(m); });
        satMarkers = [];

        var allAdv = [];
        (prcSats || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _c: '#FF2020', _r: s.category === 'military_isr' ? 4 : s.category === 'sda_asat' ? 3.5 : 2.5 })); });
        (cisSats || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _c: '#FF8C00', _r: s.category === 'military_isr' ? 4 : s.category === 'sda_asat' ? 3.5 : 2.5 })); });
        (nkorSats || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _c: '#C040FF', _r: 5 })); });
        (iranSats || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _c: '#FFD700', _r: 5 })); });

        allAdv.forEach(function(s) {
            if (!s.lat || !s.lng) return;
            var isISR = s.category === 'military_isr';
            var isASAT = s.category === 'sda_asat';
            var m = L.circleMarker([s.lat, s.lng], {
                radius: s._r,
                fillColor: s._c,
                fillOpacity: isISR ? 0.85 : isASAT ? 0.75 : 0.5,
                color: isISR ? '#fff' : s._c,
                weight: isISR ? 1 : isASAT ? 1 : 0,
                opacity: isISR ? 0.3 : 0.2,
                className: isISR ? 'isr-pulse-marker' : '',
            }).bindPopup(satPopup(s.name, s._c, [
                'NORAD: ' + s.norad_id + ' | ' + s.country,
                'MISSION: <span style="color:' + (isISR ? 'var(--red)' : isASAT ? 'var(--cis)' : 'var(--text)') + '">' + (s.category || '').replace(/_/g, ' ').toUpperCase() + '</span>',
                'ALT: ' + Math.round(s.alt_km || 0) + ' KM | INC: ' + (s.inclination ? s.inclination.toFixed(1) : '?') + '&deg;',
                'REGIME: ' + (s.regime || '?'),
            ]), { className: 'sat-popup', closeButton: false }).addTo(satMap);
            satMarkers.push(m);
        });

        // FVEY sats (dim blue)
        (fveySats || []).forEach(function(s) {
            if (!s.lat || !s.lng) return;
            var isISS = s.norad_id === 25544;
            var m = L.circleMarker([s.lat, s.lng], {
                radius: isISS ? 6 : 1.5,
                fillColor: '#2080FF', fillOpacity: isISS ? 0.9 : 0.12,
                color: '#2080FF', weight: isISS ? 2 : 0,
            }).addTo(satMap);
            satMarkers.push(m);
        });

        var mapTsEl = document.getElementById('ov-map-ts');
        if (mapTsEl) mapTsEl.textContent = zulu();
    }, 350);

    // --- AUTO-REFRESH: Satellites every 30s ---
    registerInterval(async function() {
        if (!satMap) return;
        var refreshResults = await Promise.all([
            api('/api/adversary/satellites?country=PRC'),
            api('/api/adversary/satellites?country=CIS'),
            api('/api/adversary/satellites?country=NKOR'),
            api('/api/adversary/satellites?country=IRAN'),
        ]);
        satMarkers.forEach(function(m) { satMap.removeLayer(m); });
        satMarkers = [];
        var refresh = [];
        (refreshResults[0] || []).forEach(function(s) { refresh.push(Object.assign({}, s, { _c: '#FF2020', _r: s.category === 'military_isr' ? 4 : 2.5 })); });
        (refreshResults[1] || []).forEach(function(s) { refresh.push(Object.assign({}, s, { _c: '#FF8C00', _r: s.category === 'military_isr' ? 4 : 2.5 })); });
        (refreshResults[2] || []).forEach(function(s) { refresh.push(Object.assign({}, s, { _c: '#C040FF', _r: 5 })); });
        (refreshResults[3] || []).forEach(function(s) { refresh.push(Object.assign({}, s, { _c: '#FFD700', _r: 5 })); });
        refresh.forEach(function(s) {
            if (!s.lat || !s.lng) return;
            var m = L.circleMarker([s.lat, s.lng], {
                radius: s._r, fillColor: s._c, fillOpacity: 0.6,
                color: s._c, weight: 0,
            }).addTo(satMap);
            satMarkers.push(m);
        });
        var tsEl = document.getElementById('ov-map-ts');
        if (tsEl) tsEl.textContent = zulu();
    }, 30000);

    // --- AUTO-REFRESH: SITREP every 60s ---
    registerInterval(async function() {
        var freshSitrep = await api('/api/intel/sitrep');
        renderSitrep(freshSitrep);
    }, 60000);

    // --- AUTO-REFRESH: Proximity every 120s ---
    registerInterval(async function() {
        var freshProx = await api('/api/intel/proximity');
        renderProximity(freshProx);
    }, 120000);

    // --- AUTO-REFRESH: Weather every 60s ---
    registerInterval(async function() {
        var w = await api('/api/weather');
        if (!w) return;
        if (w.kp_current != null) {
            var kpRefEl = document.getElementById('ov-kp');
            if (kpRefEl) {
                kpRefEl.textContent = w.kp_current.toFixed(1);
                kpRefEl.style.color = w.kp_current < 4 ? 'var(--green)' : w.kp_current < 6 ? '#FFD700' : 'var(--red)';
            }
        }
        if (w.solar_wind_speed != null) {
            var wEl = document.getElementById('ov-wind');
            if (wEl) wEl.textContent = Math.round(w.solar_wind_speed) + ' KM/S';
        }
        if (w.kp_history && typeof updateKpChart === 'function') updateKpChart(w.kp_history);
    }, 60000);

    // --- TOP DEDUCTIONS (CMD overlay) ---
    function renderCmdDeductions(data) {
        var dedEl = document.getElementById('ov-deductions');
        if (!dedEl) return;
        if (!data || !Array.isArray(data) || !data.length) {
            dedEl.innerHTML = '<div class="empty-state">NO DEDUCTIONS AVAILABLE</div>';
            return;
        }
        var items = data.slice(0, 3);
        var dHtml = '';
        items.forEach(function(d, idx) {
            var conf = d.confidence || d.priority || 'medium';
            var confLower = (typeof conf === 'string') ? conf.toLowerCase() : 'medium';
            var badgeCls = confLower === 'critical' || confLower === 'high' ? 'badge-critical' : confLower === 'medium' ? 'badge-high' : 'badge-medium';
            dHtml += '<div style="padding:3px 0;border-bottom:1px solid rgba(0,212,255,0.08)">' +
                '<div style="display:flex;align-items:center;gap:4px">' +
                '<span style="color:var(--cyan);font-size:9px;font-weight:normal">#' + (idx + 1) + '</span>' +
                '<span class="badge ' + badgeCls + '">' + (d.category || confLower).toUpperCase() + '</span>' +
                '</div>' +
                '<div style="font-size:9px;color:var(--white);line-height:1.4;margin-top:2px">' + (d.title || d.deduction || '').substring(0, 100) + '</div>' +
                '</div>';
        });
        dHtml += '<div style="font-size:7px;color:var(--text-muted);margin-top:3px">' + zulu() + '</div>';
        dedEl.innerHTML = dHtml;
    }

    api('/api/deductions/priority').then(function(dedData) {
        renderCmdDeductions(dedData);
    });

    registerInterval(async function() {
        var freshDed = await api('/api/deductions/priority');
        renderCmdDeductions(freshDed);
    }, 120000);

    // --- AUTO-REFRESH: Launches every 120s ---
    registerInterval(async function() {
        var freshLaunches = await api('/api/launches');
        if (freshLaunches) {
            advLaunches = freshLaunches.filter(function(l) { return isAdvLaunch(l); });
        }
    }, 120000);

    // --- AUTO-REFRESH: Enhanced env bar (X-ray, Aurora, Proton) every 120s ---
    registerInterval(async function() {
        var freshEnvData = await api('/api/environment/enhanced');
        updateCmdEnvEnhanced(freshEnvData);
    }, 120000);
};


/* ================================================================
   PAGE 2: ADVERSARY PROFILES
   Country profiles with tabs -- PRC / RUS / DPRK / IRAN
   ================================================================ */
Pages.adversary = async function (el) {
    el.innerHTML = '<div class="loading">LOADING ADVERSARY INTELLIGENCE</div>';

    var results = await Promise.all([
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

    var advStatsData = results[0];
    var countries = [
        { code: 'PRC', name: 'CHINA', sats: results[1], threat: results[5], color: '#FF2020', stats: advStatsData ? advStatsData.PRC : null },
        { code: 'CIS', name: 'RUSSIA', sats: results[2], threat: results[6], color: '#FF8C00', stats: advStatsData ? advStatsData.CIS : null },
        { code: 'NKOR', name: 'DPRK', sats: results[3], threat: results[7], color: '#C040FF', stats: advStatsData ? advStatsData.NKOR : null },
        { code: 'IRAN', name: 'IRAN', sats: results[4], threat: results[8], color: '#FFD700', stats: advStatsData ? advStatsData.IRAN : null },
    ];

    var totalAll = 0;
    var totalISR = 0;
    countries.forEach(function(c) {
        totalAll += (c.stats ? c.stats.total : 0) || (c.sats ? c.sats.length : 0);
        totalISR += (c.stats ? c.stats.military_isr : 0) || 0;
    });

    var tabsHtml = '';
    countries.forEach(function(c, i) {
        var cnt = (c.stats ? c.stats.total : 0) || (c.sats ? c.sats.length : 0);
        tabsHtml += '<div class="country-tab' + (i === 0 ? ' active' : '') + '" data-country="' + c.code + '"' +
            (i === 0 ? ' style="color:' + c.color + '"' : '') + '>' +
            c.name + ' <span style="font-size:9px;opacity:0.5">' + cnt + '</span></div>';
    });

    var barHtml = '';
    countries.forEach(function(c) {
        var cnt = (c.stats ? c.stats.total : 0) || (c.sats ? c.sats.length : 0);
        barHtml += '<div class="tb-cell" style="border-left:2px solid ' + c.color + '">' +
            '<div class="tb-icon" style="color:' + c.color + '">&#9760;</div>' +
            '<div><div class="tb-val" style="color:' + c.color + '">' + cnt + '</div><div class="tb-lbl">' + c.name + '</div></div>' +
            '</div>';
    });

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' + barHtml +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9673;</div><div><div class="tb-val">' + totalISR + '</div><div class="tb-lbl">TOTAL ISR</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">' + totalAll + '</div><div class="tb-lbl">TOTAL HOSTILE</div></div></div>' +
            '<div class="tb-cell"><div><div class="tb-val"><span class="live-indicator"><span class="live-dot"></span> LIVE</span></div><div class="tb-lbl">60S REFRESH <span id="adv-live-ts" class="last-updated-ts">' + zulu() + '</span></div></div></div>' +
        '</div>' +
        '<div class="country-tabs" id="adv-tabs">' + tabsHtml + '</div>' +
        '<div id="adv-detail"></div>' +
        '</div>';

    var advMiniMap = null;

    function renderCountry(code) {
        var c = null;
        for (var i = 0; i < countries.length; i++) {
            if (countries[i].code === code) { c = countries[i]; break; }
        }
        if (!c) return;
        var sats = c.sats || [];
        var t = c.threat || {};
        var cats = {};
        var regimes = {};
        sats.forEach(function(s) {
            cats[s.category] = (cats[s.category] || 0) + 1;
            if (s.regime) regimes[s.regime] = (regimes[s.regime] || 0) + 1;
        });

        el.querySelectorAll('.country-tab').forEach(function(tab) {
            var tc = null;
            for (var j = 0; j < countries.length; j++) {
                if (countries[j].code === tab.dataset.country) { tc = countries[j]; break; }
            }
            tab.style.color = tab.classList.contains('active') ? tc.color : '';
        });

        if (advMiniMap) { try { advMiniMap.remove(); } catch (e) { } advMiniMap = null; }

        // Key threat line
        var keyThreat = t.trend || t.key_threat || '';
        var threatLevel = (t.overall_threat || 'high').toLowerCase();

        // Build mission breakdown
        var catEntries = Object.entries(cats).sort(function(a, b) { return b[1] - a[1]; });
        var catHtml = '';
        catEntries.forEach(function(entry) {
            var cat = entry[0];
            var count = entry[1];
            var pct = Math.round(count / sats.length * 100);
            var isMil = cat === 'military_isr' || cat === 'sda_asat';
            catHtml += '<div class="cat-breakdown">' +
                '<span class="cat-label" style="' + (isMil ? 'color:var(--red)' : '') + '">' + cat.replace(/_/g, ' ') + '</span>' +
                '<div class="cat-bar-wrap"><div class="cat-bar" style="width:' + pct + '%;background:' + c.color + ';opacity:' + (isMil ? 0.9 : 0.6) + '"></div></div>' +
                '<span class="cat-count" style="color:' + c.color + '">' + count + '</span>' +
                '</div>';
        });

        // Build regime breakdown
        var regEntries = Object.entries(regimes).sort(function(a, b) { return b[1] - a[1]; });
        var regHtml = '';
        regEntries.forEach(function(entry) {
            var regime = entry[0];
            var count = entry[1];
            var pct = Math.round(count / sats.length * 100);
            regHtml += '<div class="cat-breakdown">' +
                '<span class="cat-label">' + regime + '</span>' +
                '<div class="cat-bar-wrap"><div class="cat-bar" style="width:' + pct + '%;background:' + c.color + ';opacity:0.5"></div></div>' +
                '<span class="cat-count">' + count + '</span>' +
                '</div>';
        });

        // Build capabilities list
        var capsHtml = '';
        if (t.key_capabilities && t.key_capabilities.length) {
            capsHtml = '<div class="intel-field"><span class="intel-label">KEY CAPABILITIES</span><ul style="margin:3px 0 0 14px;color:var(--text)">';
            t.key_capabilities.forEach(function(k) {
                capsHtml += '<li style="margin-bottom:3px;font-size:10px;line-height:1.4">' + k + '</li>';
            });
            capsHtml += '</ul></div>';
        }

        // Build intel gaps
        var gapsHtml = '';
        if (t.intelligence_gaps && t.intelligence_gaps.length) {
            gapsHtml = '<div class="intel-field intel-gap-field"><span class="intel-label" style="color:var(--cis)">&#9888; INTELLIGENCE GAPS</span><ul style="margin:3px 0 0 14px">';
            t.intelligence_gaps.forEach(function(g) {
                gapsHtml += '<li style="margin-bottom:3px;font-size:10px;line-height:1.4;color:var(--cis)">' + g + '</li>';
            });
            gapsHtml += '</ul></div>';
        }

        // Build satellite table rows
        var satRowsHtml = '';
        sats.slice(0, 200).forEach(function(s) {
            var catBadge = s.category === 'military_isr' ? 'critical' : s.category === 'sda_asat' ? 'high' : 'medium';
            satRowsHtml += '<tr>' +
                '<td style="color:' + c.color + '">' + (s.name || '?') + '</td>' +
                '<td>' + (s.norad_id || '?') + '</td>' +
                '<td>' + badge(catBadge) + ' ' + (s.category || '').replace(/_/g, ' ') + '</td>' +
                '<td>' + (s.regime || '?') + '</td>' +
                '<td>' + (s.alt_km ? Math.round(s.alt_km) : '?') + '</td>' +
                '<td>' + (s.inclination ? s.inclination.toFixed(1) + '\u00B0' : '?') + '</td>' +
                '</tr>';
        });

        document.getElementById('adv-detail').innerHTML =
            // Key threat banner
            (keyThreat ? '<div class="key-threat-banner" style="border-left-color:' + c.color + '">' +
                '<span class="intel-label">KEY THREAT ASSESSMENT</span> ' +
                '<span style="color:var(--red);font-size:11px">' + keyThreat + '</span> ' +
                badge(threatLevel) +
                '</div>' : '') +

            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:2px">' +
                '<div class="panel">' +
                    '<div class="panel-head"><h3>STRATEGIC ASSESSMENT</h3><span class="ph-meta">' + badge(threatLevel) + ' THREAT</span></div>' +
                    '<div class="panel-body" style="max-height:380px">' +
                        (t.trend ? '<div class="intel-summary"><strong>TREND:</strong> <span style="color:var(--red)">' + t.trend + '</span></div>' : '') +
                        '<div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:10px">' + (t.assessment || t.summary || '') + '</div>' +
                        (t.doctrine ? '<div class="intel-field doctrine-field"><span class="intel-label">DOCTRINE</span><div style="font-size:10px;line-height:1.5;color:var(--text)">' + t.doctrine + '</div></div>' : '') +
                        (t.strategic_context ? '<div class="intel-field doctrine-field"><span class="intel-label">STRATEGIC CONTEXT</span><div style="font-size:10px;line-height:1.5;color:var(--text)">' + t.strategic_context + '</div></div>' : '') +
                        capsHtml +
                        gapsHtml +
                    '</div>' +
                '</div>' +
                '<div class="panel">' +
                    '<div class="panel-head"><h3>' + c.name + ' ORBITAL POSITIONS</h3><span class="ph-meta">' + sats.length + ' ACTIVE</span></div>' +
                    '<div class="panel-body" style="padding:0"><div id="adv-mini-map" style="height:350px;min-height:350px;background:#000"></div></div>' +
                '</div>' +
            '</div>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:2px">' +
                '<div class="panel">' +
                    '<div class="panel-head"><h3>MISSION BREAKDOWN</h3><span class="ph-meta">' + Object.keys(cats).length + ' CATEGORIES</span></div>' +
                    '<div class="panel-body">' +
                        '<div style="font-size:28px;color:' + c.color + ';margin-bottom:8px">' + sats.length + ' <span style="font-size:10px;color:var(--text-dim)">ACTIVE SATELLITES</span></div>' +
                        catHtml +
                    '</div>' +
                '</div>' +
                '<div class="panel">' +
                    '<div class="panel-head"><h3>ORBITAL REGIME DISTRIBUTION</h3></div>' +
                    '<div class="panel-body">' + regHtml + '</div>' +
                '</div>' +
            '</div>' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>' + c.name + ' SATELLITE CATALOG</h3><span class="ph-meta">' + sats.length + ' OBJECTS</span></div>' +
                '<div class="panel-body" style="max-height:400px">' +
                    '<table class="data-table"><thead><tr>' +
                        '<th>DESIGNATION</th><th>NORAD</th><th>MISSION</th><th>REGIME</th><th>ALT KM</th><th>INC</th>' +
                    '</tr></thead><tbody>' + satRowsHtml + '</tbody></table>' +
                '</div>' +
            '</div>' +
            '<!-- CONSTELLATION ANALYSIS -->' +
            '<div id="adv-constellation-container"></div>';

        // Initialize mini map — larger and more prominent
        setTimeout(function() {
            var mapEl = document.getElementById('adv-mini-map');
            if (!mapEl) return;
            mapEl.style.height = '350px';
            var centerLng = code === 'PRC' ? 105 : code === 'CIS' ? 60 : code === 'NKOR' ? 127 : 52;
            advMiniMap = makeMap('adv-mini-map', [30, centerLng], 2);
            if (advMiniMap) {
                storeMap(advMiniMap);
                sats.forEach(function(s) {
                    if (!s.lat || !s.lng) return;
                    var isISR = s.category === 'military_isr';
                    var isASAT = s.category === 'sda_asat';
                    L.circleMarker([s.lat, s.lng], {
                        radius: isISR ? 4 : isASAT ? 3.5 : 2,
                        fillColor: c.color, fillOpacity: isISR ? 0.9 : 0.5,
                        color: isISR ? '#fff' : c.color, weight: isISR ? 1 : 0,
                        className: isISR ? 'isr-pulse-marker' : '',
                    }).bindPopup(satPopup(s.name, c.color, [
                        (s.category || '').replace(/_/g, ' ') + ' | ' + Math.round(s.alt_km || 0) + ' KM',
                    ]), { className: 'sat-popup', closeButton: false }).addTo(advMiniMap);
                });
            }
        }, 150);

        // Fetch constellation analysis for relevant constellations
        var constellationMap = {
            PRC: ['yaogan', 'jilin', 'beidou', 'shijian'],
            CIS: ['glonass', 'cosmos_isr'],
            NKOR: [],
            IRAN: []
        };
        var constellations = constellationMap[code] || [];
        if (constellations.length > 0) {
            var constContainer = document.getElementById('adv-constellation-container');
            if (constContainer) {
                constContainer.innerHTML = '<div class="section-head" style="margin-top:4px">CONSTELLATION ANALYSIS ' + liveIndicator('') + '</div>' +
                    '<div id="adv-constellation-body"><div class="loading">LOADING CONSTELLATION DATA</div></div>';

                var constPromises = constellations.map(function(cn) {
                    return api('/api/analysis/constellation/' + cn);
                });
                Promise.all(constPromises).then(function(constResults) {
                    var constBody = document.getElementById('adv-constellation-body');
                    if (!constBody) return;
                    var cHtml = '<div class="asat-grid">';
                    constellations.forEach(function(cn, ci) {
                        var cData = constResults[ci];
                        if (!cData) {
                            cHtml += '<div class="panel"><div class="panel-head"><h3>' + cn.toUpperCase() + '</h3></div>' +
                                '<div class="panel-body"><div class="empty-state">DATA UNAVAILABLE</div></div></div>';
                            return;
                        }
                        var cName = cData.constellation || cData.name || cn.toUpperCase();
                        var cTotal = cData.total_satellites || cData.count || 0;
                        var cAssess = cData.assessment || cData.analysis || cData.summary || '';
                        var cCapabilities = cData.capabilities || cData.key_capabilities || [];
                        var cRole = cData.primary_role || cData.mission || '';
                        cHtml += '<div class="panel"><div class="panel-head"><h3>' + cName.toUpperCase() + '</h3><span class="ph-meta">' +
                            (cTotal ? '<span class="badge badge-critical">' + cTotal + ' SATS</span>' : '') + '</span></div>' +
                            '<div class="panel-body">';
                        if (cRole) cHtml += '<div style="font-size:9px;color:var(--amber);letter-spacing:0.5px;margin-bottom:4px">ROLE: ' + cRole + '</div>';
                        if (cAssess) cHtml += '<div style="font-size:10px;color:var(--text);line-height:1.5;margin-bottom:6px">' + (typeof cAssess === 'string' ? cAssess : JSON.stringify(cAssess)) + '</div>';
                        if (Array.isArray(cCapabilities) && cCapabilities.length) {
                            cHtml += '<div><span class="intel-label">CAPABILITIES</span><ul style="margin:2px 0 0 14px;font-size:9px;color:var(--text)">';
                            cCapabilities.forEach(function(cap) {
                                cHtml += '<li style="margin-bottom:2px;line-height:1.3">' + (typeof cap === 'string' ? cap : JSON.stringify(cap)) + '</li>';
                            });
                            cHtml += '</ul></div>';
                        }
                        // Render any other top-level fields
                        if (cData.orbital_planes) cHtml += '<div style="font-size:9px;color:var(--text-dim);margin-top:4px">ORBITAL PLANES: ' + cData.orbital_planes + '</div>';
                        if (cData.revisit_time) cHtml += '<div style="font-size:9px;color:var(--text-dim)">REVISIT: ' + cData.revisit_time + '</div>';
                        if (cData.coverage) cHtml += '<div style="font-size:9px;color:var(--text-dim)">COVERAGE: ' + cData.coverage + '</div>';
                        cHtml += '</div></div>';
                    });
                    cHtml += '</div>';
                    constBody.innerHTML = cHtml;
                });
            }
        }
    }

    renderCountry('PRC');
    el.querySelectorAll('.country-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            el.querySelectorAll('.country-tab').forEach(function(t) { t.classList.remove('active'); });
            tab.classList.add('active');
            renderCountry(tab.dataset.country);
        });
    });

    // --- AUTO-REFRESH: Adversary stats & satellite data every 60s ---
    registerInterval(async function() {
        var freshResults = await Promise.all([
            api('/api/adversary/stats'),
            api('/api/adversary/satellites?country=PRC'),
            api('/api/adversary/satellites?country=CIS'),
            api('/api/adversary/satellites?country=NKOR'),
            api('/api/adversary/satellites?country=IRAN'),
        ]);
        var freshStats = freshResults[0];
        if (freshStats) {
            advStatsData = freshStats;
            countries[0].stats = freshStats.PRC;
            countries[1].stats = freshStats.CIS;
            countries[2].stats = freshStats.NKOR;
            countries[3].stats = freshStats.IRAN;
        }
        countries[0].sats = freshResults[1] || countries[0].sats;
        countries[1].sats = freshResults[2] || countries[1].sats;
        countries[2].sats = freshResults[3] || countries[2].sats;
        countries[3].sats = freshResults[4] || countries[3].sats;

        // Update threat bar counts
        var freshTotalAll = 0;
        var freshTotalISR = 0;
        countries.forEach(function(c) {
            freshTotalAll += (c.stats ? c.stats.total : 0) || (c.sats ? c.sats.length : 0);
            freshTotalISR += (c.stats ? c.stats.military_isr : 0) || 0;
        });

        // Re-render active country detail
        var activeTab = el.querySelector('.country-tab.active');
        if (activeTab) {
            renderCountry(activeTab.dataset.country);
        }

        // Update last-updated timestamp
        var advTsEl = document.getElementById('adv-live-ts');
        if (advTsEl) advTsEl.textContent = zulu();
    }, 60000);
};


/* ================================================================
   PAGE 3: ORBITAL THREATS
   Full adversary orbital map + tables by mission type + regime cards
   ================================================================ */
Pages.orbital = async function (el) {
    el.innerHTML = '<div class="loading">MAPPING ORBITAL THREATS</div>';

    var results = await Promise.all([
        api('/api/adversary/satellites?country=PRC'),
        api('/api/adversary/satellites?country=CIS'),
        api('/api/adversary/satellites?country=NKOR'),
        api('/api/adversary/satellites?country=IRAN'),
        api('/api/adversary/stats'),
    ]);

    var allAdv = [];
    (results[0] || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _nation: 'PRC' })); });
    (results[1] || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _nation: 'CIS' })); });
    (results[2] || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _nation: 'NKOR' })); });
    (results[3] || []).forEach(function(s) { allAdv.push(Object.assign({}, s, { _nation: 'IRAN' })); });

    var milISR = allAdv.filter(function(s) { return s.category === 'military_isr'; });
    var sda = allAdv.filter(function(s) { return s.category === 'sda_asat'; });
    var nav = allAdv.filter(function(s) { return s.category === 'navigation'; });
    var comms = allAdv.filter(function(s) { return s.category === 'comms'; });
    var other = allAdv.filter(function(s) { return !['military_isr', 'sda_asat', 'navigation', 'comms'].includes(s.category); });

    // Regime counts
    var regimes = {};
    allAdv.forEach(function(s) { if (s.regime) regimes[s.regime] = (regimes[s.regime] || 0) + 1; });
    var regimeSorted = Object.entries(regimes).sort(function(a, b) { return b[1] - a[1]; });

    var mapH = Math.max(450, window.innerHeight * 0.45);

    // Build regime strip
    var regimeStripHtml = '';
    regimeSorted.slice(0, 5).forEach(function(entry) {
        regimeStripHtml += '<div class="regime-card">' +
            '<div class="regime-card-val">' + entry[1] + '</div>' +
            '<div class="regime-card-label">' + entry[0] + '</div>' +
            '</div>';
    });

    // Build ISR table rows with aggressive coloring
    function buildOrbitalRows(arr, maxCount) {
        var html = '';
        arr.slice(0, maxCount || 100).forEach(function(s) {
            var isISR = s.category === 'military_isr';
            var rowStyle = isISR ? ' style="background:rgba(255,32,32,0.04)"' : '';
            html += '<tr' + rowStyle + '>' +
                '<td style="color:' + countryColor(s._nation) + '">' + s.name + '</td>' +
                '<td>' + countryBadge(s._nation) + '</td>' +
                '<td>' + (s.alt_km ? Math.round(s.alt_km) + ' KM' : '?') + '</td>' +
                '<td>' + (s.inclination ? s.inclination.toFixed(1) + '\u00B0' : '?') + '</td>' +
                '<td>' + (s.regime || '?') + '</td>' +
                '</tr>';
        });
        return html;
    }

    function buildSimpleRows(arr, maxCount) {
        var html = '';
        arr.slice(0, maxCount || 60).forEach(function(s) {
            html += '<tr>' +
                '<td style="color:' + countryColor(s._nation) + '">' + s.name + '</td>' +
                '<td>' + countryBadge(s._nation) + '</td>' +
                '<td>' + (s.alt_km ? Math.round(s.alt_km) + ' KM' : '?') + '</td>' +
                '<td>' + (s.regime || '?') + '</td>' +
                '</tr>';
        });
        return html;
    }

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">' + allAdv.length + '</div><div class="tb-lbl">TOTAL HOSTILE</div></div></div>' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9673;</div><div><div class="tb-val">' + milISR.length + '</div><div class="tb-lbl">ISR / RECON</div></div></div>' +
            '<div class="tb-cell alert"><div class="tb-icon">&#9888;</div><div><div class="tb-val">' + sda.length + '</div><div class="tb-lbl">SDA / ASAT</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">' + nav.length + '</div><div class="tb-lbl">PNT / NAV</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9656;</div><div><div class="tb-val">' + comms.length + '</div><div class="tb-lbl">COMMS</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9670;</div><div><div class="tb-val">' + other.length + '</div><div class="tb-lbl">OTHER</div></div></div>' +
            '<div class="tb-cell"><div><div class="tb-val"><span class="live-indicator"><span class="live-dot"></span> LIVE</span></div><div class="tb-lbl">30S REFRESH <span id="orbital-live-ts" class="last-updated-ts">' + zulu() + '</span></div></div></div>' +
        '</div>' +
        '<div class="regime-strip" id="orbital-regime-strip">' + regimeStripHtml + '</div>' +
        '<div class="panel mb-2">' +
            '<div class="panel-head"><h3>ADVERSARY ORBITAL ASSETS // GLOBAL VIEW</h3><span class="ph-meta"><span id="orbital-map-ts">' + zulu() + '</span> | <span id="orbital-obj-count">' + allAdv.length + '</span> OBJECTS</span></div>' +
            '<div class="panel-body" style="padding:0"><div id="orbital-map" class="map-container" style="height:' + mapH + 'px;min-height:' + mapH + 'px"></div></div>' +
        '</div>' +
        '<div class="grid-2 mb-2">' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>HOSTILE ISR / RECONNAISSANCE</h3><span class="ph-meta"><span class="badge badge-critical">' + milISR.length + ' TRACKED</span></span></div>' +
                '<div class="panel-body" style="max-height:350px">' +
                    '<table class="data-table isr-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>INC</th><th>REGIME</th></tr></thead><tbody>' +
                    buildOrbitalRows(milISR, 100) +
                    '</tbody></table>' +
                '</div>' +
            '</div>' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>SDA / ASAT-CAPABLE</h3><span class="ph-meta"><span class="badge badge-critical">' + sda.length + ' TRACKED</span></span></div>' +
                '<div class="panel-body" style="max-height:350px">' +
                    '<table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>INC</th><th>REGIME</th></tr></thead><tbody>' +
                    buildOrbitalRows(sda) +
                    '</tbody></table>' +
                '</div>' +
            '</div>' +
        '</div>' +
        '<div class="grid-3">' +
            '<div class="panel"><div class="panel-head"><h3>NAVIGATION / PNT</h3><span class="ph-meta">' + nav.length + '</span></div>' +
                '<div class="panel-body" style="max-height:250px"><table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>REGIME</th></tr></thead><tbody>' + buildSimpleRows(nav) + '</tbody></table></div></div>' +
            '<div class="panel"><div class="panel-head"><h3>COMMUNICATIONS</h3><span class="ph-meta">' + comms.length + '</span></div>' +
                '<div class="panel-body" style="max-height:250px"><table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>REGIME</th></tr></thead><tbody>' + buildSimpleRows(comms) + '</tbody></table></div></div>' +
            '<div class="panel"><div class="panel-head"><h3>OTHER / UNCAT</h3><span class="ph-meta">' + other.length + '</span></div>' +
                '<div class="panel-body" style="max-height:250px"><table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>REGIME</th></tr></thead><tbody>' + buildSimpleRows(other) + '</tbody></table></div></div>' +
        '</div>' +
        '</div>';

    setTimeout(function() {
        var mapEl = document.getElementById('orbital-map');
        if (!mapEl) return;
        mapEl.style.height = mapH + 'px';
        var omap = makeMap('orbital-map', [20, 0], 2);
        if (!omap) return;
        storeMap(omap);

        allAdv.forEach(function(s) {
            if (!s.lat || !s.lng) return;
            var col = countryColor(s._nation);
            var isISR = s.category === 'military_isr';
            var isASAT = s.category === 'sda_asat';
            var r = isASAT ? 5 : isISR ? 4 : s.category === 'navigation' ? 3 : 2.5;
            L.circleMarker([s.lat, s.lng], {
                radius: r,
                fillColor: col,
                fillOpacity: isISR ? 0.9 : isASAT ? 0.8 : 0.5,
                color: isISR ? '#fff' : col,
                weight: isISR ? 1.5 : isASAT ? 1.5 : 0,
                opacity: 0.4,
                className: isISR ? 'isr-pulse-marker' : '',
            }).bindPopup(satPopup(s.name, col, [
                s._nation + ' | ' + (s.category || '').replace(/_/g, ' ') + ' | ' + Math.round(s.alt_km || 0) + ' KM | ' + (s.regime || '?'),
            ]), { className: 'sat-popup', closeButton: false }).addTo(omap);
        });
    }, 150);

    // --- AUTO-REFRESH: Orbital satellite positions every 30s ---
    registerInterval(async function() {
        var freshResults = await Promise.all([
            api('/api/adversary/satellites?country=PRC'),
            api('/api/adversary/satellites?country=CIS'),
            api('/api/adversary/satellites?country=NKOR'),
            api('/api/adversary/satellites?country=IRAN'),
        ]);

        var freshAdv = [];
        (freshResults[0] || []).forEach(function(s) { freshAdv.push(Object.assign({}, s, { _nation: 'PRC' })); });
        (freshResults[1] || []).forEach(function(s) { freshAdv.push(Object.assign({}, s, { _nation: 'CIS' })); });
        (freshResults[2] || []).forEach(function(s) { freshAdv.push(Object.assign({}, s, { _nation: 'NKOR' })); });
        (freshResults[3] || []).forEach(function(s) { freshAdv.push(Object.assign({}, s, { _nation: 'IRAN' })); });

        if (freshAdv.length === 0) return;

        // Update threat bar counts
        var freshISR = freshAdv.filter(function(s) { return s.category === 'military_isr'; });
        var freshSDA = freshAdv.filter(function(s) { return s.category === 'sda_asat'; });
        var freshNav = freshAdv.filter(function(s) { return s.category === 'navigation'; });
        var freshComms = freshAdv.filter(function(s) { return s.category === 'comms'; });
        var freshOther = freshAdv.filter(function(s) { return !['military_isr', 'sda_asat', 'navigation', 'comms'].includes(s.category); });

        var tbVals = el.querySelectorAll('.tb-val');
        if (tbVals.length >= 6) {
            tbVals[0].textContent = freshAdv.length;
            tbVals[1].textContent = freshISR.length;
            tbVals[2].textContent = freshSDA.length;
            tbVals[3].textContent = freshNav.length;
            tbVals[4].textContent = freshComms.length;
            tbVals[5].textContent = freshOther.length;
        }

        // Update object count in map header
        var objCountEl = document.getElementById('orbital-obj-count');
        if (objCountEl) objCountEl.textContent = freshAdv.length;

        // Update map markers if map exists
        var existingMaps = window._extraMaps || [];
        var orbMap = existingMaps.length > 0 ? existingMaps[existingMaps.length - 1] : null;
        if (orbMap) {
            try {
                orbMap.eachLayer(function(layer) {
                    if (layer instanceof L.CircleMarker && !(layer instanceof L.Circle)) {
                        orbMap.removeLayer(layer);
                    }
                });
                freshAdv.forEach(function(s) {
                    if (!s.lat || !s.lng) return;
                    var col = countryColor(s._nation);
                    var isISR = s.category === 'military_isr';
                    var isASAT = s.category === 'sda_asat';
                    var r = isASAT ? 5 : isISR ? 4 : s.category === 'navigation' ? 3 : 2.5;
                    L.circleMarker([s.lat, s.lng], {
                        radius: r, fillColor: col,
                        fillOpacity: isISR ? 0.9 : isASAT ? 0.8 : 0.5,
                        color: isISR ? '#fff' : col,
                        weight: isISR ? 1.5 : isASAT ? 1.5 : 0,
                        opacity: 0.4,
                        className: isISR ? 'isr-pulse-marker' : '',
                    }).addTo(orbMap);
                });
            } catch (e) {
                // Map may have been destroyed
            }
        }

        // Update timestamps
        var mapTsEl = document.getElementById('orbital-map-ts');
        if (mapTsEl) mapTsEl.textContent = zulu();
        var liveTsEl = document.getElementById('orbital-live-ts');
        if (liveTsEl) liveTsEl.textContent = zulu();
    }, 30000);
};


/* ================================================================
   PAGE 4: LAUNCH MONITOR
   Hero countdown for next adversary launch + adversary vs allied split
   ================================================================ */
Pages.launches = async function (el) {
    el.innerHTML = '<div class="loading">LOADING LAUNCH INTELLIGENCE</div>';
    var data = await api('/api/launches');
    if (!data) { el.innerHTML = '<div class="empty-state">LAUNCH DATA UNAVAILABLE</div>'; return; }

    data.forEach(function(l) { l._isAdv = isAdvLaunch(l); });
    var advLaunches = data.filter(function(l) { return l._isAdv; });
    var fveyLaunches = data.filter(function(l) { return !l._isAdv; });

    var nextAdv = null;
    for (var i = 0; i < advLaunches.length; i++) {
        if (advLaunches[i].net && new Date(advLaunches[i].net).getTime() > Date.now()) {
            nextAdv = advLaunches[i];
            break;
        }
    }

    var heroHtml = '';
    if (nextAdv) {
        heroHtml = '<div class="launch-hero" id="launch-hero">' +
            '<div>' +
                '<div class="launch-hero-label">&#9760; NEXT ADVERSARY LAUNCH</div>' +
                '<div class="launch-hero-name">' + nextAdv.name + '</div>' +
                '<div class="launch-hero-meta">' + (nextAdv.provider || '?') + ' | ' + (nextAdv.rocket || '?') + ' | ' + (nextAdv.pad_location || '?') + '</div>' +
            '</div>' +
            '<div class="launch-hero-countdown" id="hero-countdown">' + countdown(nextAdv.net) + '</div>' +
        '</div>';
    }

    el.innerHTML = '<div class="page-wrap">' + heroHtml +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">' + advLaunches.length + '</div><div class="tb-lbl">ADVERSARY</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9733;</div><div><div class="tb-val">' + fveyLaunches.length + '</div><div class="tb-lbl">ALLIED / OTHER</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">' + data.length + '</div><div class="tb-lbl">TOTAL UPCOMING</div></div></div>' +
            '<div class="tb-cell"><div><div class="tb-val"><span class="live-indicator"><span class="live-dot"></span> LIVE</span></div><div class="tb-lbl">120S DATA <span id="launch-live-ts" class="last-updated-ts">' + zulu() + '</span></div></div></div>' +
        '</div>' +
        '<div class="grid-2">' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>ADVERSARY LAUNCHES</h3><span class="ph-meta"><span class="badge badge-critical">' + advLaunches.length + ' SCHEDULED</span> ' + livePulse('1S', 'red') + '</span></div>' +
                '<div class="panel-body" id="launch-adv" style="max-height:calc(100vh - 280px)"></div>' +
            '</div>' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>ALLIED / OTHER LAUNCHES</h3><span class="ph-meta">' + fveyLaunches.length + ' TOTAL ' + livePulse('1S', '') + '</span></div>' +
                '<div class="panel-body" id="launch-fvey" style="max-height:calc(100vh - 280px)"></div>' +
            '</div>' +
        '</div>' +
        '</div>';

    function renderLaunchList(container, launches) {
        if (!container) return;
        if (!launches.length) { container.innerHTML = '<div class="empty-state">NONE SCHEDULED</div>'; return; }
        var html = '';
        launches.forEach(function(l) {
            html += '<div class="launch-line ' + (l._isAdv ? 'll-adv' : '') + '">' +
                '<div style="display:flex;align-items:center;justify-content:space-between">' +
                '<div class="ll-name">' + (l._isAdv ? '&#9760; ' : '') + l.name + '</div>' +
                '<div class="ll-countdown" style="font-size:13px">' + (l.net ? countdown(l.net) : 'TBD') + '</div>' +
                '</div>' +
                '<div class="ll-detail">' + (l.provider || '?') + ' | ' + (l.rocket || '?') + ' | ' + (l.pad_location || '?') + '</div>' +
                (l.mission_description ? '<div style="font-size:9px;color:var(--text-dim);margin-top:2px;line-height:1.3">' + (l.mission_description || '').substring(0, 120) + '</div>' : '') +
                '</div>';
        });
        container.innerHTML = html;
    }

    renderLaunchList(document.getElementById('launch-adv'), advLaunches);
    renderLaunchList(document.getElementById('launch-fvey'), fveyLaunches);

    registerInterval(function() {
        if (nextAdv) {
            var heroEl = document.getElementById('hero-countdown');
            if (heroEl) heroEl.textContent = countdown(nextAdv.net);
        }
        renderLaunchList(document.getElementById('launch-adv'), advLaunches);
        renderLaunchList(document.getElementById('launch-fvey'), fveyLaunches);
    }, 1000);

    // --- AUTO-REFRESH: Launch data every 120s ---
    registerInterval(async function() {
        var freshData = await api('/api/launches');
        if (!freshData) return;
        freshData.forEach(function(l) { l._isAdv = isAdvLaunch(l); });
        advLaunches = freshData.filter(function(l) { return l._isAdv; });
        fveyLaunches = freshData.filter(function(l) { return !l._isAdv; });

        // Update next adversary launch
        nextAdv = null;
        for (var li = 0; li < advLaunches.length; li++) {
            if (advLaunches[li].net && new Date(advLaunches[li].net).getTime() > Date.now()) {
                nextAdv = advLaunches[li];
                break;
            }
        }

        // Update hero section
        var heroSection = document.getElementById('launch-hero');
        if (heroSection && nextAdv) {
            heroSection.querySelector('.launch-hero-name').textContent = nextAdv.name;
            heroSection.querySelector('.launch-hero-meta').textContent = (nextAdv.provider || '?') + ' | ' + (nextAdv.rocket || '?') + ' | ' + (nextAdv.pad_location || '?');
        }

        // Update threat bar counts
        var tbVals = el.querySelectorAll('.tb-val');
        if (tbVals.length >= 3) {
            tbVals[0].textContent = advLaunches.length;
            tbVals[1].textContent = fveyLaunches.length;
            tbVals[2].textContent = freshData.length;
        }

        // Update live timestamp
        var launchTsEl = document.getElementById('launch-live-ts');
        if (launchTsEl) launchTsEl.textContent = zulu();
    }, 120000);
};


/* ================================================================
   PAGE 5: GROUND STATIONS
   Map with custom markers + adversary / FVEY tables
   ================================================================ */
Pages.ground = async function (el) {
    el.innerHTML = '<div class="loading">MAPPING GROUND INFRASTRUCTURE</div>';

    var results = await Promise.all([
        api('/api/ground-stations'),
        api('/api/ground-stations?scope=adversary'),
        api('/api/ground-stations?scope=fvey'),
    ]);

    var stations = results[0] || [];
    if (!stations.length) { el.innerHTML = '<div class="empty-state">DATA UNAVAILABLE</div>'; return; }

    var adversary = results[1] || stations.filter(function(s) { return ['PRC', 'CIS', 'NKOR', 'IRAN'].includes(s.country); });
    var fvey = results[2] || stations.filter(function(s) { return ['US', 'UK', 'CA', 'AU', 'NZ'].includes(s.country); });

    var launchSites = stations.filter(function(s) { return (s.type || '').toLowerCase().includes('launch'); });
    var ttcSites = stations.filter(function(s) { var t = (s.type || '').toLowerCase(); return t.includes('tt&c') || t.includes('tracking') || t.includes('telemetry'); });
    var radarSites = stations.filter(function(s) { var t = (s.type || '').toLowerCase(); return t.includes('radar') || t.includes('sensor'); });

    var mapH = Math.max(450, window.innerHeight * 0.5);

    // Build adversary table
    var advTableHtml = '';
    adversary.forEach(function(s) {
        advTableHtml += '<tr>' +
            '<td style="color:' + countryColor(s.country) + '">' + s.name + '</td>' +
            '<td>' + countryBadge(s.country) + '</td>' +
            '<td>' + (s.type || '?') + '</td>' +
            '<td style="white-space:normal;max-width:300px;font-size:9px;color:var(--text-dim)">' + (s.description || '').substring(0, 100) + '</td>' +
            '</tr>';
    });

    var fveyTableHtml = '';
    fvey.forEach(function(s) {
        fveyTableHtml += '<tr>' +
            '<td style="color:var(--cyan)">' + s.name + '</td>' +
            '<td>' + countryBadge(s.country) + '</td>' +
            '<td>' + (s.type || '?') + '</td>' +
            '<td style="white-space:normal;max-width:300px;font-size:9px;color:var(--text-dim)">' + (s.description || '').substring(0, 100) + '</td>' +
            '</tr>';
    });

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9873;</div><div><div class="tb-val">' + adversary.length + '</div><div class="tb-lbl">ADVERSARY</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9733;</div><div><div class="tb-val">' + fvey.length + '</div><div class="tb-lbl">FVEY</div></div></div>' +
            '<div class="tb-cell alert"><div class="tb-icon">&#9650;</div><div><div class="tb-val">' + launchSites.length + '</div><div class="tb-lbl">LAUNCH</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9632;</div><div><div class="tb-val">' + ttcSites.length + '</div><div class="tb-lbl">TT&C</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9679;</div><div><div class="tb-val">' + radarSites.length + '</div><div class="tb-lbl">RADAR/SENSOR</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">' + stations.length + '</div><div class="tb-lbl">TOTAL</div></div></div>' +
        '</div>' +
        '<div class="panel mb-2">' +
            '<div class="panel-head">' +
                '<h3>GLOBAL GROUND INFRASTRUCTURE</h3>' +
                '<span class="ph-meta">' + zulu() + '</span>' +
            '</div>' +
            '<div class="panel-body" style="padding:0;position:relative">' +
                '<div id="gs-map" class="map-container" style="height:' + mapH + 'px;min-height:' + mapH + 'px"></div>' +
                '<div class="gs-legend">' +
                    '<div class="gs-legend-item"><div class="gs-launch-marker" style="width:10px;height:10px"></div> LAUNCH</div>' +
                    '<div class="gs-legend-item"><div class="gs-ttc-marker" style="width:8px;height:8px"></div> TT&C</div>' +
                    '<div class="gs-legend-item"><div class="gs-radar-marker" style="width:7px;height:7px"></div> RADAR</div>' +
                    '<div class="gs-legend-item"><div class="gs-fvey-marker" style="width:9px;height:9px"></div> FVEY</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
        '<div class="grid-2 mb-2">' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>ADVERSARY FACILITIES</h3><span class="ph-meta"><span class="badge badge-critical">' + adversary.length + '</span></span></div>' +
                '<div class="panel-body" style="max-height:350px"><table class="data-table"><thead><tr><th>FACILITY</th><th>NATION</th><th>TYPE</th><th>DESCRIPTION</th></tr></thead><tbody>' + advTableHtml + '</tbody></table></div>' +
            '</div>' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>FVEY FACILITIES</h3><span class="ph-meta"><span class="badge badge-fvey">' + fvey.length + '</span></span></div>' +
                '<div class="panel-body" style="max-height:350px"><table class="data-table"><thead><tr><th>FACILITY</th><th>NATION</th><th>TYPE</th><th>DESCRIPTION</th></tr></thead><tbody>' + fveyTableHtml + '</tbody></table></div>' +
            '</div>' +
        '</div>' +
        '<!-- SIGINT MAPPING -->' +
        '<div class="panel" id="ground-sigint-panel">' +
            '<div class="panel-head"><h3>SIGINT / ELINT CONSTELLATION MAPPING</h3><span class="ph-meta">' + liveIndicator('') + '</span></div>' +
            '<div class="panel-body" id="ground-sigint-body"><div class="loading">LOADING SIGINT DATA</div></div>' +
        '</div>' +
        '</div>';

    setTimeout(function() {
        var mapEl = document.getElementById('gs-map');
        if (!mapEl) return;
        mapEl.style.height = mapH + 'px';
        var gmap = makeMap('gs-map', [25, 60], 3);
        if (!gmap) return;
        storeMap(gmap);

        stations.forEach(function(s) {
            if (!s.lat || !s.lng) return;
            var isAdv = ['PRC', 'CIS', 'NKOR', 'IRAN'].includes(s.country);
            var isFvey = ['US', 'UK', 'CA', 'AU', 'NZ'].includes(s.country);
            var col = countryColor(s.country) || (isAdv ? '#FF2020' : '#2080FF');
            var type = (s.type || '').toLowerCase();
            var isLaunch = type.includes('launch');
            var isTTC = type.includes('tt&c') || type.includes('tracking') || type.includes('telemetry');

            var marker;
            if (isLaunch && isAdv) {
                marker = L.marker([s.lat, s.lng], {
                    icon: L.divIcon({ className: '', html: '<div class="gs-launch-marker"></div>', iconSize: [14, 14], iconAnchor: [7, 7] })
                });
            } else if (isFvey) {
                marker = L.marker([s.lat, s.lng], {
                    icon: L.divIcon({ className: '', html: '<div class="gs-fvey-marker"></div>', iconSize: [10, 10], iconAnchor: [5, 5] })
                });
            } else if (isTTC && isAdv) {
                marker = L.marker([s.lat, s.lng], {
                    icon: L.divIcon({ className: '', html: '<div class="gs-ttc-marker"></div>', iconSize: [10, 10], iconAnchor: [5, 5] })
                });
            } else {
                var radius = isAdv ? 7 : 5;
                marker = L.circleMarker([s.lat, s.lng], {
                    radius: radius, fillColor: col, fillOpacity: isAdv ? 0.6 : 0.35,
                    color: col, weight: 1, opacity: isAdv ? 0.6 : 0.3,
                });
            }

            marker.bindPopup(satPopup(s.name, col, [
                s.country + ' | ' + (s.type || '?'),
                '<span style="color:var(--text-dim);font-size:9px;line-height:1.4">' + (s.description || '') + '</span>',
                '<span style="font-size:8px;color:var(--text-muted)">' + s.lat.toFixed(2) + 'N ' + s.lng.toFixed(2) + 'E</span>',
            ]), { className: 'sat-popup', closeButton: false }).addTo(gmap);
        });
    }, 150);

    // Fetch SIGINT mapping data
    api('/api/analysis/sigint-mapping').then(function(sigintData) {
        var sigBody = document.getElementById('ground-sigint-body');
        if (!sigBody) return;
        if (!sigintData) {
            sigBody.innerHTML = '<div class="empty-state">SIGINT DATA UNAVAILABLE</div>';
            return;
        }
        var sHtml = '';
        if (typeof sigintData === 'string') {
            sHtml = '<div class="intel-summary" style="white-space:pre-line;line-height:1.6">' + sigintData + '</div>';
        } else {
            var sigArr = Array.isArray(sigintData) ? sigintData : (sigintData.constellations || sigintData.systems || sigintData.entries || [sigintData]);
            if (!Array.isArray(sigArr)) sigArr = [sigArr];
            sHtml = '<div class="asat-grid">';
            sigArr.forEach(function(s) {
                if (typeof s === 'string') {
                    sHtml += '<div style="padding:4px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:10px;color:var(--text)">' + s + '</div>';
                    return;
                }
                var sName = s.name || s.constellation || s.system || 'SIGINT SYSTEM';
                var sCountry = s.country || s.operator || '';
                var sCol = countryColor(sCountry === 'Russia' ? 'CIS' : sCountry === 'China' ? 'PRC' : sCountry) || 'var(--amber)';
                sHtml += '<div class="threat-card severity-high" style="border-left-color:' + sCol + '">' +
                    '<div class="tc-header">' +
                        (sCountry ? '<span class="badge" style="background:rgba(255,255,255,0.05);color:' + sCol + ';border:1px solid ' + sCol + '">' + sCountry.toUpperCase() + '</span> ' : '') +
                        '<span class="tc-title">' + sName + '</span>' +
                    '</div>' +
                    '<div class="tc-body">' + (s.description || s.mission || s.assessment || '') + '</div>' +
                    '<div class="tc-meta">' +
                        (s.frequency_range ? 'FREQ: ' + s.frequency_range + ' // ' : '') +
                        (s.orbit ? 'ORBIT: ' + s.orbit + ' // ' : '') +
                        (s.count ? 'COUNT: ' + s.count : '') +
                    '</div>' +
                '</div>';
            });
            sHtml += '</div>';
        }
        sigBody.innerHTML = sHtml;
    });
};


/* ================================================================
   PAGE 6: ASAT / COUNTERSPACE INTELLIGENCE
   33 systems, country filter tabs, summary bars, 2-column grid
   ================================================================ */
Pages.missile = async function (el) {
    el.innerHTML = '<div class="loading">LOADING COUNTERSPACE INTELLIGENCE</div>';
    var allSystems = await api('/api/missile-asat');
    if (!allSystems) { el.innerHTML = '<div class="empty-state">DATA UNAVAILABLE</div>'; return; }

    var critical = allSystems.filter(function(s) { return s.threat_level === 'critical'; });
    var high = allSystems.filter(function(s) { return s.threat_level === 'high'; });
    var medium = allSystems.filter(function(s) { return s.threat_level === 'medium'; });

    var byCountry = {};
    allSystems.forEach(function(s) { var c = s.country || 'Unknown'; byCountry[c] = (byCountry[c] || 0) + 1; });

    var byType = {};
    allSystems.forEach(function(s) { var t = (s.type || 'unknown').replace(/_/g, ' '); byType[t] = (byType[t] || 0) + 1; });

    var total = allSystems.length;
    var cc = { 'PRC': '#FF2020', 'Russia': '#FF8C00', 'DPRK': '#C040FF', 'Iran': '#FFD700' };

    // Build summary bars by nation
    var nationBarHtml = '';
    var nationBreakHtml = '';
    Object.entries(byCountry).forEach(function(entry) {
        var name = entry[0];
        var count = entry[1];
        var pct = (count / total * 100).toFixed(1);
        var col = cc[name] || '#888';
        nationBarHtml += '<div class="asat-summary-segment" style="width:' + pct + '%;background:' + col + '"><span class="seg-label">' + name + ' ' + count + '</span></div>';
    });
    Object.entries(byCountry).sort(function(a, b) { return b[1] - a[1]; }).forEach(function(entry) {
        var name = entry[0];
        var count = entry[1];
        var col = cc[name] || '#888';
        nationBreakHtml += '<div class="cat-breakdown"><span class="cat-label" style="color:' + col + '">' + name + '</span><div class="cat-bar-wrap"><div class="cat-bar" style="width:' + (count / total * 100) + '%;background:' + col + '"></div></div><span class="cat-count">' + count + '</span></div>';
    });

    var typeBarHtml = '';
    var typeBreakHtml = '';
    var typeColors = ['#FF2020', '#FF8C00', '#FFD700', '#C040FF', '#2080FF', '#20FF60', '#00D4FF'];
    var typeIdx = 0;
    Object.entries(byType).forEach(function(entry) {
        var name = entry[0];
        var count = entry[1];
        var pct = (count / total * 100).toFixed(1);
        var col = typeColors[typeIdx % typeColors.length];
        typeBarHtml += '<div class="asat-summary-segment" style="width:' + pct + '%;background:' + col + '"><span class="seg-label">' + name.toUpperCase().substring(0, 12) + '</span></div>';
        typeIdx++;
    });
    typeIdx = 0;
    Object.entries(byType).sort(function(a, b) { return b[1] - a[1]; }).forEach(function(entry) {
        var name = entry[0];
        var count = entry[1];
        var col = typeColors[typeIdx % typeColors.length];
        typeBreakHtml += '<div class="cat-breakdown"><span class="cat-label">' + name.toUpperCase() + '</span><div class="cat-bar-wrap"><div class="cat-bar" style="width:' + (count / total * 100) + '%;background:' + col + '"></div></div><span class="cat-count">' + count + '</span></div>';
        typeIdx++;
    });

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9888;</div><div><div class="tb-val">' + critical.length + '</div><div class="tb-lbl">CRITICAL</div></div></div>' +
            '<div class="tb-cell warning"><div class="tb-icon">&#9888;</div><div><div class="tb-val">' + high.length + '</div><div class="tb-lbl">HIGH</div></div></div>' +
            '<div class="tb-cell alert"><div class="tb-icon">&#9670;</div><div><div class="tb-val">' + medium.length + '</div><div class="tb-lbl">MEDIUM</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">' + total + '</div><div class="tb-lbl">TOTAL SYSTEMS</div></div></div>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:4px">' +
            '<div class="panel"><div class="panel-head"><h3>BY NATION</h3></div><div class="panel-body">' +
                '<div class="asat-summary-bar">' + nationBarHtml + '</div>' + nationBreakHtml +
            '</div></div>' +
            '<div class="panel"><div class="panel-head"><h3>BY TYPE</h3></div><div class="panel-body">' +
                '<div class="asat-summary-bar">' + typeBarHtml + '</div>' + typeBreakHtml +
            '</div></div>' +
        '</div>' +
        '<div class="filter-tabs" id="missile-tabs">' +
            '<div class="filter-tab active" data-filter="all">ALL (' + total + ')</div>' +
            '<div class="filter-tab" data-filter="PRC" style="color:#FF2020">PRC (' + (byCountry['PRC'] || 0) + ')</div>' +
            '<div class="filter-tab" data-filter="Russia" style="color:#FF8C00">RUS (' + (byCountry['Russia'] || 0) + ')</div>' +
            '<div class="filter-tab" data-filter="DPRK" style="color:#C040FF">DPRK (' + (byCountry['DPRK'] || 0) + ')</div>' +
            '<div class="filter-tab" data-filter="Iran" style="color:#FFD700">IRAN (' + (byCountry['Iran'] || 0) + ')</div>' +
            '<div class="filter-tab" data-filter="critical" style="color:var(--red)">CRITICAL (' + critical.length + ')</div>' +
        '</div>' +
        '<div id="missile-detail"></div>' +
        '<!-- ENGAGEMENT ENVELOPES -->' +
        '<div id="asat-envelopes-container"></div>' +
        '</div>';

    function renderSystems(filter) {
        var systems = allSystems;
        if (filter === 'critical') systems = allSystems.filter(function(s) { return s.threat_level === 'critical'; });
        else if (filter !== 'all') systems = allSystems.filter(function(s) { return s.country === filter; });

        var html = '<div class="asat-grid">';
        systems.forEach(function(s) {
            var cCode = s.country === 'Russia' ? 'CIS' : s.country === 'DPRK' ? 'NKOR' : s.country === 'Iran' ? 'IRAN' : s.country;
            var isCrit = s.threat_level === 'critical';
            html += '<div class="threat-card severity-' + (s.threat_level || 'medium') + (isCrit ? ' critical-glow' : '') + '">' +
                '<div class="tc-header">' +
                    badge(s.threat_level || 'medium') +
                    ' <span class="tc-title">' + s.name + '</span> ' +
                    countryBadge(cCode) +
                '</div>' +
                '<div class="tc-body">' + (s.description || '') + '</div>' +
                '<div class="tc-meta" style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px">' +
                    '<span>TYPE: <span style="color:var(--amber)">' + (s.type || '').replace(/_/g, ' ').toUpperCase() + '</span></span>' +
                    '<span>STATUS: <span style="color:' + (s.status === 'operational' ? 'var(--red)' : 'var(--text)') + '">' + (s.status || '?').toUpperCase() + '</span></span>' +
                    (s.max_altitude_km ? '<span>MAX ALT: <span style="color:var(--cyan)">' + s.max_altitude_km.toLocaleString() + ' KM</span></span>' : '') +
                    (s.first_tested ? '<span>FIRST TEST: ' + s.first_tested + '</span>' : '') +
                '</div>' +
                (s.evidence ? '<div class="tc-source">SOURCE: ' + s.evidence + '</div>' : '') +
            '</div>';
        });
        html += '</div>';
        document.getElementById('missile-detail').innerHTML = html;
    }

    renderSystems('all');
    el.querySelectorAll('#missile-tabs .filter-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            el.querySelectorAll('#missile-tabs .filter-tab').forEach(function(t) { t.classList.remove('active'); });
            tab.classList.add('active');
            renderSystems(tab.dataset.filter);
        });
    });

    // Fetch engagement envelopes (optional endpoint)
    api('/api/analysis/engagement-envelopes').then(function(envData) {
        var envContainer = document.getElementById('asat-envelopes-container');
        if (!envContainer || !envData) return;
        var eHtml = '<div class="panel" style="margin-top:4px">' +
            '<div class="panel-head"><h3>ENGAGEMENT ENVELOPES</h3><span class="ph-meta">' + liveIndicator('') + '</span></div>' +
            '<div class="panel-body">';
        if (typeof envData === 'string') {
            eHtml += '<div class="intel-summary" style="white-space:pre-line">' + envData + '</div>';
        } else {
            var envArr = Array.isArray(envData) ? envData : (envData.envelopes || envData.systems || [envData]);
            if (!Array.isArray(envArr)) envArr = [envArr];
            eHtml += '<div class="asat-grid">';
            envArr.forEach(function(e) {
                if (typeof e === 'string') {
                    eHtml += '<div style="padding:4px;font-size:10px;color:var(--text)">' + e + '</div>';
                    return;
                }
                var eName = e.name || e.system || 'SYSTEM';
                var eCountry = e.country || e.operator || '';
                eHtml += '<div class="threat-card severity-critical" style="border-left-color:var(--red)">' +
                    '<div class="tc-header">' +
                        (eCountry ? countryBadge(eCountry === 'Russia' ? 'CIS' : eCountry === 'DPRK' ? 'NKOR' : eCountry === 'Iran' ? 'IRAN' : eCountry) + ' ' : '') +
                        '<span class="tc-title">' + eName + '</span>' +
                    '</div>' +
                    '<div class="tc-body">' + (e.description || '') + '</div>' +
                    '<div class="tc-meta">' +
                        (e.min_altitude ? 'MIN ALT: ' + e.min_altitude + ' KM // ' : '') +
                        (e.max_altitude ? 'MAX ALT: ' + e.max_altitude + ' KM // ' : '') +
                        (e.engagement_time ? 'ENG TIME: ' + e.engagement_time : '') +
                    '</div>' +
                '</div>';
            });
            eHtml += '</div>';
        }
        eHtml += '</div></div>';
        envContainer.innerHTML = eHtml;
    });
};


/* ================================================================
   PAGE 7: FVEY POSTURE
   Vulnerabilities with resilience scores + policy recommendations
   ================================================================ */
Pages.fvey = async function (el) {
    el.innerHTML = '<div class="loading">ASSESSING FVEY POSTURE</div>';
    var results = await Promise.all([
        api('/api/threat/vulnerabilities'),
        api('/api/threat/recommendations'),
        api('/api/threat/overview'),
    ]);

    var vulns = results[0] || [];
    var recs = results[1] || [];
    var threatOv = results[2] || {};

    var criticalVulns = vulns.filter(function(v) { return v.severity === 'critical'; });
    var highVulns = vulns.filter(function(v) { return v.severity === 'high'; });
    var medVulns = vulns.filter(function(v) { return v.severity === 'medium'; });

    function calcResilience(severity) {
        if (severity === 'critical') return Math.floor(Math.random() * 15 + 10);
        if (severity === 'high') return Math.floor(Math.random() * 20 + 25);
        if (severity === 'medium') return Math.floor(Math.random() * 20 + 50);
        return Math.floor(Math.random() * 20 + 70);
    }

    var totalVulns = vulns.length;
    var critWeight = criticalVulns.length * 4;
    var highWeight = highVulns.length * 2;
    var medWeight = medVulns.length * 1;
    var overallResilience = totalVulns > 0 ? Math.max(10, Math.min(85, Math.round(100 - ((critWeight + highWeight + medWeight) / totalVulns) * 20))) : 50;

    // Build resilience bars
    var resilienceBarsHtml = '';
    vulns.forEach(function(v) {
        var score = calcResilience(v.severity);
        resilienceBarsHtml += buildResilienceBar(
            v.title.substring(0, 30),
            score,
            severityDots(v.severity || 'high')
        );
    });

    // Build vulnerability cards
    var vulnCardsHtml = '';
    vulns.forEach(function(v) {
        vulnCardsHtml += '<div class="threat-card severity-' + (v.severity || 'high') + '">' +
            '<div class="tc-header">' +
                severityDots(v.severity || 'high') + ' ' +
                badge(v.severity || 'high') + ' ' +
                '<span class="tc-title">' + v.title + '</span>' +
            '</div>' +
            '<div class="tc-body">' + v.description + '</div>' +
            (v.impact ? '<div class="tc-meta" style="color:var(--red)">IMPACT: ' + v.impact + '</div>' : '') +
            (v.mitigation ? '<div class="tc-source" style="color:var(--green)">MITIGATION: ' + v.mitigation + '</div>' : '') +
            '</div>';
    });

    // Build recommendation cards
    var recCardsHtml = '';
    recs.forEach(function(r, i) {
        recCardsHtml += '<div class="threat-card severity-' + (r.priority || 'medium') + '" style="border-left-color:var(--green)">' +
            '<div class="tc-header">' +
                '<span class="rec-number">#' + (i + 1) + '</span> ' +
                badge(r.priority || 'medium') + ' ' +
                '<span class="tc-title">' + r.title + '</span>' +
            '</div>' +
            '<div class="tc-body">' + r.description + '</div>' +
            '<div class="tc-meta" style="display:flex;gap:12px">' +
                (r.cost_estimate ? '<span>COST: <span style="color:var(--cyan)">' + r.cost_estimate + '</span></span>' : '') +
                (r.timeline ? '<span>TIMELINE: <span style="color:var(--amber)">' + r.timeline + '</span></span>' : '') +
            '</div>' +
            '</div>';
    });

    var overallStatusText = overallResilience < 40 ? 'CRITICAL -- Immediate action required across multiple domains' :
        overallResilience < 70 ? 'DEGRADED -- Significant vulnerabilities require priority attention' :
        'ADEQUATE -- Maintain vigilance and continue hardening';

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9888;</div><div><div class="tb-val">' + criticalVulns.length + '</div><div class="tb-lbl">CRITICAL</div></div></div>' +
            '<div class="tb-cell warning"><div class="tb-icon">&#9888;</div><div><div class="tb-val">' + highVulns.length + '</div><div class="tb-lbl">HIGH</div></div></div>' +
            '<div class="tb-cell alert"><div class="tb-icon">&#9670;</div><div><div class="tb-val">' + medVulns.length + '</div><div class="tb-lbl">MEDIUM</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9881;</div><div><div class="tb-val">' + recs.length + '</div><div class="tb-lbl">RECOMMENDATIONS</div></div></div>' +
            '<div class="tb-cell" style="border-left:2px solid ' + resilienceColor(overallResilience) + '">' +
                '<div class="tb-icon" style="color:' + resilienceColor(overallResilience) + '">&#9733;</div>' +
                '<div><div class="tb-val" style="color:' + resilienceColor(overallResilience) + '">' + overallResilience + '%</div><div class="tb-lbl">RESILIENCE</div></div>' +
            '</div>' +
        '</div>' +
        '<div class="panel mb-2">' +
            '<div class="panel-head"><h3>FVEY SPACE ARCHITECTURE RESILIENCE ASSESSMENT</h3><span class="ph-meta">' + zulu() + '</span></div>' +
            '<div class="panel-body">' +
                '<div style="display:flex;align-items:center;gap:16px;margin-bottom:10px">' +
                    '<div style="font-size:36px;color:' + resilienceColor(overallResilience) + ';text-shadow:0 0 15px ' + resilienceColor(overallResilience) + '">' + overallResilience + '%</div>' +
                    '<div>' +
                        '<div style="font-size:11px;color:var(--white);letter-spacing:1px">OVERALL RESILIENCE SCORE</div>' +
                        '<div style="font-size:9px;color:var(--text-dim);margin-top:2px">' + overallStatusText + '</div>' +
                    '</div>' +
                '</div>' +
                resilienceBarsHtml +
            '</div>' +
        '</div>' +
        '<div class="grid-2">' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>VULNERABILITY DETAILS</h3><span class="ph-meta"><span class="badge badge-critical">' + totalVulns + ' IDENTIFIED</span></span></div>' +
                '<div class="panel-body" style="max-height:calc(100vh - 420px)">' + vulnCardsHtml + '</div>' +
            '</div>' +
            '<div class="panel">' +
                '<div class="panel-head"><h3>POLICY RECOMMENDATIONS</h3><span class="ph-meta"><span class="badge badge-low">ADVISE</span> ' + recs.length + '</span></div>' +
                '<div class="panel-body" style="max-height:calc(100vh - 420px)">' + recCardsHtml + '</div>' +
            '</div>' +
        '</div>' +
        '<!-- ALLIANCE & TREATY SECTIONS -->' +
        '<div class="grid-2" style="margin-top:4px">' +
            '<div class="panel" id="fvey-alliances-panel">' +
                '<div class="panel-head"><h3>ALLIANCE TRACKER</h3><span class="ph-meta">' + liveIndicator('') + '</span></div>' +
                '<div class="panel-body" id="fvey-alliances-body"><div class="loading">LOADING ALLIANCE DATA</div></div>' +
            '</div>' +
            '<div class="panel" id="fvey-treaties-panel">' +
                '<div class="panel-head"><h3>TREATY / NORMS STATUS</h3><span class="ph-meta">' + liveIndicator('') + '</span></div>' +
                '<div class="panel-body" id="fvey-treaties-body"><div class="loading">LOADING TREATY DATA</div></div>' +
            '</div>' +
        '</div>' +
        '<div id="fvey-mission-assurance-container"></div>' +
        '</div>';

    // Fetch alliance, treaty, and mission-assurance data
    Promise.all([
        api('/api/analysis/alliances'),
        api('/api/analysis/treaties'),
        api('/api/analysis/mission-assurance'),
    ]).then(function(fveyResults) {
        var alliances = fveyResults[0];
        var treaties = fveyResults[1];
        var missionAssurance = fveyResults[2];

        // ALLIANCES
        var alliBody = document.getElementById('fvey-alliances-body');
        if (alliBody) {
            if (!alliances) {
                alliBody.innerHTML = '<div class="empty-state">ALLIANCE DATA UNAVAILABLE</div>';
            } else {
                var aHtml = '';
                var alliArr = Array.isArray(alliances) ? alliances : (alliances.alliances || alliances.frameworks || [alliances]);
                if (!Array.isArray(alliArr)) alliArr = [alliArr];
                alliArr.forEach(function(a) {
                    if (typeof a === 'string') {
                        aHtml += '<div style="padding:4px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:10px;color:var(--text)">' + a + '</div>';
                        return;
                    }
                    var aName = a.name || a.alliance || a.framework || 'Alliance';
                    var aMembers = a.members || a.nations || [];
                    var aStatus = a.status || a.operational_status || '';
                    var aFocus = a.focus_areas || a.capabilities || [];
                    aHtml += '<div class="threat-card severity-low" style="border-left-color:var(--cyan)">' +
                        '<div class="tc-header"><span class="badge badge-fvey">' + aName.toUpperCase().substring(0, 12) + '</span> <span class="tc-title">' + aName + '</span></div>' +
                        '<div class="tc-body">' + (a.description || a.summary || '') + '</div>' +
                        '<div class="tc-meta">' +
                            (Array.isArray(aMembers) && aMembers.length ? 'MEMBERS: ' + aMembers.join(', ') + ' // ' : '') +
                            (aStatus ? 'STATUS: <span style="color:var(--green)">' + aStatus.toUpperCase() + '</span>' : '') +
                        '</div>' +
                        (Array.isArray(aFocus) && aFocus.length ? '<div class="tc-source">FOCUS: ' + aFocus.join(', ') + '</div>' : '') +
                    '</div>';
                });
                alliBody.innerHTML = aHtml || '<div class="empty-state">NO ALLIANCE DATA</div>';
            }
        }

        // TREATIES
        var treatBody = document.getElementById('fvey-treaties-body');
        if (treatBody) {
            if (!treaties) {
                treatBody.innerHTML = '<div class="empty-state">TREATY DATA UNAVAILABLE</div>';
            } else {
                var tHtml = '';
                var treatArr = Array.isArray(treaties) ? treaties : (treaties.treaties || treaties.norms || [treaties]);
                if (!Array.isArray(treatArr)) treatArr = [treatArr];
                treatArr.forEach(function(t) {
                    if (typeof t === 'string') {
                        tHtml += '<div style="padding:4px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:10px;color:var(--text)">' + t + '</div>';
                        return;
                    }
                    var tName = t.name || t.treaty || 'Treaty';
                    var tStatus = (t.status || t.compliance_status || '').toLowerCase();
                    var tColor = tStatus === 'active' || tStatus === 'in force' ? 'var(--green)' : tStatus === 'violated' || tStatus === 'withdrawn' ? 'var(--red)' : 'var(--amber)';
                    var tSeverity = tStatus === 'violated' || tStatus === 'withdrawn' ? 'critical' : tStatus === 'contested' || tStatus === 'under review' ? 'high' : 'low';
                    tHtml += '<div class="threat-card severity-' + tSeverity + '">' +
                        '<div class="tc-header">' + badge(tSeverity) + ' <span class="tc-title">' + tName + '</span></div>' +
                        '<div class="tc-body">' + (t.description || t.summary || '') + '</div>' +
                        '<div class="tc-meta">' +
                            'STATUS: <span style="color:' + tColor + '">' + (t.status || 'UNKNOWN').toUpperCase() + '</span>' +
                            (t.year ? ' // YEAR: ' + t.year : '') +
                            (t.signatories ? ' // SIGNATORIES: ' + (Array.isArray(t.signatories) ? t.signatories.join(', ') : t.signatories) : '') +
                        '</div>' +
                    '</div>';
                });
                treatBody.innerHTML = tHtml || '<div class="empty-state">NO TREATY DATA</div>';
            }
        }

        // MISSION ASSURANCE (optional - skip gracefully if not available)
        var maContainer = document.getElementById('fvey-mission-assurance-container');
        if (maContainer && missionAssurance) {
            var maHtml = '<div class="panel" style="margin-top:4px"><div class="panel-head"><h3>MISSION ASSURANCE SCORES</h3><span class="ph-meta">' + liveIndicator('') + '</span></div><div class="panel-body">';
            if (typeof missionAssurance === 'string') {
                maHtml += '<div class="intel-summary">' + missionAssurance + '</div>';
            } else if (Array.isArray(missionAssurance)) {
                missionAssurance.forEach(function(ma) {
                    var maScore = ma.score || ma.assurance_level || 0;
                    maHtml += buildResilienceBar(ma.domain || ma.name || 'DOMAIN', typeof maScore === 'number' ? maScore : 50, badge(ma.risk || 'medium'));
                });
            } else {
                Object.entries(missionAssurance).forEach(function(entry) {
                    if (typeof entry[1] === 'number') {
                        maHtml += buildResilienceBar(entry[0].replace(/_/g, ' ').toUpperCase(), entry[1], '');
                    } else if (typeof entry[1] === 'string') {
                        maHtml += '<div class="intel-field"><span class="intel-label">' + entry[0].replace(/_/g, ' ').toUpperCase() + '</span>' + entry[1] + '</div>';
                    }
                });
            }
            maHtml += '</div></div>';
            maContainer.innerHTML = maHtml;
        }
    });
};


/* ================================================================
   PAGE 8: STRATEGIC ANALYSIS
   Threat overview, collapsible scenarios, hotspot map, research feed
   ================================================================ */
Pages.strategy = async function (el) {
    el.innerHTML = '<div class="loading">GENERATING STRATEGIC ANALYSIS</div>';

    var results = await Promise.all([
        api('/api/threat/overview'),
        api('/api/threat/scenarios'),
        api('/api/threat/vulnerabilities'),
        api('/api/threat/recommendations'),
        api('/api/intel/hotspots'),
        api('/api/intel/research'),
        api('/api/intel/brief'),
        api('/api/intel/arxiv'),
    ]);

    var ov = results[0] || {};
    var scenarios = results[1] || [];
    var vulns = results[2] || [];
    var recs = results[3] || [];
    var hotspots = results[4];
    var research = results[5] || [];
    var brief = results[6];
    var arxiv = results[7] || [];

    var level = (ov.overall_threat_level || ov.threat_level || 'HIGH').toUpperCase();
    var critVulns = vulns.filter(function(v) { return v.severity === 'critical'; }).length;
    var highVulns = vulns.filter(function(v) { return v.severity === 'high'; }).length;
    var totalScenarios = scenarios.length;
    var hs = (hotspots && hotspots.hotspots) || [];
    var mapH = hs.length > 0 ? Math.max(350, window.innerHeight * 0.35) : 0;

    // Build scenarios
    var scenariosHtml = '';
    scenarios.forEach(function(s, idx) {
        var phasesHtml = '';
        if (s.phases && s.phases.length) {
            phasesHtml = '<div style="margin-bottom:8px"><span class="intel-label" style="color:var(--red)">ESCALATION PHASES</span><ol class="phase-list" style="margin-top:4px">';
            s.phases.forEach(function(p) {
                phasesHtml += '<li style="margin-bottom:4px;line-height:1.4">' + p + '</li>';
            });
            phasesHtml += '</ol></div>';
        }
        scenariosHtml += '<div class="scenario-section' + (idx === 0 ? ' open' : '') + '" id="scenario-' + idx + '">' +
            '<div class="scenario-header" onclick="document.getElementById(\'scenario-' + idx + '\').classList.toggle(\'open\')">' +
                '<span class="chevron">&#9654;</span> ' +
                badge(s.severity || s.probability || 'high') + ' ' +
                '<span style="color:var(--white);font-size:11px;flex:1">' + (s.title || s.name) + '</span>' +
                (s.probability ? '<span style="font-size:8px;color:var(--text-dim);letter-spacing:1px">P: ' + s.probability.toUpperCase() + '</span>' : '') +
                (s.timeframe ? ' <span style="font-size:8px;color:var(--text-muted)">' + s.timeframe + '</span>' : '') +
            '</div>' +
            '<div class="scenario-body"><div class="scenario-body-inner">' +
                '<div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:8px">' + (s.description || '') + '</div>' +
                phasesHtml +
                (s.fvey_response ? '<div><span class="intel-label" style="color:var(--green)">RECOMMENDED FVEY RESPONSE</span><div style="font-size:10px;color:var(--text);line-height:1.5;margin-top:3px">' + s.fvey_response + '</div></div>' : '') +
            '</div></div>' +
        '</div>';
    });

    // Build hotspot cards
    var hotspotCardsHtml = '';
    hs.slice(0, 6).forEach(function(h) {
        var passesHtml = '';
        if (h.passes_by_country) {
            Object.keys(h.passes_by_country).forEach(function(c) {
                var n = h.passes_by_country[c];
                passesHtml += '<div class="fd-row">' +
                    '<span class="fd-nation" style="color:' + countryColor(c) + ';font-size:9px">' + c + '</span>' +
                    '<div class="fd-bar-wrap"><div class="fd-bar" style="width:' + Math.min(n / h.total_adversary_passes * 100, 100) + '%;background:' + countryColor(c) + '"></div></div>' +
                    '<span class="fd-count" style="font-size:10px">' + n + '</span>' +
                '</div>';
            });
        }
        var catHtml = '';
        if (h.passes_by_category) {
            var catParts = [];
            Object.keys(h.passes_by_category).forEach(function(c) {
                catParts.push(c.replace(/_/g, ' ') + ':' + h.passes_by_category[c]);
            });
            catHtml = '<div style="margin-top:4px;font-size:8px;color:var(--text-muted)">' + catParts.join(' | ') + '</div>';
        }
        var topThreatsHtml = '';
        if (h.top_threats && h.top_threats.length) {
            topThreatsHtml = '<div style="margin-top:4px;border-top:1px solid var(--border);padding-top:3px">';
            h.top_threats.slice(0, 3).forEach(function(t) {
                topThreatsHtml += '<div style="font-size:8px;color:var(--text-dim)">' + countryBadge(t.country) + ' ' + t.name + ' <span style="color:var(--text-muted)">' + Math.round(t.alt_km || 0) + 'KM</span></div>';
            });
            topThreatsHtml += '</div>';
        }
        hotspotCardsHtml += '<div class="panel">' +
            '<div class="panel-head"><h3>' + h.name + '</h3><span class="ph-meta" style="color:var(--red)">' + h.total_adversary_passes + ' PASSES</span></div>' +
            '<div class="panel-body">' + passesHtml + catHtml + topThreatsHtml + '</div></div>';
    });

    // Build research feed
    var researchHtml = '';
    if (research.length) {
        research.slice(0, 12).forEach(function(r) {
            researchHtml += '<a href="' + (r.url || '#') + '" target="_blank" rel="noopener" class="news-line">' +
                '<span class="nl-title">' + r.title + '</span>' +
                '<span class="nl-meta">' + (r.source || 'OSINT') + (r.relevance_tag ? ' // ' + r.relevance_tag : '') + ' // ' + (r.published_at ? timeAgo(r.published_at) : '') + '</span>' +
                (r.summary ? '<div style="font-size:8px;color:var(--text-muted);line-height:1.3;margin-top:1px">' + r.summary.substring(0, 120) + (r.summary.length > 120 ? '...' : '') + '</div>' : '') +
                '</a>';
        });
    } else {
        researchHtml = '<div class="empty-state">NO RESEARCH DATA</div>';
    }

    // Build arxiv feed
    var arxivHtml = '';
    if (arxiv.length) {
        arxiv.slice(0, 12).forEach(function(a) {
            arxivHtml += '<a href="' + (a.url || '#') + '" target="_blank" rel="noopener" class="news-line">' +
                '<span class="nl-title">' + a.title + '</span>' +
                '<span class="nl-meta">' + (a.source || 'arXiv') + (a.relevance_tag ? ' // ' + a.relevance_tag : '') + ' // ' + (a.published_at ? timeAgo(a.published_at) : '') + '</span>' +
                (a.summary ? '<div style="font-size:8px;color:var(--text-muted);line-height:1.3;margin-top:1px">' + a.summary.substring(0, 120) + (a.summary.length > 120 ? '...' : '') + '</div>' : '') +
                '</a>';
        });
    } else {
        arxivHtml = '<div class="empty-state">NO ARXIV DATA</div>';
    }

    var briefText = '';
    if (brief) {
        briefText = typeof brief === 'string' ? brief.substring(0, 400) : (brief.summary || brief.assessment || JSON.stringify(brief)).substring(0, 400);
    }

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="strategy-banner">' +
            '<div class="strategy-title">FIVE EYES SPACE DOMAIN THREAT ASSESSMENT</div>' +
            '<div class="strategy-subtitle">UNCLASSIFIED // OSINT-DERIVED // ' + new Date().toISOString().substring(0, 10) + ' // ' + zulu() + '</div>' +
            '<div class="strategy-threat-display">' +
                '<div class="strategy-threat-level ' + level.toLowerCase() + '">' + level + '</div>' +
            '</div>' +
            '<div style="font-size:9px;color:var(--text-dim);letter-spacing:1px;margin-top:4px">' + critVulns + ' CRITICAL VULNERABILITIES | ' + highVulns + ' HIGH VULNERABILITIES | ' + totalScenarios + ' ESCALATION SCENARIOS MODELLED</div>' +
        '</div>' +
        '<div class="panel mb-4">' +
            '<div class="panel-head"><h3>EXECUTIVE SUMMARY</h3><span class="ph-meta">ASSESSMENT PERIOD: CURRENT</span></div>' +
            '<div class="panel-body">' +
                '<div style="font-size:10px;color:var(--text);line-height:1.7;margin-bottom:8px">' + (ov.summary || '') + '</div>' +
                (brief ? '<div class="intel-summary" style="margin-top:6px"><strong>DAILY BRIEF:</strong> ' + briefText + '</div>' : '') +
            '</div>' +
        '</div>' +
        (ov.key_concerns && ov.key_concerns.length ? '<div class="panel mb-4">' +
            '<div class="panel-head"><h3>KEY CONCERNS</h3><span class="ph-meta"><span class="badge badge-critical">' + ov.key_concerns.length + ' IDENTIFIED</span></span></div>' +
            '<div class="panel-body"><div class="asat-grid">' + (function() {
                var kc = '';
                ov.key_concerns.forEach(function(c) {
                    kc += '<div class="threat-card severity-' + (c.severity || 'high') + '">' +
                        '<div class="tc-header">' + severityDots(c.severity || 'high') + ' ' + badge(c.severity || 'high') + ' <span class="tc-title">' + c.title + '</span></div>' +
                        '<div class="tc-body">' + (c.detail || c.description || '') + '</div>' +
                        (c.evidence ? '<div class="tc-source">EVIDENCE: ' + c.evidence + '</div>' : '') +
                    '</div>';
                });
                return kc;
            })() + '</div></div></div>' : '') +
        '<div class="panel mb-4">' +
            '<div class="panel-head"><h3>CONFLICT ESCALATION SCENARIOS</h3><span class="ph-meta"><span class="badge badge-critical">WARGAME</span> ' + totalScenarios + ' SCENARIOS</span></div>' +
            '<div class="panel-body" style="padding:4px">' + scenariosHtml + '</div>' +
        '</div>' +
        (hs.length ? '<div class="panel mb-4">' +
            '<div class="panel-head"><h3>HOTSPOT ANALYSIS</h3><span class="ph-meta">' + hs.length + ' ZONES TRACKED</span></div>' +
            '<div class="panel-body" style="padding:0"><div id="strategy-hotspot-map" class="map-container" style="height:' + mapH + 'px;min-height:' + mapH + 'px"></div></div>' +
        '</div><div class="grid-3 mb-4">' + hotspotCardsHtml + '</div>' : '') +
        '<!-- AI DEDUCTIONS -->' +
        '<div class="panel mb-4" id="strategy-deductions-panel">' +
            '<div class="panel-head"><h3>AI DEDUCTIONS ENGINE</h3><span class="ph-meta">' + liveIndicator('120S') + '</span></div>' +
            '<div class="panel-body" id="strategy-deductions-body"><div class="loading">LOADING DEDUCTIONS</div></div>' +
        '</div>' +
        '<!-- THREAT NARRATIVE -->' +
        '<div class="panel mb-4" id="strategy-narrative-panel">' +
            '<div class="panel-head"><h3>THREAT NARRATIVE</h3><span class="ph-meta"><span class="badge badge-critical">AI-GENERATED</span></span></div>' +
            '<div class="panel-body" id="strategy-narrative-body"><div class="loading">LOADING NARRATIVE</div></div>' +
        '</div>' +
        '<!-- DAILY INTELLIGENCE BRIEF -->' +
        '<div class="panel mb-4" id="strategy-dailybrief-panel">' +
            '<div class="panel-head"><h3>DAILY INTELLIGENCE BRIEF</h3><span class="ph-meta">' + liveIndicator('300S') + '</span></div>' +
            '<div class="panel-body" id="strategy-dailybrief-body"><div class="loading">LOADING DAILY SUMMARY</div></div>' +
        '</div>' +
        '<div class="grid-2">' +
            '<div class="panel"><div class="panel-head"><h3>INTELLIGENCE RESEARCH FEED</h3><span class="ph-meta">' + research.length + ' ITEMS ' + liveIndicator('300S') + '</span></div>' +
                '<div class="panel-body" style="max-height:400px" id="strategy-research-body">' + researchHtml + '</div></div>' +
            '<div class="panel"><div class="panel-head"><h3>ACADEMIC / ARXIV PAPERS</h3><span class="ph-meta">' + arxiv.length + ' PAPERS ' + liveIndicator('300S') + '</span></div>' +
                '<div class="panel-body" style="max-height:400px" id="strategy-arxiv-body">' + arxivHtml + '</div></div>' +
        '</div>' +
        '<div style="text-align:center;padding:4px;font-size:7px;letter-spacing:1.5px;color:var(--text-muted)"><span class="live-indicator"><span class="live-dot"></span> LIVE</span> STRATEGY FEEDS AUTO-REFRESH 300S | LAST: <span id="strategy-live-ts">' + zulu() + '</span></div>' +
        '</div>';

    // Hotspot map
    if (hs.length) {
        setTimeout(function() {
            var mapEl = document.getElementById('strategy-hotspot-map');
            if (!mapEl) return;
            mapEl.style.height = mapH + 'px';
            var hmap = makeMap('strategy-hotspot-map', [20, 80], 3);
            if (!hmap) return;
            storeMap(hmap);

            hs.forEach(function(h) {
                if (!h.lat || !h.lng) return;
                var radius = Math.min(30, Math.max(10, h.total_adversary_passes / 3));
                L.circle([h.lat, h.lng], {
                    radius: radius * 10000, fillColor: '#FF2020', fillOpacity: 0.15,
                    color: '#FF2020', weight: 1, opacity: 0.4,
                }).addTo(hmap);

                L.circleMarker([h.lat, h.lng], {
                    radius: 6, fillColor: '#FF2020', fillOpacity: 0.8,
                    color: '#fff', weight: 1, opacity: 0.5,
                }).bindPopup(satPopup(h.name, '#FF2020', [
                    'ADVERSARY PASSES: <span style="color:var(--red)">' + h.total_adversary_passes + '</span>',
                    h.passes_by_country ? Object.entries(h.passes_by_country).map(function(e) { return e[0] + ': ' + e[1]; }).join(' | ') : '',
                ]), { className: 'sat-popup', closeButton: false }).addTo(hmap);

                (h.top_threats || []).slice(0, 5).forEach(function(t) {
                    if (!t.lat || !t.lng) return;
                    L.circleMarker([t.lat, t.lng], {
                        radius: 3, fillColor: countryColor(t.country), fillOpacity: 0.7,
                        color: countryColor(t.country), weight: 0.5,
                    }).addTo(hmap);
                });
            });
        }, 150);
    }

    // --- STRATEGY: AI Deductions, Narrative, Daily Brief ---
    function renderStrategyDeductions(data) {
        var dedBody = document.getElementById('strategy-deductions-body');
        if (!dedBody) return;
        if (!data || !Array.isArray(data) || !data.length) {
            dedBody.innerHTML = '<div class="empty-state">DEDUCTIONS DATA UNAVAILABLE</div>';
            return;
        }
        var dHtml = '<div class="asat-grid">';
        data.forEach(function(d, idx) {
            var cat = (d.category || 'general').toLowerCase();
            var confLevel = (d.confidence || d.priority || 'medium').toLowerCase();
            var badgeCls = confLevel === 'critical' || confLevel === 'high' ? 'critical' : confLevel === 'medium' ? 'high' : 'medium';
            var catColor = cat === 'threat' ? 'var(--red)' : cat === 'capability' ? 'var(--cis)' : cat === 'intent' ? 'var(--nkor)' : cat === 'vulnerability' ? 'var(--amber)' : 'var(--cyan)';
            dHtml += '<div class="threat-card severity-' + badgeCls + '" style="border-left-color:' + catColor + '">' +
                '<div class="tc-header">' +
                    '<span class="badge" style="background:rgba(0,212,255,0.1);color:' + catColor + ';border:1px solid ' + catColor + '">' + cat.toUpperCase() + '</span> ' +
                    badge(confLevel) + ' ' +
                    '<span class="tc-title">' + (d.title || d.deduction || 'Deduction #' + (idx + 1)) + '</span>' +
                '</div>' +
                '<div class="tc-body">' + (d.reasoning || d.detail || d.description || '') + '</div>' +
                '<div class="tc-meta">' +
                    (d.sources ? 'SOURCES: ' + (Array.isArray(d.sources) ? d.sources.join(', ') : d.sources) : '') +
                    (d.timestamp ? ' // ' + timeAgo(d.timestamp) : '') +
                '</div>' +
            '</div>';
        });
        dHtml += '</div>';
        dedBody.innerHTML = dHtml;
    }

    function renderStrategyNarrative(data) {
        var narBody = document.getElementById('strategy-narrative-body');
        if (!narBody) return;
        if (!data) {
            narBody.innerHTML = '<div class="empty-state">NARRATIVE DATA UNAVAILABLE</div>';
            return;
        }
        var narText = '';
        if (typeof data === 'string') {
            narText = data;
        } else if (data.narrative) {
            narText = data.narrative;
        } else if (data.document) {
            narText = data.document;
        } else if (data.text) {
            narText = data.text;
        } else {
            narText = JSON.stringify(data, null, 2);
        }
        narBody.innerHTML = '<div class="intel-summary" style="white-space:pre-line;line-height:1.7;max-height:500px;overflow-y:auto">' + narText + '</div>';
    }

    function renderDailyBrief(data) {
        var briefBody = document.getElementById('strategy-dailybrief-body');
        if (!briefBody) return;
        if (!data) {
            briefBody.innerHTML = '<div class="empty-state">DAILY BRIEF UNAVAILABLE</div>';
            return;
        }
        var bHtml = '';
        if (typeof data === 'string') {
            bHtml = '<div class="intel-summary" style="white-space:pre-line;line-height:1.7">' + data + '</div>';
        } else {
            if (data.title) bHtml += '<div style="font-size:12px;color:var(--amber);letter-spacing:1px;margin-bottom:6px">' + data.title + '</div>';
            if (data.date) bHtml += '<div style="font-size:8px;color:var(--text-muted);letter-spacing:1px;margin-bottom:6px">' + data.date + '</div>';
            if (data.summary || data.executive_summary) bHtml += '<div class="intel-summary" style="margin-bottom:8px">' + (data.summary || data.executive_summary) + '</div>';
            if (data.key_developments && Array.isArray(data.key_developments)) {
                bHtml += '<div style="margin-top:6px"><span class="intel-label">KEY DEVELOPMENTS</span>';
                data.key_developments.forEach(function(dev) {
                    var devText = typeof dev === 'string' ? dev : (dev.title || dev.description || JSON.stringify(dev));
                    bHtml += '<div style="padding:3px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:10px;color:var(--text);line-height:1.5">' + devText + '</div>';
                });
                bHtml += '</div>';
            }
            if (data.threat_assessment) bHtml += '<div class="intel-field" style="margin-top:8px"><span class="intel-label">THREAT ASSESSMENT</span><div style="font-size:10px;line-height:1.5;color:var(--text)">' + data.threat_assessment + '</div></div>';
            if (data.recommendations && Array.isArray(data.recommendations)) {
                bHtml += '<div style="margin-top:8px"><span class="intel-label" style="color:var(--green)">RECOMMENDATIONS</span>';
                data.recommendations.forEach(function(rec) {
                    var recText = typeof rec === 'string' ? rec : (rec.title || rec.description || JSON.stringify(rec));
                    bHtml += '<div style="padding:3px 0;border-bottom:1px solid rgba(32,255,96,0.06);font-size:10px;color:var(--text);line-height:1.4">' + recText + '</div>';
                });
                bHtml += '</div>';
            }
            if (!bHtml) bHtml = '<div class="intel-summary" style="white-space:pre-wrap">' + JSON.stringify(data, null, 2) + '</div>';
        }
        briefBody.innerHTML = bHtml;
    }

    // Fetch deductions, narrative, daily summary in parallel
    Promise.all([
        api('/api/deductions'),
        api('/api/deductions/narrative'),
        api('/api/analysis/daily-summary'),
    ]).then(function(stratResults) {
        renderStrategyDeductions(stratResults[0]);
        renderStrategyNarrative(stratResults[1]);
        renderDailyBrief(stratResults[2]);
    });

    // Auto-refresh deductions every 120s
    registerInterval(async function() {
        var freshDedResults = await Promise.all([
            api('/api/deductions'),
            api('/api/deductions/narrative'),
        ]);
        renderStrategyDeductions(freshDedResults[0]);
        renderStrategyNarrative(freshDedResults[1]);
    }, 120000);

    // --- AUTO-REFRESH: Research & Arxiv feeds every 300s ---
    registerInterval(async function() {
        var freshFeeds = await Promise.all([
            api('/api/intel/research'),
            api('/api/intel/arxiv'),
        ]);

        var freshResearch = freshFeeds[0] || [];
        var freshArxiv = freshFeeds[1] || [];

        // Update research feed
        var resBodyEl = document.getElementById('strategy-research-body');
        if (resBodyEl && freshResearch.length) {
            var rHtml = '';
            freshResearch.slice(0, 12).forEach(function(r) {
                rHtml += '<a href="' + (r.url || '#') + '" target="_blank" rel="noopener" class="news-line">' +
                    '<span class="nl-title">' + r.title + '</span>' +
                    '<span class="nl-meta">' + (r.source || 'OSINT') + (r.relevance_tag ? ' // ' + r.relevance_tag : '') + ' // ' + (r.published_at ? timeAgo(r.published_at) : '') + '</span>' +
                    (r.summary ? '<div style="font-size:8px;color:var(--text-muted);line-height:1.3;margin-top:1px">' + r.summary.substring(0, 120) + (r.summary.length > 120 ? '...' : '') + '</div>' : '') +
                    '</a>';
            });
            resBodyEl.innerHTML = rHtml || '<div class="empty-state">NO RESEARCH DATA</div>';
        }

        // Update arxiv feed
        var arxBodyEl = document.getElementById('strategy-arxiv-body');
        if (arxBodyEl && freshArxiv.length) {
            var aHtml = '';
            freshArxiv.slice(0, 12).forEach(function(a) {
                aHtml += '<a href="' + (a.url || '#') + '" target="_blank" rel="noopener" class="news-line">' +
                    '<span class="nl-title">' + a.title + '</span>' +
                    '<span class="nl-meta">' + (a.source || 'arXiv') + (a.relevance_tag ? ' // ' + a.relevance_tag : '') + ' // ' + (a.published_at ? timeAgo(a.published_at) : '') + '</span>' +
                    (a.summary ? '<div style="font-size:8px;color:var(--text-muted);line-height:1.3;margin-top:1px">' + a.summary.substring(0, 120) + (a.summary.length > 120 ? '...' : '') + '</div>' : '') +
                    '</a>';
            });
            arxBodyEl.innerHTML = aHtml || '<div class="empty-state">NO ARXIV DATA</div>';
        }

        var stratTsEl = document.getElementById('strategy-live-ts');
        if (stratTsEl) stratTsEl.textContent = zulu();
    }, 300000);
};


/* ================================================================
   PAGE 9: OVERMATCH
   Crown jewel -- domain overmatch scores for 6 contested zones
   ================================================================ */
Pages.overmatch = async function (el) {
    el.innerHTML = '<div class="loading">CALCULATING OVERMATCH SCORES</div>';

    var overmatch = null;
    var summary = null;
    var hotspots = null;

    try {
        var results = await Promise.all([
            api('/api/overmatch'),
            api('/api/overmatch/summary'),
            api('/api/intel/hotspots'),
        ]);
        overmatch = results[0];
        summary = results[1];
        hotspots = results[2];
    } catch (e) {
        // Endpoints may not exist yet
    }

    var zones = (overmatch && overmatch.zones) ? overmatch.zones : null;
    var hs = (hotspots && hotspots.hotspots) || [];
    var domains = ['ISR', 'COMMS', 'PNT', 'SDA', 'ASAT', 'EW'];
    var mapH = Math.max(380, window.innerHeight * 0.4);

    if (!zones) {
        var fallbackZonesHtml = '';
        hs.slice(0, 6).forEach(function(h) {
            fallbackZonesHtml += '<div class="overmatch-zone-card">' +
                '<div class="overmatch-zone-header">' +
                    '<span class="overmatch-zone-name">' + h.name + '</span>' +
                    '<span style="font-size:9px;color:var(--red)">' + h.total_adversary_passes + ' PASSES</span>' +
                '</div>' +
                '<div class="overmatch-zone-body">' +
                    '<div style="text-align:center;padding:10px 0;font-size:10px;color:var(--text-muted);letter-spacing:1px">OVERMATCH DATA PENDING</div>' +
                    domains.map(function(d) { return buildOvermatchBar(d, 0); }).join('') +
                '</div></div>';
        });

        el.innerHTML = '<div class="page-wrap">' +
            '<div class="strategy-banner" style="border-bottom-color:var(--amber)">' +
                '<div class="strategy-title">FVEY DOMAIN OVERMATCH ASSESSMENT</div>' +
                '<div class="strategy-subtitle">UNCLASSIFIED // ' + new Date().toISOString().substring(0, 10) + ' // ' + zulu() + '</div>' +
                '<div class="strategy-threat-display"><div class="strategy-threat-level elevated" style="animation:blink-text 1.5s step-end infinite">CALCULATING</div></div>' +
                '<div style="font-size:9px;color:var(--text-dim);letter-spacing:1px;margin-top:4px">OVERMATCH ENGINE INITIALIZING -- COLLECTING DOMAIN SCORES</div>' +
            '</div>' +
            (hs.length ? '<div class="section-head">CONTESTED ZONES IDENTIFIED</div><div class="grid-3 mb-4">' + fallbackZonesHtml + '</div>' : '') +
            '<div class="panel"><div class="panel-head"><h3>DOMAIN ANALYSIS PENDING</h3><span class="ph-meta">' + livePulse('CALCULATING', 'amber') + '</span></div>' +
                '<div class="panel-body" style="text-align:center;padding:30px">' +
                    '<div style="font-size:11px;color:var(--amber);letter-spacing:2px;margin-bottom:8px">OVERMATCH ENGINE LOADING</div>' +
                    '<div style="font-size:9px;color:var(--text-dim)">The overmatch calculation engine processes ISR, COMMS, PNT, SDA, ASAT, and EW domain data across all 6 contested zones. Refresh when backend is available.</div>' +
            '</div></div></div>';
        return;
    }

    // Full overmatch display
    var globalScore = (summary && summary.global_overmatch) || (summary && summary.overall_score) || Math.round(zones.reduce(function(a, z) { return a + (z.overmatch_score || 0); }, 0) / zones.length);
    var globalVerdict = overmatchVerdict(globalScore);

    // Build zone cards
    var zoneCardsHtml = '';
    zones.forEach(function(z) {
        var zScore = z.overmatch_score || 0;
        var zVerdict = overmatchVerdict(zScore);
        var dm = z.domains || {};
        var domainBarsHtml = '';
        var domainMiniHtml = '';
        domains.forEach(function(d) {
            var raw = dm[d];
            var dScore = (typeof raw === 'object' && raw !== null) ? (raw.score || 0) : (raw || 0);
            domainBarsHtml += buildOvermatchBar(d, dScore);
            domainMiniHtml += '<div class="domain-score-card">' +
                '<div class="domain-score-label">' + d + '</div>' +
                '<div class="domain-score-val" style="color:' + overmatchColor(dScore) + '">' + (dScore > 0 ? '+' : '') + dScore + '</div>' +
                '</div>';
        });

        zoneCardsHtml += '<div class="overmatch-zone-card">' +
            '<div class="overmatch-zone-header">' +
                '<span class="overmatch-zone-name">' + z.zone + '</span>' +
                '<span class="overmatch-zone-score" style="color:' + overmatchColor(zScore) + '">' + (zScore > 0 ? '+' : '') + zScore + '</span>' +
            '</div>' +
            '<div class="overmatch-zone-body">' +
                '<div style="margin-bottom:6px"><span class="overmatch-zone-verdict ' + zVerdict.cls + '">' + zVerdict.text + '</span>' +
                (z.overall_overmatch ? '<span style="font-size:8px;color:var(--text-muted);margin-left:6px">' + z.overall_overmatch + '</span>' : '') +
                '</div>' +
                domainBarsHtml +
                '<div class="domain-scores-grid">' + domainMiniHtml + '</div>' +
            '</div></div>';
    });

    // Build recommendations
    var recsHtml = '';
    if (summary && summary.recommendations && summary.recommendations.length) {
        recsHtml = '<div class="panel mb-4"><div class="panel-head"><h3>OVERMATCH RECOMMENDATIONS</h3><span class="ph-meta">' + summary.recommendations.length + ' ITEMS</span></div><div class="panel-body">';
        summary.recommendations.forEach(function(r, i) {
            var title = typeof r === 'string' ? r : (r.title || r.description || '');
            var detail = typeof r === 'object' && r.detail ? r.detail : '';
            recsHtml += '<div class="threat-card severity-high" style="border-left-color:var(--cyan)">' +
                '<div class="tc-header"><span style="color:var(--text-dim);font-size:9px">#' + (i + 1) + '</span> <span class="tc-title">' + title + '</span></div>' +
                (detail ? '<div class="tc-body">' + detail + '</div>' : '') +
                '</div>';
        });
        recsHtml += '</div></div>';
    }

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="strategy-banner" style="border-bottom-color:' + overmatchColor(globalScore) + '">' +
            '<div class="strategy-title">FVEY DOMAIN OVERMATCH ASSESSMENT</div>' +
            '<div class="strategy-subtitle">UNCLASSIFIED // ' + new Date().toISOString().substring(0, 10) + ' // ' + zulu() + ' // ' + zones.length + ' CONTESTED ZONES</div>' +
            '<div class="strategy-threat-display">' +
                '<div class="strategy-threat-level" style="color:' + overmatchColor(globalScore) + ';border-color:' + overmatchColor(globalScore) + ';background:rgba(0,0,0,0.3)">' + (globalScore > 0 ? '+' : '') + Math.round(globalScore) + '</div>' +
            '</div>' +
            '<div style="margin-top:6px"><span class="overmatch-zone-verdict ' + globalVerdict.cls + '">' + globalVerdict.text + '</span></div>' +
            '<div style="font-size:8px;color:var(--text-dim);letter-spacing:1px;margin-top:6px">SCALE: -100 (ADVERSARY DOMINANT) ... 0 (CONTESTED) ... +100 (FVEY DOMINANT)</div>' +
        '</div>' +
        '<div class="overmatch-global-bar">' +
            '<div class="overmatch-global-score" style="color:' + overmatchColor(globalScore) + ';text-shadow:0 0 15px ' + overmatchColor(globalScore) + '">' + (globalScore > 0 ? '+' : '') + Math.round(globalScore) + '</div>' +
            '<div class="overmatch-global-detail">' +
                '<div class="overmatch-global-label">GLOBAL OVERMATCH SCORE</div>' +
                '<div class="overmatch-global-verdict" style="color:' + overmatchColor(globalScore) + '">' + globalVerdict.text + '</div>' +
                (summary && summary.key_finding ? '<div style="font-size:9px;color:var(--text);margin-top:4px;line-height:1.4">' + summary.key_finding + '</div>' : '') +
            '</div>' +
            '<div>' + livePulse('LIVE', '') + '</div>' +
        '</div>' +
        '<div class="panel mb-2"><div class="panel-head"><h3>CONTESTED ZONES // OVERMATCH MAP</h3><span class="ph-meta">' + zones.length + ' ZONES | ' + zulu() + '</span></div>' +
            '<div class="panel-body" style="padding:0"><div id="overmatch-map" class="map-container" style="height:' + mapH + 'px;min-height:' + mapH + 'px"></div></div></div>' +
        '<div class="section-head">ZONE OVERMATCH BREAKDOWN // 6 DOMAINS <span class="live-indicator" style="float:right"><span class="live-dot"></span> LIVE 120S</span></div>' +
        '<div class="grid-3 mb-4" id="overmatch-zone-cards">' + zoneCardsHtml + '</div>' +
        recsHtml +
        '<div style="text-align:center;padding:4px;font-size:7px;letter-spacing:1.5px;color:var(--text-muted)"><span class="live-indicator"><span class="live-dot"></span> LIVE</span> OVERMATCH SCORES AUTO-REFRESH 120S | LAST: <span id="overmatch-live-ts">' + zulu() + '</span></div>' +
        '</div>';

    // Overmatch map
    setTimeout(function() {
        var mapEl = document.getElementById('overmatch-map');
        if (!mapEl) return;
        mapEl.style.height = mapH + 'px';
        var omap = makeMap('overmatch-map', [25, 60], 3);
        if (!omap) return;
        storeMap(omap);

        zones.forEach(function(z) {
            var matchHS = null;
            for (var i = 0; i < hs.length; i++) {
                if (hs[i].name && z.zone) {
                    var hsFirst = hs[i].name.split(' ')[0].toLowerCase();
                    var zFirst = z.zone.split(' ')[0].toLowerCase();
                    if (hs[i].name.toLowerCase().includes(zFirst) || z.zone.toLowerCase().includes(hsFirst)) {
                        matchHS = hs[i];
                        break;
                    }
                }
            }
            var lat = matchHS ? matchHS.lat : 0;
            var lng = matchHS ? matchHS.lng : 0;
            if (!lat && !lng) return;

            var zScore = z.overmatch_score || 0;
            var col = overmatchColor(zScore);
            var colHex = zScore > 20 ? '#20FF60' : zScore > -20 ? '#FFB000' : '#FF2020';
            var radius = Math.max(15, Math.abs(zScore) / 2);

            L.circle([lat, lng], {
                radius: radius * 15000, fillColor: colHex, fillOpacity: 0.12,
                color: colHex, weight: 1.5, opacity: 0.5,
            }).addTo(omap);

            var domainLabels = Object.entries(z.domains || {}).map(function(e) {
                return e[0] + ': <span style="color:' + overmatchColor(e[1]) + '">' + (e[1] > 0 ? '+' : '') + e[1] + '</span>';
            }).join(' | ');

            L.circleMarker([lat, lng], {
                radius: 8, fillColor: colHex, fillOpacity: 0.9,
                color: '#fff', weight: 1, opacity: 0.6,
            }).bindPopup(satPopup(z.zone, colHex, [
                'OVERMATCH: <span style="color:' + col + '">' + (zScore > 0 ? '+' : '') + zScore + '</span>',
                overmatchVerdict(zScore).text,
                domainLabels,
            ]), { className: 'sat-popup', closeButton: false }).addTo(omap);
        });
    }, 200);

    // --- AUTO-REFRESH: Overmatch scores every 120s ---
    registerInterval(async function() {
        var freshOM = null;
        var freshSummary = null;
        try {
            var freshResults = await Promise.all([
                api('/api/overmatch'),
                api('/api/overmatch/summary'),
            ]);
            freshOM = freshResults[0];
            freshSummary = freshResults[1];
        } catch (e) {
            return;
        }

        if (!freshOM || !freshOM.zones) return;
        var freshZones = freshOM.zones;

        // Update global score in banner
        var freshGlobalScore = (freshSummary && freshSummary.global_overmatch) || (freshSummary && freshSummary.overall_score) || Math.round(freshZones.reduce(function(a, z) { return a + (z.overmatch_score || 0); }, 0) / freshZones.length);
        var freshGlobalVerdict = overmatchVerdict(freshGlobalScore);

        // Update global score display
        var globalScoreEl = el.querySelector('.overmatch-global-score');
        if (globalScoreEl) {
            globalScoreEl.textContent = (freshGlobalScore > 0 ? '+' : '') + Math.round(freshGlobalScore);
            globalScoreEl.style.color = overmatchColor(freshGlobalScore);
            globalScoreEl.style.textShadow = '0 0 15px ' + overmatchColor(freshGlobalScore);
        }
        var globalVerdictEl = el.querySelector('.overmatch-global-verdict');
        if (globalVerdictEl) {
            globalVerdictEl.textContent = freshGlobalVerdict.text;
            globalVerdictEl.style.color = overmatchColor(freshGlobalScore);
        }

        // Update zone cards
        var zoneContainer = document.getElementById('overmatch-zone-cards');
        if (zoneContainer) {
            var freshZoneHtml = '';
            freshZones.forEach(function(z) {
                var zScore = z.overmatch_score || 0;
                var zVerdict = overmatchVerdict(zScore);
                var dm = z.domains || {};
                var domainBarsHtml = '';
                var domainMiniHtml = '';
                domains.forEach(function(d) {
                    var rawD = dm[d];
                    var dScore = (typeof rawD === 'object' && rawD !== null) ? (rawD.score || 0) : (rawD || 0);
                    domainBarsHtml += buildOvermatchBar(d, dScore);
                    domainMiniHtml += '<div class="domain-score-card">' +
                        '<div class="domain-score-label">' + d + '</div>' +
                        '<div class="domain-score-val" style="color:' + overmatchColor(dScore) + '">' + (dScore > 0 ? '+' : '') + dScore + '</div>' +
                        '</div>';
                });
                freshZoneHtml += '<div class="overmatch-zone-card">' +
                    '<div class="overmatch-zone-header">' +
                        '<span class="overmatch-zone-name">' + z.zone + '</span>' +
                        '<span class="overmatch-zone-score" style="color:' + overmatchColor(zScore) + '">' + (zScore > 0 ? '+' : '') + zScore + '</span>' +
                    '</div>' +
                    '<div class="overmatch-zone-body">' +
                        '<div style="margin-bottom:6px"><span class="overmatch-zone-verdict ' + zVerdict.cls + '">' + zVerdict.text + '</span></div>' +
                        domainBarsHtml +
                        '<div class="domain-scores-grid">' + domainMiniHtml + '</div>' +
                    '</div></div>';
            });
            zoneContainer.innerHTML = freshZoneHtml;
        }

        var omTsEl = document.getElementById('overmatch-live-ts');
        if (omTsEl) omTsEl.textContent = zulu();
    }, 120000);
};


/* ================================================================
   PAGE 10: WARGAME
   Conflict simulation -- scenarios, run results, resilience
   ================================================================ */
Pages.wargame = async function (el) {
    el.innerHTML = '<div class="loading">LOADING WARGAME SCENARIOS</div>';

    var scenarios = null;
    var resilience = null;
    try {
        var results = await Promise.all([
            api('/api/wargame/scenarios'),
            api('/api/wargame/resilience'),
        ]);
        scenarios = results[0];
        resilience = results[1];
    } catch (e) {
        // Endpoints may not exist yet
    }

    var scenarioList = scenarios || [];
    var hasScenarios = scenarioList.length > 0;

    if (!hasScenarios) {
        var threatScenarios = await api('/api/threat/scenarios');
        var ts = threatScenarios || [];
        var tsHtml = '';
        ts.forEach(function(s, idx) {
            var phaseHtml = '';
            if (s.phases && s.phases.length) {
                phaseHtml = '<div class="phase-flow" style="margin-top:6px">';
                s.phases.forEach(function(p, pi) {
                    phaseHtml += '<div class="phase-step"><div class="phase-step-num">PHASE ' + (pi + 1) + '</div>' + p + '</div>';
                });
                phaseHtml += '</div>';
            }
            tsHtml += '<div class="wargame-card">' +
                '<div class="wargame-card-head">' + badge(s.severity || s.probability || 'high') +
                    ' <span style="color:var(--white);font-size:11px;flex:1">' + (s.title || s.name) + '</span>' +
                    (s.probability ? '<span style="font-size:8px;color:var(--text-muted)">P: ' + (s.probability || '').toUpperCase() + '</span>' : '') +
                '</div>' +
                '<div class="wargame-card-body"><div>' + (s.description || '') + '</div>' +
                    phaseHtml +
                    (s.fvey_response ? '<div style="margin-top:6px"><span class="intel-label" style="color:var(--green)">FVEY RESPONSE</span><div style="font-size:9px;color:var(--text);line-height:1.4;margin-top:2px">' + s.fvey_response + '</div></div>' : '') +
                '</div></div>';
        });

        el.innerHTML = '<div class="page-wrap">' +
            '<div class="strategy-banner" style="border-bottom-color:var(--red)">' +
                '<div class="strategy-title">CONFLICT SIMULATION ENGINE</div>' +
                '<div class="strategy-subtitle">UNCLASSIFIED // WARGAME MODULE // ' + zulu() + '</div>' +
                '<div class="strategy-threat-display"><div class="strategy-threat-level elevated" style="animation:blink-text 1.5s step-end infinite">INITIALIZING</div></div>' +
                '<div style="font-size:9px;color:var(--text-dim);letter-spacing:1px;margin-top:4px">WARGAME ENGINE LOADING -- ' + ts.length + ' THREAT SCENARIOS AVAILABLE FOR SIMULATION</div>' +
            '</div>' +
            (ts.length ? '<div class="section-head">AVAILABLE THREAT SCENARIOS</div>' + tsHtml : '<div class="empty-state">NO SCENARIOS AVAILABLE</div>') +
            (resilience ? '<div class="panel" style="margin-top:4px"><div class="panel-head"><h3>FVEY RECONSTITUTION ASSESSMENT</h3></div>' +
                '<div class="panel-body"><div style="font-size:10px;color:var(--text);line-height:1.6">' + (typeof resilience === 'string' ? resilience : JSON.stringify(resilience, null, 2)) + '</div></div></div>' : '') +
            '</div>';
        return;
    }

    // Full wargame display with runnable scenarios
    var scenListHtml = '';
    scenarioList.forEach(function(s, i) {
        scenListHtml += '<div class="wargame-card" data-idx="' + i + '" style="margin:0;border-left:0;border-right:0;' + (i > 0 ? 'border-top:0' : '') + '">' +
            '<div class="wargame-card-head" style="padding:6px 10px">' +
                badge(s.severity || 'high') +
                ' <span style="color:var(--white);font-size:10px;flex:1">' + (s.title || s.name || 'Scenario ' + (i + 1)) + '</span>' +
            '</div>' +
            '<div style="padding:4px 10px 6px;font-size:9px;color:var(--text-dim)">' + (s.description || '').substring(0, 80) + '...</div>' +
        '</div>';
    });

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="strategy-banner" style="border-bottom-color:var(--red)">' +
            '<div class="strategy-title">CONFLICT SIMULATION ENGINE</div>' +
            '<div class="strategy-subtitle">UNCLASSIFIED // WARGAME MODULE // ' + zulu() + '</div>' +
            '<div class="strategy-threat-display"><div class="strategy-threat-level critical">' + scenarioList.length + ' SCENARIOS</div></div>' +
            '<div style="font-size:9px;color:var(--text-dim);letter-spacing:1px;margin-top:4px">SELECT A SCENARIO TO EXECUTE SIMULATION</div>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:1fr 2fr;gap:2px">' +
            '<div class="panel"><div class="panel-head"><h3>SCENARIOS</h3><span class="ph-meta">' + scenarioList.length + '</span></div>' +
                '<div class="panel-body" style="max-height:calc(100vh - 260px);padding:0" id="wg-scenario-list">' + scenListHtml + '</div></div>' +
            '<div id="wg-result-area"><div class="panel" style="height:100%"><div class="panel-head"><h3>SIMULATION RESULTS</h3></div>' +
                '<div class="panel-body" style="text-align:center;padding:40px"><div style="font-size:11px;color:var(--text-dim);letter-spacing:2px">SELECT A SCENARIO TO BEGIN</div></div></div></div>' +
        '</div>' +
        (resilience ? '<div class="panel" style="margin-top:4px"><div class="panel-head"><h3>FVEY RECONSTITUTION & RESILIENCE ASSESSMENT</h3><span class="ph-meta">' + livePulse('', '') + '</span></div>' +
            '<div class="panel-body" id="wg-resilience"></div></div>' : '') +
        '</div>';

    // Scenario click handlers
    var listEl = document.getElementById('wg-scenario-list');
    if (listEl) {
        listEl.querySelectorAll('.wargame-card').forEach(function(card) {
            card.addEventListener('click', async function() {
                listEl.querySelectorAll('.wargame-card').forEach(function(c) { c.classList.remove('active'); });
                card.classList.add('active');
                var idx = parseInt(card.dataset.idx);
                var scenario = scenarioList[idx];
                var resultArea = document.getElementById('wg-result-area');
                resultArea.innerHTML = '<div class="loading">EXECUTING SIMULATION</div>';

                var result = null;
                try {
                    result = await api('/api/wargame/run/' + (scenario.id || idx));
                } catch (e) {
                    // May fail
                }

                if (!result) {
                    var fallbackPhasesHtml = '';
                    if (scenario.phases && scenario.phases.length) {
                        fallbackPhasesHtml = '<div class="phase-flow">';
                        scenario.phases.forEach(function(p, pi) {
                            fallbackPhasesHtml += '<div class="phase-step"><div class="phase-step-num">PHASE ' + (pi + 1) + '</div>' + p + '</div>';
                        });
                        fallbackPhasesHtml += '</div>';
                    }
                    resultArea.innerHTML = '<div class="wargame-result-panel">' +
                        '<div class="wargame-result-head"><h3 style="font-size:10px;letter-spacing:1.5px;color:var(--amber)">' + (scenario.title || scenario.name) + '</h3><span>' + badge(scenario.severity || 'high') + '</span></div>' +
                        '<div class="wargame-result-body">' +
                            '<div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:8px">' + (scenario.description || '') + '</div>' +
                            fallbackPhasesHtml +
                            '<div style="text-align:center;padding:16px;color:var(--amber);font-size:10px;letter-spacing:1px">DETAILED SIMULATION RESULTS PENDING ENGINE INITIALIZATION</div>' +
                        '</div></div>';
                    return;
                }

                // Render full result
                var resultPhasesHtml = '';
                if (result.phases && result.phases.length) {
                    resultPhasesHtml = '<div style="margin-top:8px"><span class="intel-label">ESCALATION PHASES</span><div class="phase-flow" style="margin-top:4px">';
                    result.phases.forEach(function(p, pi) {
                        var phaseText = typeof p === 'object' ? (p.description || p.name || JSON.stringify(p)) : p;
                        resultPhasesHtml += '<div class="phase-step"><div class="phase-step-num">PHASE ' + (pi + 1) + '</div>' + phaseText + '</div>';
                    });
                    resultPhasesHtml += '</div></div>';
                }

                function formatVal(v) {
                    if (typeof v === 'object') return Array.isArray(v) ? v.join('; ') : JSON.stringify(v);
                    return v;
                }

                resultArea.innerHTML = '<div class="wargame-result-panel">' +
                    '<div class="wargame-result-head"><h3 style="font-size:10px;letter-spacing:1.5px;color:var(--amber)">' + (result.title || scenario.title || 'SIMULATION RESULT') + '</h3>' +
                        '<span>' + badge(result.severity || scenario.severity || 'high') + ' ' + livePulse('COMPLETE', '') + '</span></div>' +
                    '<div class="wargame-result-body" style="max-height:calc(100vh - 320px);overflow-y:auto">' +
                        (result.description ? '<div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:8px">' + result.description + '</div>' : '') +
                        (result.engagement_capacity ? '<div class="wargame-stat-row"><span class="wargame-stat-label">ENGAGEMENT CAPACITY</span><span class="wargame-stat-val">' + formatVal(result.engagement_capacity) + '</span></div>' : '') +
                        (result.impact_assessment ? '<div class="wargame-stat-row"><span class="wargame-stat-label">IMPACT ASSESSMENT</span><span class="wargame-stat-val" style="color:var(--red)">' + formatVal(result.impact_assessment) + '</span></div>' : '') +
                        (result.debris_consequences ? '<div class="wargame-stat-row"><span class="wargame-stat-label">DEBRIS CONSEQUENCES</span><span class="wargame-stat-val">' + formatVal(result.debris_consequences) + '</span></div>' : '') +
                        (result.fvey_response_options ? '<div class="wargame-stat-row"><span class="wargame-stat-label">FVEY RESPONSE</span><span class="wargame-stat-val" style="color:var(--green)">' + formatVal(result.fvey_response_options) + '</span></div>' : '') +
                        (result.reconstitution_timeline ? '<div class="wargame-stat-row"><span class="wargame-stat-label">RECONSTITUTION</span><span class="wargame-stat-val" style="color:var(--cyan)">' + formatVal(result.reconstitution_timeline) + '</span></div>' : '') +
                        resultPhasesHtml +
                        (result.outcome ? '<div style="margin-top:8px;padding:8px;background:rgba(255,176,0,0.03);border:1px solid var(--border)"><span class="intel-label">OUTCOME</span><div style="font-size:10px;color:var(--text);line-height:1.5;margin-top:3px">' + formatVal(result.outcome) + '</div></div>' : '') +
                    '</div></div>';
            });
        });
    }

    // Render resilience
    if (resilience) {
        var resEl = document.getElementById('wg-resilience');
        if (resEl) {
            if (typeof resilience === 'object') {
                var resHtml = '';
                Object.entries(resilience).forEach(function(entry) {
                    resHtml += '<div class="wargame-stat-row">' +
                        '<span class="wargame-stat-label">' + entry[0].replace(/_/g, ' ').toUpperCase() + '</span>' +
                        '<span class="wargame-stat-val">' + (typeof entry[1] === 'object' ? JSON.stringify(entry[1]) : entry[1]) + '</span>' +
                        '</div>';
                });
                resEl.innerHTML = resHtml;
            } else {
                resEl.innerHTML = '<div style="font-size:10px;color:var(--text);line-height:1.6">' + resilience + '</div>';
            }
        }
    }
};


/* ================================================================
   PAGE 11: INCIDENTS
   Historical timeline of space security incidents
   ================================================================ */
Pages.incidents = async function (el) {
    el.innerHTML = '<div class="loading">LOADING INCIDENT DATABASE</div>';

    var results = await Promise.all([
        api('/api/incidents'),
        api('/api/incidents/stats'),
    ]);

    var all = results[0] || [];
    var incStats = results[1] || {};
    if (!all.length) { el.innerHTML = '<div class="empty-state">INCIDENT DATA UNAVAILABLE</div>'; return; }

    var byType = incStats.by_type || {};
    var byActor = incStats.by_actor || {};
    var bySeverity = incStats.by_severity || {};

    var types = [];
    var actors = [];
    var typeSet = {};
    var actorSet = {};
    all.forEach(function(inc) {
        if (inc.type && !typeSet[inc.type]) { types.push(inc.type); typeSet[inc.type] = true; }
        if (inc.actor && !actorSet[inc.actor]) { actors.push(inc.actor); actorSet[inc.actor] = true; }
    });

    // Build stats cards
    var statsCardsHtml = '<div class="incident-stat-card" style="border-left:2px solid var(--red)">' +
        '<div class="incident-stat-val" style="color:var(--red)">' + all.length + '</div>' +
        '<div class="incident-stat-label">TOTAL INCIDENTS</div></div>';
    Object.entries(bySeverity).slice(0, 4).forEach(function(entry) {
        statsCardsHtml += '<div class="incident-stat-card"><div class="incident-stat-val">' + entry[1] + '</div><div class="incident-stat-label">' + entry[0].toUpperCase() + '</div></div>';
    });
    Object.entries(byActor).slice(0, 3).forEach(function(entry) {
        statsCardsHtml += '<div class="incident-stat-card"><div class="incident-stat-val">' + entry[1] + '</div><div class="incident-stat-label">' + entry[0].toUpperCase() + '</div></div>';
    });

    // Build type distribution
    var typeDistHtml = '';
    var typeColors = ['#FF2020', '#FF8C00', '#FFD700', '#C040FF', '#2080FF', '#20FF60', '#00D4FF'];
    var tIdx = 0;
    Object.entries(byType).sort(function(a, b) { return b[1] - a[1]; }).forEach(function(entry) {
        typeDistHtml += '<div class="cat-breakdown"><span class="cat-label">' + entry[0].replace(/-/g, ' ').toUpperCase() + '</span><div class="cat-bar-wrap"><div class="cat-bar" style="width:' + (entry[1] / all.length * 100) + '%;background:' + typeColors[tIdx % typeColors.length] + '"></div></div><span class="cat-count">' + entry[1] + '</span></div>';
        tIdx++;
    });

    // Build actor distribution
    var actorDistHtml = '';
    var actorColorMap = { 'PRC': '#FF2020', 'China': '#FF2020', 'Russia': '#FF8C00', 'CIS': '#FF8C00', 'India': '#20FF60', 'US': '#2080FF', 'USA': '#2080FF' };
    Object.entries(byActor).sort(function(a, b) { return b[1] - a[1]; }).forEach(function(entry) {
        var col = actorColorMap[entry[0]] || '#FFB000';
        actorDistHtml += '<div class="cat-breakdown"><span class="cat-label" style="color:' + col + '">' + entry[0] + '</span><div class="cat-bar-wrap"><div class="cat-bar" style="width:' + (entry[1] / all.length * 100) + '%;background:' + col + '"></div></div><span class="cat-count">' + entry[1] + '</span></div>';
    });

    // Build filter tabs
    var filterTabsHtml = '<div class="filter-tab active" data-filter="all">ALL (' + all.length + ')</div>';
    types.slice(0, 5).forEach(function(t) {
        filterTabsHtml += '<div class="filter-tab" data-filter="type:' + t + '">' + t.replace(/-/g, ' ').toUpperCase() + '</div>';
    });
    actors.slice(0, 4).forEach(function(a) {
        filterTabsHtml += '<div class="filter-tab" data-filter="actor:' + a + '">' + a.toUpperCase() + '</div>';
    });

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="strategy-banner" style="border-bottom-color:var(--cis)">' +
            '<div class="strategy-title">SPACE SECURITY INCIDENT DATABASE</div>' +
            '<div class="strategy-subtitle">UNCLASSIFIED // ' + all.length + ' DOCUMENTED INCIDENTS // OSINT COMPILATION</div>' +
        '</div>' +
        '<div class="incident-stats-grid">' + statsCardsHtml + '</div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:4px">' +
            '<div class="panel"><div class="panel-head"><h3>BY TYPE</h3></div><div class="panel-body">' + typeDistHtml + '</div></div>' +
            '<div class="panel"><div class="panel-head"><h3>BY ACTOR</h3></div><div class="panel-body">' + actorDistHtml + '</div></div>' +
        '</div>' +
        '<div class="filter-tabs" id="incident-filters">' + filterTabsHtml + '</div>' +
        '<div class="panel"><div class="panel-head"><h3>INCIDENT TIMELINE</h3><span class="ph-meta">' + livePulse('', '') + ' ' + all.length + ' EVENTS</span></div>' +
            '<div class="panel-body" style="max-height:calc(100vh - 460px)" id="incident-timeline-wrap"></div></div>' +
        '<!-- MANEUVER INDICATORS WATCHLIST -->' +
        '<div class="panel" style="margin-top:4px" id="incident-maneuver-panel">' +
            '<div class="panel-head"><h3>MANEUVER INDICATORS WATCHLIST</h3><span class="ph-meta">' + livePulse('120S', 'red') + '</span></div>' +
            '<div class="panel-body" id="incident-maneuver-body"><div class="loading">LOADING WATCHLIST</div></div>' +
        '</div>' +
        '</div>';

    function renderTimeline(filter) {
        var filtered = all;
        if (filter && filter !== 'all') {
            if (filter.indexOf('type:') === 0) {
                var t = filter.replace('type:', '');
                filtered = all.filter(function(i) { return i.type === t; });
            } else if (filter.indexOf('actor:') === 0) {
                var a = filter.replace('actor:', '');
                filtered = all.filter(function(i) { return i.actor === a; });
            }
        }

        filtered.sort(function(a, b) {
            var dateA = a.date ? new Date(a.date).getTime() : (a.year ? new Date(a.year + '-01-01').getTime() : 0);
            var dateB = b.date ? new Date(b.date).getTime() : (b.year ? new Date(b.year + '-01-01').getTime() : 0);
            return dateB - dateA;
        });

        var timelineEl = document.getElementById('incident-timeline-wrap');
        if (!timelineEl) return;

        var html = '<div class="incident-timeline">';
        filtered.forEach(function(inc) {
            var date = inc.date ? new Date(inc.date).toISOString().substring(0, 10) : (inc.year ? inc.year + '' : '?');
            var sev = (inc.severity || 'medium').toLowerCase();
            var col = actorColorMap[inc.actor] || '#FFB000';
            html += '<div class="incident-item">';
            html += '<div class="incident-date">' + date + '</div>';
            html += '<div class="incident-dot ' + sev + '"></div>';
            html += '<div class="incident-head">';
            html += badge(sev);
            if (inc.actor) html += ' <span class="badge" style="background:rgba(255,255,255,0.05);color:' + col + ';border:1px solid ' + col + '">' + inc.actor + '</span>';
            if (inc.type) html += ' <span style="font-size:8px;letter-spacing:1px;color:var(--text-muted)">' + inc.type.replace(/-/g, ' ').toUpperCase() + '</span>';
            html += ' <span class="incident-title">' + (inc.title || inc.name || '?') + '</span>';
            html += '</div>';
            html += '<div class="incident-body">' + (inc.description || '') + '</div>';
            html += '<div class="incident-meta">';
            if (inc.impact) html += '<span>IMPACT: <span style="color:var(--red)">' + inc.impact + '</span></span>';
            if (inc.orbit_affected) html += '<span>ORBIT: ' + inc.orbit_affected + '</span>';
            if (inc.debris_generated) html += '<span>DEBRIS: <span style="color:var(--cis)">' + inc.debris_generated + '</span></span>';
            if (inc.source) html += '<span style="color:var(--text-muted)">SRC: ' + inc.source + '</span>';
            html += '</div></div>';
        });
        html += '</div>';
        timelineEl.innerHTML = html;
    }

    renderTimeline('all');
    el.querySelectorAll('#incident-filters .filter-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            el.querySelectorAll('#incident-filters .filter-tab').forEach(function(t) { t.classList.remove('active'); });
            tab.classList.add('active');
            renderTimeline(tab.dataset.filter);
        });
    });

    // Fetch maneuver indicators watchlist
    function renderManeuverIndicators(data) {
        var mBody = document.getElementById('incident-maneuver-body');
        if (!mBody) return;
        if (!data) {
            mBody.innerHTML = '<div class="empty-state">MANEUVER DATA UNAVAILABLE</div>';
            return;
        }
        var mHtml = '';
        if (typeof data === 'string') {
            mHtml = '<div class="intel-summary" style="white-space:pre-line">' + data + '</div>';
        } else {
            var mArr = Array.isArray(data) ? data : (data.indicators || data.watchlist || data.entries || [data]);
            if (!Array.isArray(mArr)) mArr = [mArr];
            mArr.forEach(function(m) {
                if (typeof m === 'string') {
                    mHtml += '<div style="padding:3px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:10px;color:var(--text)">' + m + '</div>';
                    return;
                }
                var mName = m.satellite || m.name || m.object || 'UNKNOWN';
                var mSev = (m.severity || m.risk || m.priority || 'medium').toLowerCase();
                var mCol = mSev === 'critical' || mSev === 'high' ? 'var(--red)' : 'var(--amber)';
                mHtml += '<div class="threat-card severity-' + mSev + '">' +
                    '<div class="tc-header">' +
                        badge(mSev) + ' ' +
                        (m.country ? countryBadge(m.country === 'Russia' ? 'CIS' : m.country === 'China' ? 'PRC' : m.country) + ' ' : '') +
                        '<span class="tc-title">' + mName + '</span>' +
                    '</div>' +
                    '<div class="tc-body">' + (m.description || m.activity || m.assessment || '') + '</div>' +
                    '<div class="tc-meta">' +
                        (m.type ? 'TYPE: <span style="color:' + mCol + '">' + m.type.toUpperCase() + '</span> // ' : '') +
                        (m.last_maneuver ? 'LAST: ' + m.last_maneuver + ' // ' : '') +
                        (m.delta_v ? 'DV: ' + m.delta_v + ' // ' : '') +
                        (m.timestamp ? timeAgo(m.timestamp) : '') +
                    '</div>' +
                '</div>';
            });
        }
        mBody.innerHTML = mHtml || '<div class="empty-state">NO MANEUVER INDICATORS</div>';
    }

    api('/api/analysis/maneuver-indicators').then(function(mData) {
        renderManeuverIndicators(mData);
    });

    registerInterval(async function() {
        var freshMData = await api('/api/analysis/maneuver-indicators');
        renderManeuverIndicators(freshMData);
    }, 120000);
};


/* ================================================================
   PAGE 12: FUTURES -- Space Program Tracking
   ================================================================ */
Pages.futures = async function(el) {
    el.innerHTML = '<div class="loading">LOADING FUTURES INTELLIGENCE</div>';
    var results = await Promise.all([
        api('/api/futures'),
        api('/api/futures/summary'),
    ]);
    var data = results[0];
    var summary = results[1];
    if (!data) { el.innerHTML = '<div class="empty-state">FUTURES DATA UNAVAILABLE</div>'; return; }

    var programs = Array.isArray(data) ? data : [];
    var advCount = programs.filter(function(p) { return ['PRC','Russia','DPRK','Iran'].includes(p.nation); }).length;
    var alliedCount = programs.filter(function(p) { return ['US','UK','Australia','Canada','NZ','Japan','South Korea','NATO'].includes(p.nation); }).length;

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">' + advCount + '</div><div class="tb-lbl">ADVERSARY PROGRAMS</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9733;</div><div><div class="tb-val">' + alliedCount + '</div><div class="tb-lbl">ALLIED PROGRAMS</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">' + programs.length + '</div><div class="tb-lbl">TOTAL TRACKED</div></div></div>' +
        '</div>' +
        '<div class="filter-tabs mb-2" id="futures-tabs">' +
            '<div class="filter-tab active" data-filter="all">ALL</div>' +
            '<div class="filter-tab" data-filter="PRC" style="color:var(--red)">PRC</div>' +
            '<div class="filter-tab" data-filter="Russia" style="color:var(--cis)">RUSSIA</div>' +
            '<div class="filter-tab" data-filter="US" style="color:var(--cyan)">US/FVEY</div>' +
            '<div class="filter-tab" data-filter="adversary">ADVERSARY</div>' +
            '<div class="filter-tab" data-filter="ASAT">ASAT/COUNTER</div>' +
            '<div class="filter-tab" data-filter="lunar">LUNAR</div>' +
        '</div>' +
        '<div id="futures-list"></div></div>';

    function renderFutures(filter) {
        var filtered = programs;
        if (filter === 'adversary') filtered = programs.filter(function(p) { return ['PRC','Russia','DPRK','Iran'].includes(p.nation); });
        else if (filter === 'US') filtered = programs.filter(function(p) { return ['US','UK','Australia','Canada','NZ','Japan','South Korea','NATO'].includes(p.nation); });
        else if (filter === 'ASAT') filtered = programs.filter(function(p) { return (p.domain||'').toLowerCase().indexOf('asat') >= 0 || (p.domain||'').toLowerCase().indexOf('counter') >= 0; });
        else if (filter === 'lunar') filtered = programs.filter(function(p) { return (p.domain||'').toLowerCase().indexOf('lunar') >= 0 || (p.description||'').toLowerCase().indexOf('lunar') >= 0 || (p.description||'').toLowerCase().indexOf('moon') >= 0; });
        else if (filter !== 'all') filtered = programs.filter(function(p) { return p.nation === filter; });

        var html = '<div class="futures-grid">';
        filtered.forEach(function(p) {
            var isAdv = ['PRC','Russia','DPRK','Iran'].includes(p.nation);
            var cCode = p.nation === 'Russia' ? 'CIS' : p.nation === 'DPRK' ? 'NKOR' : p.nation === 'Iran' ? 'IRAN' : p.nation === 'PRC' ? 'PRC' : 'US';
            var col = countryColor(cCode);
            var statusCol = p.status === 'operational' ? 'var(--green)' : p.status === 'development' ? 'var(--amber)' : p.status === 'delayed' ? 'var(--red)' : 'var(--cyan)';
            html += '<div class="threat-card severity-' + (isAdv ? 'high' : 'low') + '" style="border-left-color:' + col + '">' +
                '<div class="tc-header">' +
                    '<span class="badge badge-' + (isAdv ? 'prc' : 'fvey') + '">' + (p.nation || '?') + '</span>' +
                    ' <span class="tc-title">' + (p.program_name || p.name || '?') + '</span>' +
                '</div>' +
                '<div class="tc-body">' + (p.description || '') + '</div>' +
                '<div class="tc-meta">' +
                    'DOMAIN: ' + (p.domain || '?') + ' // STATUS: <span style="color:' + statusCol + '">' + (p.status||'?').toUpperCase() + '</span>' +
                    (p.timeline ? ' // TIMELINE: ' + p.timeline : '') +
                '</div>' +
                (p.strategic_impact ? '<div class="tc-source">IMPACT: ' + p.strategic_impact + '</div>' : '') +
            '</div>';
        });
        html += '</div>';
        document.getElementById('futures-list').innerHTML = html;
    }

    renderFutures('all');
    el.querySelectorAll('#futures-tabs .filter-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            el.querySelectorAll('#futures-tabs .filter-tab').forEach(function(t) { t.classList.remove('active'); });
            tab.classList.add('active');
            renderFutures(tab.dataset.filter);
        });
    });
};


/* ================================================================
   PAGE 13: CONFERENCES -- Global Space Forums Tracker
   ================================================================ */
Pages.conferences = async function(el) {
    el.innerHTML = '<div class="loading">LOADING CONFERENCE INTELLIGENCE</div>';
    var results = await Promise.all([
        api('/api/conferences/upcoming'),
        api('/api/conferences'),
    ]);

    var events = Array.isArray(results[0]) ? results[0] : (Array.isArray(results[1]) ? results[1] : []);
    var highCount = events.filter(function(e) { return (e.relevance_to_fvey || e.relevance) === 'high'; }).length;

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">' + events.length + '</div><div class="tb-lbl">TRACKED EVENTS</div></div></div>' +
            '<div class="tb-cell alert"><div class="tb-icon">&#9733;</div><div><div class="tb-val">' + highCount + '</div><div class="tb-lbl">HIGH RELEVANCE</div></div></div>' +
            '<div class="tb-cell"><div><div class="tb-val"><span class="live-indicator"><span class="live-dot"></span> LIVE</span></div><div class="tb-lbl">600S REFRESH <span id="conf-live-ts" class="last-updated-ts">' + zulu() + '</span></div></div></div>' +
        '</div>' +
        '<div class="filter-tabs mb-2" id="conf-tabs">' +
            '<div class="filter-tab active" data-filter="all">ALL</div>' +
            '<div class="filter-tab" data-filter="high" style="color:var(--red)">HIGH RELEVANCE</div>' +
            '<div class="filter-tab" data-filter="military">MILITARY/GOV</div>' +
            '<div class="filter-tab" data-filter="industry">INDUSTRY</div>' +
            '<div class="filter-tab" data-filter="academic">ACADEMIC</div>' +
        '</div>' +
        '<div id="conf-list"></div></div>';

    function renderConfs(filter) {
        var filtered = events;
        if (filter === 'high') filtered = events.filter(function(e) { return (e.relevance_to_fvey || e.relevance) === 'high'; });
        else if (filter === 'military') filtered = events.filter(function(e) { return (e.category||e.organization||'').toLowerCase().match(/military|government|defense|defence|nato|space force|dod/); });
        else if (filter === 'industry') filtered = events.filter(function(e) { return (e.category||e.organization||'').toLowerCase().match(/industry|commercial|conference|satellite|iac/); });
        else if (filter === 'academic') filtered = events.filter(function(e) { return (e.category||e.organization||'').toLowerCase().match(/academic|research|university|think tank|csis|swf/); });

        var html = '';
        if (!filtered.length) {
            html = '<div class="empty-state">NO EVENTS FOUND</div>';
        } else {
            filtered.forEach(function(e) {
                var rel = (e.relevance_to_fvey || e.relevance || '?');
                var relCol = rel === 'high' ? 'var(--red)' : rel === 'medium' ? 'var(--amber)' : 'var(--cyan)';
                var nextDate = e.next_occurrence || e.date_start || '';
                html += '<div class="threat-card severity-medium conf-card" style="border-left-color:' + relCol + '">' +
                    '<div class="tc-header">' +
                        '<span class="badge" style="background:rgba(255,176,0,0.1);color:' + relCol + ';border:1px solid ' + relCol + '">' + rel.toUpperCase() + '</span>' +
                        ' <span class="tc-title">' + (e.name || '?') + '</span>' +
                        (nextDate ? '<span class="conf-next-date" style="color:' + relCol + '">' + nextDate + '</span>' : '') +
                    '</div>' +
                    '<div class="tc-body">' + (e.description || '') + '</div>' +
                    '<div class="tc-meta">' +
                        (e.organization ? 'ORG: ' + e.organization + ' // ' : '') +
                        (e.location ? 'LOCATION: ' + e.location + ' // ' : '') +
                        (e.frequency ? 'FREQ: ' + e.frequency : '') +
                    '</div>' +
                    (e.topics && e.topics.length ? '<div class="tc-source">TOPICS: ' + e.topics.join(', ') + '</div>' : '') +
                    (e.url ? '<div class="tc-source"><a href="' + e.url + '" target="_blank" style="color:var(--cyan)">' + e.url + '</a></div>' : '') +
                '</div>';
            });
        }
        document.getElementById('conf-list').innerHTML = html;
    }

    renderConfs('all');
    el.querySelectorAll('#conf-tabs .filter-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            el.querySelectorAll('#conf-tabs .filter-tab').forEach(function(t) { t.classList.remove('active'); });
            tab.classList.add('active');
            renderConfs(tab.dataset.filter);
        });
    });

    // --- AUTO-REFRESH: Conference events every 600s ---
    registerInterval(async function() {
        var freshResults = await Promise.all([
            api('/api/conferences/upcoming'),
            api('/api/conferences'),
        ]);
        var freshEvents = Array.isArray(freshResults[0]) ? freshResults[0] : (Array.isArray(freshResults[1]) ? freshResults[1] : []);
        if (freshEvents.length > 0) {
            events = freshEvents;
            // Re-render with current filter
            var activeConfTab = el.querySelector('#conf-tabs .filter-tab.active');
            var currentFilter = activeConfTab ? activeConfTab.dataset.filter : 'all';
            renderConfs(currentFilter);
        }
        var confTsEl = document.getElementById('conf-live-ts');
        if (confTsEl) confTsEl.textContent = zulu();
    }, 600000);
};


/* ================================================================
   PAGE 14: ARCHITECTURE -- Ground Segment Architecture
   ================================================================ */
Pages.architecture = async function(el) {
    el.innerHTML = '<div class="loading">LOADING ARCHITECTURE INTELLIGENCE</div>';
    var results = await Promise.all([
        api('/api/architecture/prc'),
        api('/api/architecture/russia'),
        api('/api/architecture/fvey'),
        api('/api/architecture/comparison'),
    ]);

    var prc = results[0];
    var russia = results[1];
    var fvey = results[2];
    var comparison = results[3];

    el.innerHTML = '<div class="page-wrap">' +
        '<div class="threat-bar mb-2">' +
            '<div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">PRC</div><div class="tb-lbl">ADVERSARY ARCH</div></div></div>' +
            '<div class="tb-cell warning"><div class="tb-icon">&#9760;</div><div><div class="tb-val">RUS</div><div class="tb-lbl">ADVERSARY ARCH</div></div></div>' +
            '<div class="tb-cell info"><div class="tb-icon">&#9733;</div><div><div class="tb-val">FVEY</div><div class="tb-lbl">ALLIED ARCH</div></div></div>' +
        '</div>' +
        '<div class="country-tabs mb-2" id="arch-tabs">' +
            '<div class="country-tab active" data-arch="prc" style="color:var(--red)">PRC ARCHITECTURE</div>' +
            '<div class="country-tab" data-arch="russia" style="color:var(--cis)">RUSSIAN ARCHITECTURE</div>' +
            '<div class="country-tab" data-arch="fvey" style="color:var(--cyan)">FVEY ARCHITECTURE</div>' +
            '<div class="country-tab" data-arch="comparison">COMPARISON</div>' +
        '</div>' +
        '<div id="arch-detail"></div>' +
        '<!-- CISLUNAR AWARENESS -->' +
        '<div class="panel" style="margin-top:4px" id="arch-cislunar-panel">' +
            '<div class="panel-head"><h3>CISLUNAR / BEYOND-GEO AWARENESS</h3><span class="ph-meta">' + liveIndicator('') + '</span></div>' +
            '<div class="panel-body" id="arch-cislunar-body"><div class="loading">LOADING CISLUNAR DATA</div></div>' +
        '</div>' +
        '</div>';

    function renderArch(which) {
        var data = which === 'prc' ? prc : which === 'russia' ? russia : which === 'fvey' ? fvey : comparison;
        if (!data) { document.getElementById('arch-detail').innerHTML = '<div class="empty-state">DATA UNAVAILABLE</div>'; return; }

        if (which === 'comparison') {
            var compHtml = '';
            if (typeof data === 'object') {
                Object.entries(data).forEach(function(entry) {
                    var key = entry[0];
                    var val = entry[1];
                    if (typeof val === 'string') {
                        compHtml += '<div class="intel-field"><span class="intel-label">' + key.replace(/_/g,' ').toUpperCase() + '</span>' + val + '</div>';
                    } else if (typeof val === 'object' && !Array.isArray(val)) {
                        compHtml += '<div class="threat-card severity-medium"><div class="tc-header"><span class="tc-title">' + key.replace(/_/g,' ').toUpperCase() + '</span></div><div class="tc-body">' + JSON.stringify(val, null, 1).replace(/[{}"]/g,'').replace(/,\n/g,'<br>') + '</div></div>';
                    }
                });
            } else {
                compHtml = '<div class="tc-body" style="white-space:pre-wrap">' + JSON.stringify(data, null, 2) + '</div>';
            }
            document.getElementById('arch-detail').innerHTML = '<div class="panel mb-2"><div class="panel-head"><h3>ADVERSARY vs FVEY GROUND ARCHITECTURE COMPARISON</h3></div><div class="panel-body" style="max-height:none">' + compHtml + '</div></div>';
            return;
        }

        var col = which === 'prc' ? 'var(--red)' : which === 'russia' ? 'var(--cis)' : 'var(--cyan)';
        var label = which === 'prc' ? 'PRC' : which === 'russia' ? 'RUSSIAN' : 'FVEY';

        var sections = (typeof data === 'object' && !Array.isArray(data)) ? Object.entries(data) : [];
        var html = '';
        sections.forEach(function(entry) {
            var key = entry[0];
            var val = entry[1];
            if (key === 'country' || key === 'generated_utc') return;
            var title = key.replace(/_/g, ' ').toUpperCase();
            var body = '';
            if (typeof val === 'string') {
                body = '<div class="tc-body">' + val + '</div>';
            } else if (Array.isArray(val)) {
                val.forEach(function(item) {
                    if (typeof item === 'string') {
                        body += '<div style="padding:3px 0;border-bottom:1px solid var(--border);font-size:10px">' + item + '</div>';
                    } else if (typeof item === 'object') {
                        body += '<div class="threat-card severity-medium" style="border-left-color:' + col + '">' +
                            '<div class="tc-header"><span class="tc-title">' + (item.name || item.title || Object.values(item)[0] || '?') + '</span></div>' +
                            '<div class="tc-body">' + (item.description || item.role || item.detail || JSON.stringify(item)) + '</div>' +
                            (item.facilities ? '<div class="tc-meta">FACILITIES: ' + (Array.isArray(item.facilities) ? item.facilities.join(', ') : item.facilities) + '</div>' : '') +
                            (item.coverage ? '<div class="tc-meta">COVERAGE: ' + item.coverage + '</div>' : '') +
                            (item.vulnerability ? '<div class="tc-source arch-vuln-highlight" style="color:var(--red)">VULNERABILITY: ' + item.vulnerability + '</div>' : '') +
                        '</div>';
                    }
                });
            } else if (typeof val === 'object') {
                Object.entries(val).forEach(function(subEntry) {
                    body += '<div class="intel-field"><span class="intel-label">' + subEntry[0].replace(/_/g,' ').toUpperCase() + '</span>' + (typeof subEntry[1] === 'string' ? subEntry[1] : JSON.stringify(subEntry[1])) + '</div>';
                });
                body = '<div class="tc-body" style="font-size:10px">' + body + '</div>';
            }
            html += '<div class="panel mb-2"><div class="panel-head"><h3>' + label + ' // ' + title + '</h3></div><div class="panel-body" style="max-height:500px">' + body + '</div></div>';
        });
        document.getElementById('arch-detail').innerHTML = html;
    }

    renderArch('prc');
    el.querySelectorAll('#arch-tabs .country-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            el.querySelectorAll('#arch-tabs .country-tab').forEach(function(t) { t.classList.remove('active'); });
            tab.classList.add('active');
            renderArch(tab.dataset.arch);
        });
    });

    // Fetch cislunar awareness data
    api('/api/analysis/cislunar').then(function(cisData) {
        var cisBody = document.getElementById('arch-cislunar-body');
        if (!cisBody) return;
        if (!cisData) {
            cisBody.innerHTML = '<div class="empty-state">CISLUNAR DATA UNAVAILABLE</div>';
            return;
        }
        var cHtml = '';
        if (typeof cisData === 'string') {
            cHtml = '<div class="intel-summary" style="white-space:pre-line;line-height:1.6">' + cisData + '</div>';
        } else {
            // Summary / assessment
            if (cisData.assessment || cisData.summary) {
                cHtml += '<div class="intel-summary" style="margin-bottom:8px">' + (cisData.assessment || cisData.summary) + '</div>';
            }
            // Objects or missions beyond GEO
            var cisArr = cisData.objects || cisData.missions || cisData.assets || [];
            if (Array.isArray(cisArr) && cisArr.length) {
                cHtml += '<div class="section-head" style="margin-bottom:2px">TRACKED BEYOND-GEO OBJECTS</div>';
                cHtml += '<div class="asat-grid">';
                cisArr.forEach(function(obj) {
                    if (typeof obj === 'string') {
                        cHtml += '<div style="padding:4px;font-size:10px;color:var(--text)">' + obj + '</div>';
                        return;
                    }
                    var oName = obj.name || obj.designation || obj.mission || '?';
                    var oCountry = obj.country || obj.operator || '';
                    var oCol = oCountry === 'PRC' || oCountry === 'China' ? 'var(--red)' : oCountry === 'CIS' || oCountry === 'Russia' ? 'var(--cis)' : 'var(--cyan)';
                    cHtml += '<div class="threat-card severity-medium" style="border-left-color:' + oCol + '">' +
                        '<div class="tc-header">' +
                            (oCountry ? '<span class="badge" style="background:rgba(255,255,255,0.05);color:' + oCol + ';border:1px solid ' + oCol + '">' + oCountry.toUpperCase() + '</span> ' : '') +
                            '<span class="tc-title">' + oName + '</span>' +
                        '</div>' +
                        '<div class="tc-body">' + (obj.description || obj.mission_type || obj.purpose || '') + '</div>' +
                        '<div class="tc-meta">' +
                            (obj.orbit ? 'ORBIT: ' + obj.orbit + ' // ' : '') +
                            (obj.altitude ? 'ALT: ' + obj.altitude + ' // ' : '') +
                            (obj.status ? 'STATUS: ' + obj.status.toUpperCase() : '') +
                        '</div>' +
                    '</div>';
                });
                cHtml += '</div>';
            }
            // Challenges / threats
            if (cisData.challenges && Array.isArray(cisData.challenges)) {
                cHtml += '<div style="margin-top:8px"><span class="intel-label" style="color:var(--cis)">CISLUNAR CHALLENGES</span>';
                cisData.challenges.forEach(function(ch) {
                    var chText = typeof ch === 'string' ? ch : (ch.description || ch.title || JSON.stringify(ch));
                    cHtml += '<div style="padding:3px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:10px;color:var(--text)">' + chText + '</div>';
                });
                cHtml += '</div>';
            }
            if (cisData.intel_note) cHtml += '<div class="intel-summary" style="margin-top:4px">' + cisData.intel_note + '</div>';
            if (!cHtml) cHtml = '<div style="font-size:9px;color:var(--text);white-space:pre-wrap">' + JSON.stringify(cisData, null, 2).substring(0, 800) + '</div>';
        }
        cisBody.innerHTML = cHtml;
    });
};


/* ================================================================
   PAGE 15: SPACE ENVIRONMENT MONITORING
   Enhanced space weather, solar imagery, aurora, GOES, ENLIL,
   debris awareness — all 10 new API endpoints
   ================================================================ */
Pages.environment = async function (el) {
    el.innerHTML = '<div class="loading">LOADING SPACE ENVIRONMENT DATA</div>';

    // Fetch the master composite endpoint — all data in one call
    var env = await api('/api/environment/enhanced');

    if (!env) {
        el.innerHTML = '<div class="page-wrap"><div class="empty-state">ENVIRONMENT DATA UNAVAILABLE — RETRYING</div></div>';
        return;
    }

    var goes = env.goes_instruments || {};
    var aurora = env.aurora || {};
    var geospace = env.geospace || {};
    var forecasts = env.forecasts || {};
    var solarAct = env.solar_activity || {};
    var imagery = env.solar_imagery || {};
    var enlil = env.enlil_model || {};
    var debris = env.debris_awareness || {};

    // ---- Derived values for status strip ----
    var xrayLevel = '--';
    var xrayColor = 'var(--green)';
    var xrayData = goes.xray || {};
    var xrayLatest = xrayData.latest || {};
    var xrayKeys = Object.keys(xrayLatest);
    if (xrayKeys.length > 0) {
        var firstXray = xrayLatest[xrayKeys[0]];
        var fluxVal = firstXray ? firstXray.flux : null;
        if (fluxVal != null) {
            if (fluxVal >= 1e-4) { xrayLevel = 'X'; xrayColor = 'var(--red)'; }
            else if (fluxVal >= 1e-5) { xrayLevel = 'M'; xrayColor = 'var(--cis)'; }
            else if (fluxVal >= 1e-6) { xrayLevel = 'C'; xrayColor = 'var(--amber)'; }
            else if (fluxVal >= 1e-7) { xrayLevel = 'B'; xrayColor = 'var(--green)'; }
            else { xrayLevel = 'A'; xrayColor = 'var(--green)'; }
            xrayLevel += ' (' + fluxVal.toExponential(1) + ')';
        }
    }

    var protonAlert = 'NOMINAL';
    var protonColor = 'var(--green)';
    var protonData = goes.protons || {};
    var protonLatest = protonData.latest || {};
    var protonKeys = Object.keys(protonLatest);
    for (var pi = 0; pi < protonKeys.length; pi++) {
        var pk = protonKeys[pi];
        if (pk.indexOf('10') >= 0) {
            var pFlux = protonLatest[pk] ? protonLatest[pk].flux : null;
            if (pFlux != null && pFlux >= 10) {
                protonAlert = 'S1+ STORM';
                protonColor = 'var(--red)';
            }
            break;
        }
    }

    var kpNext = '--';
    var kpColor = 'var(--cyan)';
    var kpEntries = (forecasts.kp_forecast || {}).entries || [];
    if (kpEntries.length > 0) {
        var kpVal = kpEntries[0].kp;
        if (kpVal != null) {
            kpNext = String(kpVal);
            if (parseFloat(kpVal) >= 7) kpColor = 'var(--red)';
            else if (parseFloat(kpVal) >= 5) kpColor = 'var(--cis)';
            else if (parseFloat(kpVal) >= 4) kpColor = 'var(--amber)';
            else kpColor = 'var(--green)';
        }
    }

    var geoLatest = (geospace.latest || {});
    var bzVal = geoLatest.bz != null ? geoLatest.bz : '--';
    var bzColor = 'var(--green)';
    if (typeof bzVal === 'number') {
        bzColor = bzVal < -10 ? 'var(--red)' : bzVal < 0 ? 'var(--cis)' : 'var(--green)';
        bzVal = bzVal.toFixed(1) + ' nT';
    }

    var windSpeed = geoLatest.speed != null ? Math.round(geoLatest.speed) + ' km/s' : '--';
    var windColor = 'var(--cyan)';
    if (geoLatest.speed != null) {
        windColor = geoLatest.speed > 700 ? 'var(--red)' : geoLatest.speed > 500 ? 'var(--cis)' : 'var(--cyan)';
    }

    var auroraMax = aurora.max_probability != null ? aurora.max_probability + '%' : '--';
    var auroraColor = 'var(--cyan)';
    if (aurora.max_probability != null) {
        auroraColor = aurora.max_probability >= 50 ? 'var(--red)' : aurora.max_probability >= 25 ? 'var(--amber)' : 'var(--green)';
    }

    // ==== BUILD HTML ====
    var html = '<div class="page-wrap">';

    // ---- STATUS STRIP ----
    html += '<div class="env-status-strip">' +
        '<div class="env-status-cell" style="border-left:2px solid ' + xrayColor + '">' +
            '<div class="env-status-val" style="color:' + xrayColor + '">' + xrayLevel + '</div>' +
            '<div class="env-status-lbl">X-RAY FLUX</div>' +
        '</div>' +
        '<div class="env-status-cell" style="border-left:2px solid ' + protonColor + '">' +
            '<div class="env-status-val" style="color:' + protonColor + '">' + protonAlert + '</div>' +
            '<div class="env-status-lbl">PROTON STATUS</div>' +
        '</div>' +
        '<div class="env-status-cell" style="border-left:2px solid ' + kpColor + '">' +
            '<div class="env-status-val" style="color:' + kpColor + '">Kp ' + kpNext + '</div>' +
            '<div class="env-status-lbl">Kp FORECAST</div>' +
        '</div>' +
        '<div class="env-status-cell" style="border-left:2px solid ' + bzColor + '">' +
            '<div class="env-status-val" style="color:' + bzColor + '">' + bzVal + '</div>' +
            '<div class="env-status-lbl">GEOSPACE Bz</div>' +
        '</div>' +
        '<div class="env-status-cell" style="border-left:2px solid ' + windColor + '">' +
            '<div class="env-status-val" style="color:' + windColor + '">' + windSpeed + '</div>' +
            '<div class="env-status-lbl">SOLAR WIND</div>' +
        '</div>' +
        '<div class="env-status-cell" style="border-left:2px solid ' + auroraColor + '">' +
            '<div class="env-status-val" style="color:' + auroraColor + '">' + auroraMax + '</div>' +
            '<div class="env-status-lbl">AURORA MAX</div>' +
        '</div>' +
        '</div>';

    // ---- SECTION 1: SOLAR IMAGERY ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">SOLAR IMAGERY ' + liveIndicator('5M') + '</div>' +
        '</div>';

    var suvi = (imagery.suvi || {}).wavelengths || {};
    var sdo = imagery.sdo_hmi || {};
    var lascoC2 = imagery.lasco_c2 || {};
    var lascoC3 = imagery.lasco_c3 || {};
    var drap = imagery.drap || {};
    var enlilImg = imagery.enlil || {};

    html += '<div class="solar-img-grid">';

    // SUVI images
    var suviWaves = [
        { wl: '094', label: 'SUVI 094 A (Fe XVIII 6.3 MK)' },
        { wl: '171', label: 'SUVI 171 A (Fe IX 0.6 MK)' },
        { wl: '304', label: 'SUVI 304 A (He II 0.05 MK)' },
        { wl: '195', label: 'SUVI 195 A (Fe XII 1.6 MK)' }
    ];

    for (var si = 0; si < suviWaves.length; si++) {
        var sw = suviWaves[si];
        var imgUrl = suvi[sw.wl] || '';
        html += '<div class="solar-img-panel">' +
            '<div class="solar-img-label">' + sw.label + '</div>' +
            (imgUrl ? '<img src="' + imgUrl + '" alt="' + sw.label + '" loading="lazy">' : '<div class="empty-state">NO IMAGE</div>') +
            '</div>';
    }

    // SDO/HMI Magnetogram
    html += '<div class="solar-img-panel">' +
        '<div class="solar-img-label">SDO/HMI MAGNETOGRAM</div>' +
        (sdo.url ? '<img src="' + sdo.url + '" alt="SDO HMI" loading="lazy">' : '<div class="empty-state">NO IMAGE</div>') +
        '</div>';

    // LASCO C2
    html += '<div class="solar-img-panel">' +
        '<div class="solar-img-label">LASCO C2 (2-6 Rs)</div>' +
        (lascoC2.url ? '<img src="' + lascoC2.url + '" alt="LASCO C2" loading="lazy">' : '<div class="empty-state">NO IMAGE</div>') +
        '</div>';

    // LASCO C3
    html += '<div class="solar-img-panel">' +
        '<div class="solar-img-label">LASCO C3 (3.7-30 Rs)</div>' +
        (lascoC3.url ? '<img src="' + lascoC3.url + '" alt="LASCO C3" loading="lazy">' : '<div class="empty-state">NO IMAGE</div>') +
        '</div>';

    // D-RAP
    html += '<div class="solar-img-panel">' +
        '<div class="solar-img-label">D-RAP HF ABSORPTION</div>' +
        (drap.url ? '<img src="' + drap.url + '" alt="D-RAP" loading="lazy">' : '<div class="empty-state">NO IMAGE</div>') +
        '</div>';

    html += '</div>'; // end solar-img-grid

    // ---- SECTION 2: GOES INSTRUMENT DATA ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">GOES INSTRUMENT DATA ' + liveIndicator('5M') + '</div>' +
        '<div class="env-section-body" id="env-goes-body">';

    html += '<div class="grid-2">';
    // X-ray panel
    html += '<div class="panel mb-2"><div class="panel-head"><h3>X-RAY FLUX</h3></div><div class="panel-body">';
    html += '<div style="font-size:10px;color:var(--text);line-height:1.6">';
    html += '<div>CURRENT LEVEL: <span style="color:' + xrayColor + ';font-size:14px">' + xrayLevel + '</span></div>';
    for (var xi = 0; xi < xrayKeys.length; xi++) {
        var xk = xrayKeys[xi];
        var xd = xrayLatest[xk];
        html += '<div style="padding:2px 0;border-bottom:1px solid rgba(255,176,0,0.04)">' +
            '<span style="color:var(--amber);font-size:8px;letter-spacing:1px">' + xk + '</span> ' +
            '<span style="color:var(--white)">' + (xd && xd.flux != null ? xd.flux.toExponential(2) + ' W/m2' : '--') + '</span>' +
            '</div>';
    }
    html += '</div></div></div>';

    // Proton panel
    html += '<div class="panel mb-2"><div class="panel-head"><h3>PROTON FLUX</h3></div><div class="panel-body">';
    if (protonAlert !== 'NOMINAL') {
        html += '<div class="proton-alert-active">&#9888; PROTON EVENT: ' + protonAlert + '</div>';
    }
    html += '<div style="font-size:10px;color:var(--text);line-height:1.6">';
    for (var pj = 0; pj < protonKeys.length; pj++) {
        var ppk = protonKeys[pj];
        var ppd = protonLatest[ppk];
        html += '<div style="padding:2px 0;border-bottom:1px solid rgba(255,176,0,0.04)">' +
            '<span style="color:var(--amber);font-size:8px;letter-spacing:1px">' + ppk + '</span> ' +
            '<span style="color:var(--white)">' + (ppd && ppd.flux != null ? ppd.flux.toExponential(2) + ' pfu' : '--') + '</span>' +
            '</div>';
    }
    html += '</div></div></div>';
    html += '</div>'; // end grid-2

    html += '</div></div>'; // end goes section

    // ---- SECTION 3: SOLAR ACTIVITY ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">SOLAR ACTIVITY ' + liveIndicator('15M') + '</div>' +
        '<div class="env-section-body">';

    html += '<div class="grid-2">';

    // Flare probabilities
    html += '<div class="panel mb-2"><div class="panel-head"><h3>FLARE PROBABILITIES (24h)</h3></div><div class="panel-body">';
    var fProbs = (solarAct.flare_probabilities || {}).latest || {};
    var probItems = [
        { label: 'C-CLASS FLARE', val: fProbs.c_class_1d, color: 'var(--amber)' },
        { label: 'M-CLASS FLARE', val: fProbs.m_class_1d, color: 'var(--cis)' },
        { label: 'X-CLASS FLARE', val: fProbs.x_class_1d, color: 'var(--red)' },
        { label: 'PROTON EVENT', val: fProbs.proton_1d, color: 'var(--nkor)' }
    ];
    for (var fi = 0; fi < probItems.length; fi++) {
        var fp = probItems[fi];
        var fpVal = fp.val != null ? fp.val : 0;
        html += '<div class="flare-prob-row">' +
            '<span class="flare-prob-label">' + fp.label + '</span>' +
            '<div class="flare-prob-track">' +
            '<div class="flare-prob-fill" style="width:' + fpVal + '%;background:' + fp.color + '"></div>' +
            '</div>' +
            '<span class="flare-prob-val" style="color:' + fp.color + '">' + fpVal + '%</span>' +
            '</div>';
    }
    html += '</div></div>';

    // Active regions
    html += '<div class="panel mb-2"><div class="panel-head"><h3>ACTIVE SUNSPOT REGIONS</h3><span class="ph-meta">' +
        ((solarAct.active_regions || {}).count || 0) + ' REGIONS</span></div><div class="panel-body" style="max-height:200px">';
    var regions = ((solarAct.active_regions || {}).regions || []);
    if (regions.length > 0) {
        html += '<table class="env-region-table"><thead><tr>' +
            '<th>REGION</th><th>LOC</th><th>MAG</th><th>SPOTS</th><th>C%</th><th>M%</th><th>X%</th>' +
            '</tr></thead><tbody>';
        for (var ri = 0; ri < Math.min(regions.length, 15); ri++) {
            var rg = regions[ri];
            html += '<tr>' +
                '<td style="color:var(--white)">' + (rg.region || '--') + '</td>' +
                '<td>' + (rg.location || '--') + '</td>' +
                '<td>' + (rg.mag_class || '--') + '</td>' +
                '<td>' + (rg.num_spots != null ? rg.num_spots : '--') + '</td>' +
                '<td>' + (rg.c_prob != null ? rg.c_prob : '--') + '</td>' +
                '<td style="color:' + (rg.m_prob > 25 ? 'var(--cis)' : 'var(--text)') + '">' + (rg.m_prob != null ? rg.m_prob : '--') + '</td>' +
                '<td style="color:' + (rg.x_prob > 5 ? 'var(--red)' : 'var(--text)') + '">' + (rg.x_prob != null ? rg.x_prob : '--') + '</td>' +
                '</tr>';
        }
        html += '</tbody></table>';
    } else {
        html += '<div class="empty-state">NO ACTIVE REGIONS REPORTED</div>';
    }
    html += '</div></div>';

    html += '</div>'; // end grid-2
    html += '</div></div>'; // end solar activity section

    // ---- SECTION 4: AURORA ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">AURORA FORECAST ' + liveIndicator('5M') +
        '<span style="font-size:9px;color:' + auroraColor + '">MAX PROB: ' + auroraMax + '</span></div>' +
        '<div class="env-section-body">';

    var auroraImgN = (aurora.imagery || {}).north || '';
    var auroraImgS = (aurora.imagery || {}).south || '';

    html += '<div class="aurora-img-row">' +
        '<div class="aurora-img-panel">' +
        '<div class="solar-img-label">NORTHERN HEMISPHERE</div>' +
        (auroraImgN ? '<img src="' + auroraImgN + '" alt="Aurora North" loading="lazy">' : '<div class="empty-state">NO IMAGE</div>') +
        '</div>' +
        '<div class="aurora-img-panel">' +
        '<div class="solar-img-label">SOUTHERN HEMISPHERE</div>' +
        (auroraImgS ? '<img src="' + auroraImgS + '" alt="Aurora South" loading="lazy">' : '<div class="empty-state">NO IMAGE</div>') +
        '</div>' +
        '</div>';

    if (aurora.intel_note) {
        html += '<div class="intel-summary" style="margin-top:4px">' + aurora.intel_note + '</div>';
    }

    html += '</div></div>'; // end aurora section

    // ---- SECTION 5: SPACE WEATHER FORECASTS ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">SPACE WEATHER FORECASTS ' + liveIndicator('15M') + '</div>' +
        '<div class="env-section-body">';

    html += '<div class="grid-2">';

    // Kp forecast bar chart
    html += '<div class="panel mb-2"><div class="panel-head"><h3>Kp INDEX FORECAST</h3><span class="ph-meta">' + kpEntries.length + ' PERIODS</span></div><div class="panel-body">';
    if (kpEntries.length > 0) {
        html += '<div class="kp-forecast-strip">';
        var maxBars = Math.min(kpEntries.length, 32);
        for (var ki = 0; ki < maxBars; ki++) {
            var ke = kpEntries[ki];
            var kv = parseFloat(ke.kp) || 0;
            var kpBarColor = kv >= 7 ? 'var(--red)' : kv >= 5 ? 'var(--cis)' : kv >= 4 ? 'var(--amber)' : 'var(--green)';
            var kpBarH = Math.max(2, (kv / 9) * 100);
            var kpTimeLabel = (ke.time || '').substring(5, 13).replace('T', ' ');
            html += '<div class="kp-forecast-bar">' +
                '<div class="kp-forecast-bar-fill" style="height:' + kpBarH + '%;background:' + kpBarColor + '"></div>' +
                '<div class="kp-forecast-bar-label">' + kpTimeLabel + '</div>' +
                '</div>';
        }
        html += '</div>';
    } else {
        html += '<div class="empty-state">NO Kp FORECAST DATA</div>';
    }
    html += '</div></div>';

    // Electron fluence
    html += '<div class="panel mb-2"><div class="panel-head"><h3>ELECTRON FLUENCE FORECAST</h3></div><div class="panel-body">';
    var eFluence = ((forecasts.electron_fluence || {}).entries || []);
    if (eFluence.length > 0) {
        html += '<table class="env-region-table"><thead><tr>' +
            '<th>DATE</th><th>FLUENCE</th><th>DAY 2</th><th>DAY 3</th><th>SPEED</th>' +
            '</tr></thead><tbody>';
        for (var ei = 0; ei < Math.min(eFluence.length, 10); ei++) {
            var ef = eFluence[ei];
            html += '<tr>' +
                '<td style="color:var(--white)">' + (ef.date || '--') + '</td>' +
                '<td>' + (ef.fluence != null ? ef.fluence.toExponential(2) : '--') + '</td>' +
                '<td>' + (ef.fluence_day2 != null ? ef.fluence_day2.toExponential(2) : '--') + '</td>' +
                '<td>' + (ef.fluence_day3 != null ? ef.fluence_day3.toExponential(2) : '--') + '</td>' +
                '<td>' + (ef.speed != null ? ef.speed : '--') + '</td>' +
                '</tr>';
        }
        html += '</tbody></table>';
    } else {
        html += '<div class="empty-state">NO ELECTRON DATA</div>';
    }
    html += '</div></div>';

    html += '</div>'; // end grid-2
    html += '</div></div>'; // end forecasts section

    // ---- SECTION 6: ENLIL MODEL ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">WSA-ENLIL SOLAR WIND MODEL ' + liveIndicator('1H') + '</div>' +
        '<div class="env-section-body">';

    var cmeCount = enlil.cme_arrivals_detected || 0;
    var cmeArrivals = enlil.cme_arrivals || [];
    var cmeColor = cmeCount > 0 ? 'var(--red)' : 'var(--green)';
    var cmeLabel = cmeCount > 0 ? cmeCount + ' CME DETECTED' : 'NO CME DETECTED';

    html += '<div class="enlil-status-card">' +
        '<div class="enlil-status-val" style="color:' + cmeColor + '">' + cmeCount + '</div>' +
        '<div class="enlil-status-detail">' +
        '<div style="color:' + cmeColor + ';font-size:12px;letter-spacing:1px">' + cmeLabel + '</div>';

    if (cmeArrivals.length > 0) {
        html += '<div style="margin-top:4px">';
        for (var ci = 0; ci < Math.min(cmeArrivals.length, 5); ci++) {
            var ca = cmeArrivals[ci];
            html += '<div style="padding:2px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:9px">' +
                '<span style="color:var(--red)">&#9888;</span> ' +
                '<span style="color:var(--white)">' + (ca.time || '--') + '</span> ' +
                '<span style="color:var(--text-dim)">SPEED: ' + (ca.speed != null ? Math.round(ca.speed) + ' km/s' : '--') + '</span>' +
                '</div>';
        }
        html += '</div>';
    }

    html += '<div style="font-size:8px;color:var(--text-muted);margin-top:4px">MODEL ENTRIES: ' + (enlil.entry_count || 0) + '</div>';
    html += '</div></div>';

    // ENLIL density image if available
    var enlilFrames = (imagery.enlil || {}).frames || [];
    if (enlilFrames.length > 0) {
        html += '<div class="solar-img-panel" style="margin-top:4px">' +
            '<div class="solar-img-label">ENLIL DENSITY MODEL (LATEST FRAME)</div>' +
            '<img src="' + enlilFrames[enlilFrames.length - 1] + '" alt="ENLIL Density" loading="lazy" style="max-height:300px;object-fit:contain">' +
            '</div>';
    }

    if (enlil.intel_note) {
        html += '<div class="intel-summary" style="margin-top:4px">' + enlil.intel_note + '</div>';
    }

    html += '</div></div>'; // end ENLIL section

    // ---- SECTION 7: DEBRIS AWARENESS ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">SPACE DEBRIS AWARENESS ' + liveIndicator('15M') + '</div>' +
        '<div class="env-section-body">';

    html += '<div class="grid-2">';

    // New catalog objects
    var newObj = (debris.new_catalog_objects || {});
    var newObjList = newObj.objects || [];
    html += '<div class="panel mb-2"><div class="panel-head"><h3>NEW CATALOG OBJECTS (30d)</h3><span class="ph-meta">' +
        (newObj.count || 0) + ' OBJECTS</span></div><div class="panel-body" style="max-height:200px">';
    if (newObjList.length > 0) {
        html += '<table class="env-region-table"><thead><tr>' +
            '<th>NORAD</th><th>NAME</th><th>COUNTRY</th><th>TYPE</th><th>INC</th><th>LAUNCH</th>' +
            '</tr></thead><tbody>';
        for (var ni = 0; ni < Math.min(newObjList.length, 20); ni++) {
            var no = newObjList[ni];
            var countryStyle = '';
            if (no.country === 'PRC') countryStyle = 'color:var(--red)';
            else if (no.country === 'CIS') countryStyle = 'color:var(--cis)';
            html += '<tr>' +
                '<td style="color:var(--white)">' + (no.norad_id || '--') + '</td>' +
                '<td>' + (no.name || '--').substring(0, 24) + '</td>' +
                '<td style="' + countryStyle + '">' + (no.country || '--') + '</td>' +
                '<td>' + (no.object_type || '--') + '</td>' +
                '<td>' + (no.inclination != null ? Number(no.inclination).toFixed(1) : '--') + '</td>' +
                '<td>' + (no.launch_date || '--') + '</td>' +
                '</tr>';
        }
        html += '</tbody></table>';
    } else {
        html += '<div class="empty-state">NO NEW OBJECTS</div>';
    }
    html += '</div></div>';

    // ICAO advisories
    var icao = (debris.icao_space_weather || {});
    var icaoList = icao.advisories || [];
    html += '<div class="panel mb-2"><div class="panel-head"><h3>ICAO SPACE WEATHER ADVISORIES</h3><span class="ph-meta">' +
        (icao.count || 0) + ' ADVISORIES</span></div><div class="panel-body" style="max-height:200px">';
    if (icaoList.length > 0) {
        for (var ii = 0; ii < icaoList.length; ii++) {
            var adv = icaoList[ii];
            html += '<div class="debris-obj-row">' +
                '<span class="badge badge-high">' + (adv.severity || 'MOD') + '</span> ' +
                '<span style="color:var(--white);flex:1">' + (adv.effect || '--') + '</span> ' +
                '<span style="color:var(--text-dim);font-size:8px">' + (adv.dtg || '--') + '</span>' +
                '</div>';
        }
    } else {
        html += '<div class="empty-state">NO ACTIVE ADVISORIES</div>';
    }
    html += '</div></div>';

    html += '</div>'; // end grid-2

    // Particle alerts
    var particleAlerts = (debris.particle_environment_alerts || {});
    var pAlertList = particleAlerts.alerts || [];
    if (pAlertList.length > 0) {
        html += '<div class="panel mb-2"><div class="panel-head"><h3>PARTICLE ENVIRONMENT ALERTS</h3><span class="ph-meta" style="color:var(--red)">' +
            pAlertList.length + ' ALERTS</span></div><div class="panel-body" style="max-height:150px">';
        for (var pai = 0; pai < Math.min(pAlertList.length, 5); pai++) {
            var pa = pAlertList[pai];
            html += '<div style="padding:3px 0;border-bottom:1px solid rgba(255,32,32,0.06);font-size:9px;color:var(--text)">' +
                '<span style="color:var(--amber);font-size:7px;letter-spacing:1px">' + (pa.issue_datetime || '--') + '</span><br>' +
                (pa.message || '').substring(0, 200) +
                '</div>';
        }
        html += '</div></div>';
    }

    if (debris.intel_note) {
        html += '<div class="intel-summary">' + debris.intel_note + '</div>';
    }

    html += '</div></div>'; // end debris section

    // ---- SECTION 8: GLOBAL ENVIRONMENT FEEDS (ionosphere, DSCOVR, radiation, seismic) ----
    html += '<div class="env-section">' +
        '<div class="env-section-head">GLOBAL ENVIRONMENT FEEDS ' + liveIndicator('120S') + '</div>' +
        '<div class="env-section-body">' +
        '<div class="grid-2" id="env-global-feeds">' +
            '<div class="panel mb-2" id="env-ionosphere-panel">' +
                '<div class="panel-head"><h3>IONOSPHERE TEC</h3></div>' +
                '<div class="panel-body" id="env-ionosphere-body"><div class="loading">LOADING</div></div>' +
            '</div>' +
            '<div class="panel mb-2" id="env-dscovr-panel">' +
                '<div class="panel-head"><h3>DSCOVR L1 DATA</h3></div>' +
                '<div class="panel-body" id="env-dscovr-body"><div class="loading">LOADING</div></div>' +
            '</div>' +
            '<div class="panel mb-2" id="env-radiation-panel">' +
                '<div class="panel-head"><h3>RADIATION BELT</h3></div>' +
                '<div class="panel-body" id="env-radiation-body"><div class="loading">LOADING</div></div>' +
            '</div>' +
            '<div class="panel mb-2" id="env-seismic-panel">' +
                '<div class="panel-head"><h3>SEISMIC EVENTS NEAR TEST SITES</h3></div>' +
                '<div class="panel-body" id="env-seismic-body"><div class="loading">LOADING</div></div>' +
            '</div>' +
        '</div>' +
        '</div></div>';

    // ---- TIMESTAMP ----
    html += '<div style="text-align:center;padding:6px;font-size:8px;letter-spacing:2px;color:var(--text-muted)">' +
        '<span class="live-indicator"><span class="live-dot"></span> LIVE</span> ENVIRONMENT DATA COMPOSITE // UPDATED <span id="env-live-ts">' + zuluFull() + '</span> // AUTO-REFRESH 60S' +
        '</div>';

    html += '</div>'; // end page-wrap

    el.innerHTML = html;

    // ---- Fetch global feeds for ionosphere, DSCOVR, radiation, seismic ----
    Promise.all([
        api('/api/global/ionosphere'),
        api('/api/global/dscovr'),
        api('/api/global/radiation'),
        api('/api/sigint/seismic'),
    ]).then(function(globalResults) {
        var ionoData = globalResults[0];
        var dscovrData = globalResults[1];
        var radData = globalResults[2];
        var seismicData = globalResults[3];

        // Ionosphere TEC
        var ionoBody = document.getElementById('env-ionosphere-body');
        if (ionoBody) {
            if (!ionoData) {
                ionoBody.innerHTML = '<div class="empty-state">IONOSPHERE DATA UNAVAILABLE</div>';
            } else {
                var iHtml = '';
                if (typeof ionoData === 'string') {
                    iHtml = '<div style="font-size:10px;color:var(--text);line-height:1.5">' + ionoData + '</div>';
                } else {
                    if (ionoData.tec_map_url || ionoData.image_url) {
                        iHtml += '<img src="' + (ionoData.tec_map_url || ionoData.image_url) + '" alt="TEC Map" loading="lazy" style="width:100%;max-height:200px;object-fit:contain;margin-bottom:4px">';
                    }
                    if (ionoData.global_tec != null || ionoData.tec != null) {
                        iHtml += '<div style="font-size:14px;color:var(--cyan)">' + (ionoData.global_tec || ionoData.tec || '--') + ' <span style="font-size:9px;color:var(--text-muted)">TECU</span></div>';
                    }
                    if (ionoData.assessment || ionoData.summary) {
                        iHtml += '<div style="font-size:10px;color:var(--text);line-height:1.5;margin-top:4px">' + (ionoData.assessment || ionoData.summary) + '</div>';
                    }
                    if (ionoData.intel_note) iHtml += '<div class="intel-summary" style="margin-top:4px">' + ionoData.intel_note + '</div>';
                    if (!iHtml) iHtml = '<div style="font-size:9px;color:var(--text);white-space:pre-wrap">' + JSON.stringify(ionoData, null, 2).substring(0, 500) + '</div>';
                }
                ionoBody.innerHTML = iHtml;
            }
        }

        // DSCOVR
        var dscovrBody = document.getElementById('env-dscovr-body');
        if (dscovrBody) {
            if (!dscovrData) {
                dscovrBody.innerHTML = '<div class="empty-state">DSCOVR DATA UNAVAILABLE</div>';
            } else {
                var dHtml = '';
                if (typeof dscovrData === 'string') {
                    dHtml = '<div style="font-size:10px;color:var(--text);line-height:1.5">' + dscovrData + '</div>';
                } else {
                    var dLatest = dscovrData.latest || dscovrData;
                    if (dLatest.speed != null) dHtml += '<div style="padding:2px 0;font-size:10px">SPEED: <span style="color:var(--cyan)">' + Math.round(dLatest.speed) + ' km/s</span></div>';
                    if (dLatest.density != null) dHtml += '<div style="padding:2px 0;font-size:10px">DENSITY: <span style="color:var(--amber)">' + dLatest.density.toFixed(1) + ' p/cm3</span></div>';
                    if (dLatest.bz != null) dHtml += '<div style="padding:2px 0;font-size:10px">Bz: <span style="color:' + (dLatest.bz < 0 ? 'var(--red)' : 'var(--green)') + '">' + dLatest.bz.toFixed(1) + ' nT</span></div>';
                    if (dLatest.bt != null) dHtml += '<div style="padding:2px 0;font-size:10px">Bt: <span style="color:var(--text)">' + dLatest.bt.toFixed(1) + ' nT</span></div>';
                    if (dLatest.temperature != null) dHtml += '<div style="padding:2px 0;font-size:10px">TEMP: <span style="color:var(--text)">' + Math.round(dLatest.temperature).toLocaleString() + ' K</span></div>';
                    if (dscovrData.intel_note) dHtml += '<div class="intel-summary" style="margin-top:4px">' + dscovrData.intel_note + '</div>';
                    if (!dHtml) dHtml = '<div style="font-size:9px;color:var(--text);white-space:pre-wrap">' + JSON.stringify(dscovrData, null, 2).substring(0, 500) + '</div>';
                }
                dscovrBody.innerHTML = dHtml;
            }
        }

        // Radiation Belt
        var radBody = document.getElementById('env-radiation-body');
        if (radBody) {
            if (!radData) {
                radBody.innerHTML = '<div class="empty-state">RADIATION DATA UNAVAILABLE</div>';
            } else {
                var rHtml = '';
                if (typeof radData === 'string') {
                    rHtml = '<div style="font-size:10px;color:var(--text);line-height:1.5">' + radData + '</div>';
                } else {
                    if (radData.belt_status || radData.status) rHtml += '<div style="font-size:12px;color:var(--amber);margin-bottom:4px">STATUS: ' + (radData.belt_status || radData.status).toUpperCase() + '</div>';
                    if (radData.electron_flux != null) rHtml += '<div style="padding:2px 0;font-size:10px">ELECTRON FLUX: <span style="color:var(--cyan)">' + radData.electron_flux + '</span></div>';
                    if (radData.proton_flux != null) rHtml += '<div style="padding:2px 0;font-size:10px">PROTON FLUX: <span style="color:var(--red)">' + radData.proton_flux + '</span></div>';
                    if (radData.assessment || radData.summary) rHtml += '<div style="font-size:10px;color:var(--text);line-height:1.5;margin-top:4px">' + (radData.assessment || radData.summary) + '</div>';
                    if (radData.intel_note) rHtml += '<div class="intel-summary" style="margin-top:4px">' + radData.intel_note + '</div>';
                    if (!rHtml) rHtml = '<div style="font-size:9px;color:var(--text);white-space:pre-wrap">' + JSON.stringify(radData, null, 2).substring(0, 500) + '</div>';
                }
                radBody.innerHTML = rHtml;
            }
        }

        // Seismic Events
        var seismicBody = document.getElementById('env-seismic-body');
        if (seismicBody) {
            if (!seismicData) {
                seismicBody.innerHTML = '<div class="empty-state">SEISMIC DATA UNAVAILABLE</div>';
            } else {
                var sHtml = '';
                var sArr = Array.isArray(seismicData) ? seismicData : (seismicData.events || seismicData.earthquakes || []);
                if (!Array.isArray(sArr)) sArr = [];
                if (sArr.length === 0 && typeof seismicData === 'object' && !Array.isArray(seismicData)) {
                    if (seismicData.assessment || seismicData.summary) {
                        sHtml = '<div style="font-size:10px;color:var(--text);line-height:1.5">' + (seismicData.assessment || seismicData.summary) + '</div>';
                    } else {
                        sHtml = '<div style="font-size:9px;color:var(--text);white-space:pre-wrap">' + JSON.stringify(seismicData, null, 2).substring(0, 500) + '</div>';
                    }
                } else {
                    sArr.slice(0, 10).forEach(function(ev) {
                        var mag = ev.magnitude || ev.mag || '?';
                        var magColor = parseFloat(mag) >= 5 ? 'var(--red)' : parseFloat(mag) >= 3 ? 'var(--cis)' : 'var(--amber)';
                        sHtml += '<div style="padding:3px 0;border-bottom:1px solid rgba(255,176,0,0.04);font-size:10px">' +
                            '<span style="color:' + magColor + ';font-size:12px;font-weight:normal">M' + mag + '</span> ' +
                            '<span style="color:var(--white)">' + (ev.location || ev.place || ev.title || '?') + '</span>' +
                            '<div style="font-size:8px;color:var(--text-muted)">' + (ev.time || ev.date || '') + (ev.depth ? ' // DEPTH: ' + ev.depth + ' km' : '') + '</div>' +
                            '</div>';
                    });
                }
                if (seismicData.intel_note) sHtml += '<div class="intel-summary" style="margin-top:4px">' + seismicData.intel_note + '</div>';
                seismicBody.innerHTML = sHtml || '<div class="empty-state">NO SEISMIC EVENTS DETECTED</div>';
            }
        }
    });

    // ---- AUTO-REFRESH: Targeted status strip update every 60s ----
    registerInterval(async function() {
        var freshEnv = await api('/api/environment/enhanced');
        if (!freshEnv) return;

        var freshGoes = freshEnv.goes_instruments || {};
        var freshAurora = freshEnv.aurora || {};
        var freshGeospace = freshEnv.geospace || {};
        var freshForecasts = freshEnv.forecasts || {};

        // Update X-ray status cell
        var freshXrayData = freshGoes.xray || {};
        var freshXrayLatest = freshXrayData.latest || {};
        var freshXrayKeys = Object.keys(freshXrayLatest);
        if (freshXrayKeys.length > 0) {
            var freshFirstXray = freshXrayLatest[freshXrayKeys[0]];
            var freshFlux = freshFirstXray ? freshFirstXray.flux : null;
            if (freshFlux != null) {
                var freshXLevel = 'A';
                var freshXColor = 'var(--green)';
                if (freshFlux >= 1e-4) { freshXLevel = 'X'; freshXColor = 'var(--red)'; }
                else if (freshFlux >= 1e-5) { freshXLevel = 'M'; freshXColor = 'var(--cis)'; }
                else if (freshFlux >= 1e-6) { freshXLevel = 'C'; freshXColor = 'var(--amber)'; }
                else if (freshFlux >= 1e-7) { freshXLevel = 'B'; freshXColor = 'var(--green)'; }
                freshXLevel += ' (' + freshFlux.toExponential(1) + ')';
                var statusVals = el.querySelectorAll('.env-status-val');
                if (statusVals.length >= 1) {
                    statusVals[0].textContent = freshXLevel;
                    statusVals[0].style.color = freshXColor;
                }
            }
        }

        // Update proton status cell
        var freshProtonData = freshGoes.protons || {};
        var freshProtonLatest = freshProtonData.latest || {};
        var freshProtonKeys = Object.keys(freshProtonLatest);
        var freshProtonAlert = 'NOMINAL';
        var freshProtonColor = 'var(--green)';
        for (var fpi = 0; fpi < freshProtonKeys.length; fpi++) {
            if (freshProtonKeys[fpi].indexOf('10') >= 0) {
                var fpFlux = freshProtonLatest[freshProtonKeys[fpi]] ? freshProtonLatest[freshProtonKeys[fpi]].flux : null;
                if (fpFlux != null && fpFlux >= 10) {
                    freshProtonAlert = 'S1+ STORM';
                    freshProtonColor = 'var(--red)';
                }
                break;
            }
        }
        var statusVals2 = el.querySelectorAll('.env-status-val');
        if (statusVals2.length >= 2) {
            statusVals2[1].textContent = freshProtonAlert;
            statusVals2[1].style.color = freshProtonColor;
        }

        // Update Kp forecast cell
        var freshKpEntries = (freshForecasts.kp_forecast || {}).entries || [];
        if (freshKpEntries.length > 0 && statusVals2.length >= 3) {
            var freshKpVal = freshKpEntries[0].kp;
            var freshKpColor = 'var(--green)';
            if (parseFloat(freshKpVal) >= 7) freshKpColor = 'var(--red)';
            else if (parseFloat(freshKpVal) >= 5) freshKpColor = 'var(--cis)';
            else if (parseFloat(freshKpVal) >= 4) freshKpColor = 'var(--amber)';
            statusVals2[2].textContent = 'Kp ' + String(freshKpVal);
            statusVals2[2].style.color = freshKpColor;
        }

        // Update Bz cell
        var freshGeoLatest = freshGeospace.latest || {};
        if (freshGeoLatest.bz != null && statusVals2.length >= 4) {
            var freshBz = freshGeoLatest.bz;
            var freshBzColor = freshBz < -10 ? 'var(--red)' : freshBz < 0 ? 'var(--cis)' : 'var(--green)';
            statusVals2[3].textContent = freshBz.toFixed(1) + ' nT';
            statusVals2[3].style.color = freshBzColor;
        }

        // Update solar wind cell
        if (freshGeoLatest.speed != null && statusVals2.length >= 5) {
            var freshWindColor = freshGeoLatest.speed > 700 ? 'var(--red)' : freshGeoLatest.speed > 500 ? 'var(--cis)' : 'var(--cyan)';
            statusVals2[4].textContent = Math.round(freshGeoLatest.speed) + ' km/s';
            statusVals2[4].style.color = freshWindColor;
        }

        // Update aurora cell
        if (freshAurora.max_probability != null && statusVals2.length >= 6) {
            var freshAuroraColor = freshAurora.max_probability >= 50 ? 'var(--red)' : freshAurora.max_probability >= 25 ? 'var(--amber)' : 'var(--green)';
            statusVals2[5].textContent = freshAurora.max_probability + '%';
            statusVals2[5].style.color = freshAuroraColor;
        }

        // Update timestamp
        var envTsEl = document.getElementById('env-live-ts');
        if (envTsEl) envTsEl.textContent = zuluFull();
    }, 60000);
};

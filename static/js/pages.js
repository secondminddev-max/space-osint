/* ============================================================
   FVEY SDA — Page Renderers
   Combined Space Operations Center Display
   ============================================================ */

const Pages = {};

// ---- Helpers ----
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
    if (dd > 0) return `T-${dd}D ${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
    return `T-${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}

function badge(level) {
    return `<span class="badge badge-${level}">${level.toUpperCase()}</span>`;
}

function countryBadge(c) {
    const map = { PRC: 'prc', CIS: 'cis', NKOR: 'nkor', IRAN: 'iran', US: 'fvey', UK: 'fvey', CA: 'fvey', AU: 'fvey', NZ: 'fvey' };
    const names = { PRC: 'PRC', CIS: 'RUS', NKOR: 'DPRK', IRAN: 'IRAN', US: 'US', UK: 'UK', CA: 'CA', AU: 'AU', NZ: 'NZ' };
    return `<span class="badge badge-${map[c] || 'fvey'}">${names[c] || c}</span>`;
}

function countryColor(c) {
    return { PRC: '#FF2020', CIS: '#FF8C00', NKOR: '#C040FF', IRAN: '#FFD700', US: '#2080FF', UK: '#2080FF' }[c] || '#888';
}

function zulu() {
    return new Date().toISOString().substring(11, 19) + 'Z';
}

async function api(url) {
    try { const r = await fetch(url); return r.ok ? await r.json() : null; } catch { return null; }
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


/* ================================================================
   PAGE: COMMAND OVERVIEW (CMD)
   Main warfighting display
   ================================================================ */
Pages.cmd = async function(el) {
    el.innerHTML = `
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
            <div class="tb-cell alert">
                <div class="tb-icon">&#9888;</div>
                <div><div class="tb-val" id="ov-asat-ct">7</div><div class="tb-lbl">CRITICAL ASAT</div></div>
            </div>
            <div class="tb-cell alert">
                <div class="tb-icon">&#9650;</div>
                <div><div class="tb-val" id="ov-adv-lx">--</div><div class="tb-lbl">ADV LAUNCHES</div></div>
            </div>
            <div class="tb-cell info">
                <div class="tb-icon">&#9673;</div>
                <div><div class="tb-val" id="ov-isr-ct">--</div><div class="tb-lbl">HOSTILE ISR</div></div>
            </div>
            <div class="tb-cell info">
                <div class="tb-icon">&#9678;</div>
                <div><div class="tb-val" id="ov-total">--</div><div class="tb-lbl">TOTAL TRACKED</div></div>
            </div>
        </div>

        <!-- MAP + OVERLAY PANELS -->
        <div class="cmd-layout">
            <div class="cmd-map-wrap">
                <div id="sat-map" class="map-container"></div>
                <div class="map-legend">
                    <div class="legend-item"><span class="legend-dot" style="background:#FF2020"></span> PRC</div>
                    <div class="legend-item"><span class="legend-dot" style="background:#FF8C00"></span> RUS</div>
                    <div class="legend-item"><span class="legend-dot" style="background:#C040FF"></span> DPRK</div>
                    <div class="legend-item"><span class="legend-dot" style="background:#FFD700"></span> IRAN</div>
                    <div class="legend-item"><span class="legend-dot" style="background:rgba(32,128,255,0.4)"></span> FVEY</div>
                    <div class="legend-item" style="color:var(--text-muted)" id="ov-map-ts">--</div>
                </div>
                <div class="map-overlay-panels">
                    <!-- Force Disposition -->
                    <div class="overlay-panel">
                        <div class="op-head">FORCE DISPOSITION</div>
                        <div class="op-body" id="ov-force"></div>
                    </div>
                    <!-- Critical ASAT -->
                    <div class="overlay-panel">
                        <div class="op-head">CRITICAL ASAT THREATS</div>
                        <div class="op-body" id="ov-asat" style="max-height:180px"></div>
                    </div>
                    <!-- Next ADV Launch -->
                    <div class="overlay-panel">
                        <div class="op-head">ADVERSARY LAUNCH ACTIVITY</div>
                        <div class="op-body" id="ov-adv-launches" style="max-height:150px"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- BOTTOM STRIPS -->
        <div class="cmd-bottom-strip">
            <div class="panel">
                <div class="panel-head"><h3>FVEY VULNERABILITIES</h3><span class="ph-meta"><span class="badge badge-critical">ASSESS</span></span></div>
                <div class="panel-body" style="max-height:160px" id="ov-vulns"></div>
            </div>
            <div class="panel">
                <div class="panel-head"><h3>KEY CONCERNS</h3></div>
                <div class="panel-body" style="max-height:160px" id="ov-concerns"></div>
            </div>
            <div class="panel">
                <div class="panel-head"><h3>OSINT FEED</h3><span class="ph-meta" id="ov-news-ts">--</span></div>
                <div class="panel-body" style="max-height:160px" id="ov-news"></div>
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
        </div>
    `;

    // Init map
    setTimeout(() => { if (typeof initSatMap === 'function') initSatMap('sat-map'); }, 50);

    // Fetch all data
    const [advStats, launches, weather, neo, news, criticalSystems, vulns, threatOv, stats] = await Promise.all([
        api('/api/adversary/stats'),
        api('/api/launches'),
        api('/api/weather'),
        api('/api/neo'),
        api('/api/news'),
        api('/api/missile-asat?threat=critical'),
        api('/api/threat/vulnerabilities'),
        api('/api/threat/overview'),
        api('/api/satellites/stats'),
    ]);

    // --- Threat bar metrics ---
    if (advStats) {
        const prc = advStats.PRC || {};
        const cis = advStats.CIS || {};
        document.getElementById('ov-prc').textContent = prc.total || 0;
        document.getElementById('ov-rus').textContent = cis.total || 0;
        document.getElementById('ov-isr-ct').textContent = (prc.military_isr || 0) + (cis.military_isr || 0);
    }
    if (stats) document.getElementById('ov-total').textContent = (stats.total_tracked || 0).toLocaleString();
    if (criticalSystems) document.getElementById('ov-asat-ct').textContent = criticalSystems.length;

    // Adversary launches
    const advProviders = ['CASC', 'China', 'Roscosmos', 'Russia', 'IRGC', 'Iran', 'DPRK', 'Korea', 'Khrunichev', 'Progress', 'ExPace', 'CASIC', 'Galactic Energy', 'LandSpace', 'iSpace', 'CAS Space', 'Orienspace', 'Space Pioneer'];
    let advLaunches = [];
    if (launches) {
        advLaunches = launches.filter(l => advProviders.some(p => (l.provider || '').includes(p) || (l.name || '').includes(p)));
        document.getElementById('ov-adv-lx').textContent = advLaunches.length;
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
            return `
                <div class="fd-row">
                    <span class="fd-nation" style="color:${n.color}">${n.name}</span>
                    <div class="fd-bar-wrap"><div class="fd-bar" style="width:${Math.min(total/barMax*100,100)}%;background:${n.color}"></div></div>
                    <span class="fd-count">${total}</span>
                </div>`;
        }).join('');
    }

    // --- Critical ASAT ---
    if (criticalSystems) {
        document.getElementById('ov-asat').innerHTML = criticalSystems.map(s => `
            <div class="asat-item">
                <div class="asat-name"><span class="badge badge-critical">CRIT</span> ${s.name}</div>
                <div class="asat-meta">${s.country} | ${(s.type||'').replace(/_/g,' ')} ${s.max_altitude_km ? '| ' + s.max_altitude_km.toLocaleString() + ' KM' : ''}</div>
            </div>
        `).join('');
    }

    // --- Adversary Launches ---
    function renderAdvLaunches() {
        const body = document.getElementById('ov-adv-launches');
        if (!body) return;
        if (!advLaunches.length) { body.innerHTML = '<div class="empty-state">NO ADV LAUNCHES</div>'; return; }
        body.innerHTML = advLaunches.slice(0, 4).map(l => `
            <div class="launch-line ll-adv">
                <div class="ll-name">${l.name}</div>
                <div class="ll-detail">${l.provider} | ${l.pad_location || '?'}</div>
                <div class="ll-countdown">${l.net ? countdown(l.net) : 'TBD'}</div>
            </div>
        `).join('');
    }
    renderAdvLaunches();
    registerInterval(renderAdvLaunches, 1000);

    // --- Vulnerabilities ---
    if (vulns) {
        const sorted = [...vulns].sort((a,b) => {
            const order = {critical:0,high:1,medium:2,low:3};
            return (order[a.severity]||9) - (order[b.severity]||9);
        });
        document.getElementById('ov-vulns').innerHTML = sorted.slice(0, 5).map(v => `
            <div class="vuln-line">
                ${badge(v.severity || 'high')}
                <span style="color:var(--white);font-size:10px">${v.title}</span>
            </div>
        `).join('');
    }

    // --- Key Concerns ---
    if (threatOv && threatOv.key_concerns) {
        document.getElementById('ov-concerns').innerHTML = threatOv.key_concerns.slice(0, 4).map(c => `
            <div class="vuln-line">
                ${badge(c.severity || 'high')}
                <span style="color:var(--white);font-size:10px">${c.title}</span>
            </div>
        `).join('');
    }

    // --- News ---
    if (news) {
        document.getElementById('ov-news').innerHTML = news.slice(0, 6).map(n => `
            <a href="${n.url}" target="_blank" rel="noopener" class="news-line">
                <span class="nl-title">${n.title}</span>
                <span class="nl-meta">${n.news_site} // ${timeAgo(n.published_at)}</span>
            </a>
        `).join('');
        document.getElementById('ov-news-ts').textContent = zulu();
    }

    // --- Environment Bar ---
    if (weather) {
        if (weather.kp_current != null) {
            const el = document.getElementById('ov-kp');
            el.textContent = weather.kp_current.toFixed(1);
            el.style.color = weather.kp_current < 4 ? 'var(--green)' : weather.kp_current < 6 ? '#FFD700' : 'var(--red)';
        }
        if (weather.solar_wind_speed != null) document.getElementById('ov-wind').textContent = Math.round(weather.solar_wind_speed) + ' KM/S';
        if (weather.bz != null) {
            const el = document.getElementById('ov-bz');
            el.textContent = weather.bz.toFixed(1);
            el.style.color = weather.bz < 0 ? 'var(--red)' : 'var(--green)';
        }
        if (weather.sfi != null) document.getElementById('ov-sfi').textContent = Math.round(weather.sfi);
        if (weather.scales) {
            for (const k of ['R', 'S', 'G']) {
                const v = weather.scales[k]?.Scale || 0;
                const el = document.getElementById('ov-s' + k.toLowerCase());
                if (el) {
                    el.textContent = k + v;
                    el.style.color = v === 0 ? 'var(--green)' : v <= 2 ? '#FFD700' : 'var(--red)';
                }
            }
        }
    }
    if (neo) document.getElementById('ov-neo').textContent = neo.length;

    // --- MAP: Plot adversary sats ---
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
            ...(prcSats || []).map(s => ({...s, _c: '#FF2020', _r: s.category === 'military_isr' ? 3.5 : 2.5})),
            ...(cisSats || []).map(s => ({...s, _c: '#FF8C00', _r: s.category === 'military_isr' ? 3.5 : 2.5})),
            ...(nkorSats || []).map(s => ({...s, _c: '#C040FF', _r: 4})),
            ...(iranSats || []).map(s => ({...s, _c: '#FFD700', _r: 4})),
        ];

        allAdv.forEach(s => {
            if (!s.lat || !s.lng) return;
            const m = L.circleMarker([s.lat, s.lng], {
                radius: s._r, fillColor: s._c, fillOpacity: 0.6,
                color: s._c, weight: 0,
            }).bindPopup(`<div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#e0e8f0;background:#000;padding:6px;min-width:180px">
                <div style="color:${s._c};margin-bottom:3px">${s.name}</div>
                <div>NORAD: ${s.norad_id} | ${s.country}</div>
                <div>MISSION: ${(s.category||'').replace(/_/g,' ').toUpperCase()}</div>
                <div>ALT: ${Math.round(s.alt_km||0)} KM | INC: ${s.inclination?.toFixed(1) || '?'}&deg;</div>
                <div>REGIME: ${s.regime || '?'}</div>
            </div>`, { className: 'sat-popup', closeButton: false }).addTo(satMap);
            satMarkers.push(m);
        });

        // FVEY sats (dim)
        (fveySats || []).forEach(s => {
            if (!s.lat || !s.lng) return;
            const m = L.circleMarker([s.lat, s.lng], {
                radius: s.norad_id === 25544 ? 5 : 1.5,
                fillColor: '#2080FF', fillOpacity: 0.15,
                color: '#2080FF', weight: 0,
            }).addTo(satMap);
            satMarkers.push(m);
        });

        document.getElementById('ov-map-ts').textContent = zulu();
    }, 400);
};


/* ================================================================
   PAGE: ADVERSARY PROFILES
   ================================================================ */
Pages.adversary = async function(el) {
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

    el.innerHTML = `
        <div class="page-wrap">
            <!-- Stats bar -->
            <div class="threat-bar mb-2">
                ${countries.map(c => `
                    <div class="tb-cell" style="border-left:2px solid ${c.color}">
                        <div class="tb-icon" style="color:${c.color}">&#9760;</div>
                        <div><div class="tb-val" style="color:${c.color}">${c.stats?.total || (c.sats?.length||0)}</div><div class="tb-lbl">${c.name}</div></div>
                    </div>
                `).join('')}
                <div class="tb-cell hostile">
                    <div class="tb-icon">&#9673;</div>
                    <div><div class="tb-val">${countries.reduce((a, c) => a + (c.stats?.military_isr || 0), 0)}</div><div class="tb-lbl">TOTAL MIL ISR</div></div>
                </div>
            </div>

            <!-- Country tabs -->
            <div class="country-tabs" id="adv-tabs">
                ${countries.map((c, i) => `<div class="country-tab${i===0?' active':''}" data-country="${c.code}" style="${i===0?'color:'+c.color:''}">${c.name}</div>`).join('')}
            </div>

            <div id="adv-detail"></div>
        </div>
    `;

    function renderCountry(code) {
        const c = countries.find(x => x.code === code);
        if (!c) return;
        const sats = c.sats || [];
        const t = c.threat || {};
        const cats = {};
        sats.forEach(s => { cats[s.category] = (cats[s.category] || 0) + 1; });

        // Update tab colors
        el.querySelectorAll('.country-tab').forEach(tab => {
            const tc = countries.find(x => x.code === tab.dataset.country);
            tab.style.color = tab.classList.contains('active') ? tc.color : '';
        });

        document.getElementById('adv-detail').innerHTML = `
            <div class="grid-2 mb-4">
                <!-- Assessment -->
                <div class="panel">
                    <div class="panel-head"><h3>STRATEGIC ASSESSMENT</h3><span class="ph-meta">${badge((t.overall_threat||'high').toLowerCase())} THREAT</span></div>
                    <div class="panel-body" style="max-height:500px">
                        ${t.trend ? `<div style="font-size:10px;color:var(--red);margin-bottom:6px">TREND: ${t.trend}</div>` : ''}
                        <div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:10px">${t.assessment || t.summary || ''}</div>
                        ${t.doctrine ? `<div class="intel-field"><span class="intel-label">DOCTRINE</span>${t.doctrine}</div>` : ''}
                        ${t.strategic_context ? `<div class="intel-field"><span class="intel-label">STRATEGIC CONTEXT</span>${t.strategic_context}</div>` : ''}
                        ${t.key_capabilities?.length ? `
                            <div class="intel-field"><span class="intel-label">KEY CAPABILITIES</span>
                                <ul style="margin:3px 0 0 14px;color:var(--text)">${t.key_capabilities.map(k => `<li style="margin-bottom:2px;font-size:10px">${k}</li>`).join('')}</ul>
                            </div>
                        ` : ''}
                        ${t.intelligence_gaps?.length ? `
                            <div class="intel-field"><span class="intel-label" style="color:var(--cis)">INTELLIGENCE GAPS</span>
                                <ul style="margin:3px 0 0 14px;color:var(--text)">${t.intelligence_gaps.map(g => `<li style="margin-bottom:2px;font-size:10px">${g}</li>`).join('')}</ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <!-- Order of Battle -->
                <div class="panel">
                    <div class="panel-head"><h3>ORBITAL ORDER OF BATTLE</h3></div>
                    <div class="panel-body">
                        <div style="font-size:24px;color:${c.color};margin-bottom:10px">${sats.length} <span style="font-size:10px;color:var(--text-dim)">ACTIVE SATELLITES</span></div>
                        ${Object.entries(cats).sort((a,b) => b[1]-a[1]).map(([cat, count]) => {
                            const pct = Math.round(count / sats.length * 100);
                            return `
                            <div class="orbat-row">
                                <span class="orbat-cat">${cat.replace(/_/g,' ').toUpperCase()}</span>
                                <div class="orbat-bar-wrap"><div class="orbat-bar" style="width:${pct}%;background:${c.color}"></div></div>
                                <span class="orbat-count" style="color:${c.color}">${count}</span>
                            </div>`;
                        }).join('')}
                    </div>
                </div>
            </div>
            <!-- Satellite Catalog -->
            <div class="panel">
                <div class="panel-head"><h3>${c.name} SATELLITE CATALOG</h3><span class="ph-meta">${sats.length} OBJECTS</span></div>
                <div class="panel-body" style="max-height:400px">
                    <table class="data-table"><thead><tr>
                        <th>DESIGNATION</th><th>NORAD</th><th>MISSION</th><th>REGIME</th><th>ALT KM</th><th>INC</th>
                    </tr></thead><tbody>
                    ${sats.slice(0, 150).map(s => `<tr>
                        <td style="color:${c.color}">${s.name || '?'}</td>
                        <td>${s.norad_id || '?'}</td>
                        <td>${badge(s.category === 'military_isr' ? 'critical' : s.category === 'sda_asat' ? 'high' : 'medium')} ${(s.category||'').replace(/_/g,' ')}</td>
                        <td>${s.regime || '?'}</td>
                        <td>${s.alt_km ? Math.round(s.alt_km) : '?'}</td>
                        <td>${s.inclination ? s.inclination.toFixed(1) + '\u00B0' : '?'}</td>
                    </tr>`).join('')}
                    </tbody></table>
                </div>
            </div>
        `;
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
   PAGE: ORBITAL THREATS
   ================================================================ */
Pages.orbital = async function(el) {
    el.innerHTML = '<div class="loading">MAPPING ORBITAL THREATS</div>';

    const [prc, cis, nkor, iran] = await Promise.all([
        api('/api/adversary/satellites?country=PRC'),
        api('/api/adversary/satellites?country=CIS'),
        api('/api/adversary/satellites?country=NKOR'),
        api('/api/adversary/satellites?country=IRAN'),
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

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">${allAdv.length}</div><div class="tb-lbl">TOTAL HOSTILE</div></div></div>
                <div class="tb-cell hostile"><div class="tb-icon">&#9673;</div><div><div class="tb-val">${milISR.length}</div><div class="tb-lbl">ISR / RECON</div></div></div>
                <div class="tb-cell alert"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${sda.length}</div><div class="tb-lbl">SDA / ASAT</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${nav.length}</div><div class="tb-lbl">PNT / NAV</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9656;</div><div><div class="tb-val">${comms.length}</div><div class="tb-lbl">COMMS</div></div></div>
            </div>
            <div class="panel mb-2">
                <div class="panel-head"><h3>ADVERSARY ORBITAL ASSETS // GLOBAL VIEW</h3><span class="ph-meta">${zulu()}</span></div>
                <div class="panel-body" style="padding:0"><div id="orbital-map" class="map-container" style="min-height:420px"></div></div>
            </div>
            <div class="grid-2 mb-2">
                <div class="panel">
                    <div class="panel-head"><h3>HOSTILE ISR / RECONNAISSANCE</h3><span class="ph-meta">${milISR.length} TRACKED</span></div>
                    <div class="panel-body" style="max-height:300px">
                        <table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>INC</th><th>REGIME</th></tr></thead><tbody>
                        ${milISR.slice(0, 80).map(s => `<tr>
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
                    <div class="panel-body" style="max-height:300px">
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
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-head"><h3>NAVIGATION / PNT</h3><span class="ph-meta">${nav.length}</span></div>
                    <div class="panel-body" style="max-height:250px">
                        <table class="data-table"><thead><tr><th>DESIGNATION</th><th>NATION</th><th>ALT</th><th>REGIME</th></tr></thead><tbody>
                        ${nav.slice(0,60).map(s => `<tr>
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
                        ${comms.slice(0,60).map(s => `<tr>
                            <td style="color:${countryColor(s._nation)}">${s.name}</td>
                            <td>${countryBadge(s._nation)}</td>
                            <td>${s.alt_km ? Math.round(s.alt_km) + ' KM' : '?'}</td>
                            <td>${s.regime || '?'}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => {
        const omap = L.map('orbital-map', { center: [20, 0], zoom: 2, minZoom: 2, maxZoom: 8, attributionControl: false });
        L.tileLayer('https://{s}.basemaps-cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { subdomains: 'abcd' }).addTo(omap);
        addGridOverlay(omap);
        storeMap(omap);
        allAdv.forEach(s => {
            if (!s.lat || !s.lng) return;
            const col = countryColor(s._nation);
            const r = s.category === 'sda_asat' ? 5 : s.category === 'military_isr' ? 3.5 : 2.5;
            L.circleMarker([s.lat, s.lng], {
                radius: r, fillColor: col, fillOpacity: 0.55,
                color: col, weight: s.category === 'sda_asat' ? 1.5 : 0, opacity: 0.3
            }).bindPopup(`<div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#e0e8f0;background:#000;padding:6px"><div style="color:${col}">${s.name}</div><div>${s._nation} | ${(s.category||'').replace(/_/g,' ')} | ${Math.round(s.alt_km||0)} KM</div></div>`, { className: 'sat-popup', closeButton: false }).addTo(omap);
        });
    }, 150);
};


/* ================================================================
   PAGE: LAUNCH MONITOR
   ================================================================ */
Pages.launches = async function(el) {
    el.innerHTML = '<div class="loading">LOADING LAUNCH INTELLIGENCE</div>';
    const data = await api('/api/launches');
    if (!data) { el.innerHTML = '<div class="empty-state">LAUNCH DATA UNAVAILABLE</div>'; return; }

    const advProviders = ['CASC', 'China', 'Roscosmos', 'Russia', 'IRGC', 'Iran', 'DPRK', 'Korea', 'Khrunichev', 'Progress', 'ExPace', 'CASIC', 'Galactic Energy', 'LandSpace', 'iSpace', 'CAS Space', 'Orienspace', 'Space Pioneer'];
    data.forEach(l => { l._isAdv = advProviders.some(p => (l.provider || '').includes(p) || (l.name || '').includes(p)); });
    const advCount = data.filter(l => l._isAdv).length;

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9760;</div><div><div class="tb-val">${advCount}</div><div class="tb-lbl">ADVERSARY</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9650;</div><div><div class="tb-val">${data.length - advCount}</div><div class="tb-lbl">ALLIED / OTHER</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${data.length}</div><div class="tb-lbl">TOTAL UPCOMING</div></div></div>
            </div>
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-head"><h3>ADVERSARY LAUNCHES</h3><span class="ph-meta"><span class="badge badge-critical">${advCount} SCHEDULED</span></span></div>
                    <div class="panel-body" id="launch-adv" style="max-height:calc(100vh - 200px)"></div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>ALL GLOBAL LAUNCHES</h3><span class="ph-meta">${data.length} TOTAL</span></div>
                    <div class="panel-body" id="launch-all" style="max-height:calc(100vh - 200px)"></div>
                </div>
            </div>
        </div>
    `;

    function renderList(container, launches) {
        if (!container) return;
        container.innerHTML = launches.map(l => `
            <div class="launch-line ${l._isAdv ? 'll-adv' : ''}">
                <div class="ll-name">${l._isAdv ? '&#9760; ' : ''}${l.name}</div>
                <div class="ll-detail">${l.provider || '?'} | ${l.rocket || '?'} | ${l.pad_location || '?'}</div>
                <div class="ll-countdown">${l.net ? countdown(l.net) : 'TBD'}</div>
            </div>
        `).join('') || '<div class="empty-state">NONE</div>';
    }

    renderList(document.getElementById('launch-adv'), data.filter(l => l._isAdv));
    renderList(document.getElementById('launch-all'), data);

    registerInterval(() => {
        renderList(document.getElementById('launch-adv'), data.filter(l => l._isAdv));
        renderList(document.getElementById('launch-all'), data);
    }, 1000);
};


/* ================================================================
   PAGE: GROUND STATIONS
   ================================================================ */
Pages.ground = async function(el) {
    el.innerHTML = '<div class="loading">MAPPING GROUND INFRASTRUCTURE</div>';
    const stations = await api('/api/ground-stations');
    if (!stations) { el.innerHTML = '<div class="empty-state">DATA UNAVAILABLE</div>'; return; }

    const adversary = stations.filter(s => ['PRC', 'CIS', 'NKOR', 'IRAN'].includes(s.country));
    const fvey = stations.filter(s => ['US', 'UK', 'CA', 'AU', 'NZ'].includes(s.country));

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9873;</div><div><div class="tb-val">${adversary.length}</div><div class="tb-lbl">ADVERSARY FACILITIES</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9733;</div><div><div class="tb-val">${fvey.length}</div><div class="tb-lbl">FVEY FACILITIES</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${stations.length}</div><div class="tb-lbl">TOTAL</div></div></div>
            </div>
            <div class="panel mb-2">
                <div class="panel-head"><h3>GLOBAL GROUND INFRASTRUCTURE</h3><span class="ph-meta">${zulu()}</span></div>
                <div class="panel-body" style="padding:0"><div id="gs-map" class="map-container" style="min-height:420px"></div></div>
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
                            <td style="white-space:normal;max-width:300px;font-size:9px;color:var(--text-dim)">${(s.description||'').substring(0,80)}</td>
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
                            <td style="white-space:normal;max-width:300px;font-size:9px;color:var(--text-dim)">${(s.description||'').substring(0,80)}</td>
                        </tr>`).join('')}
                        </tbody></table>
                    </div>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => {
        const gmap = L.map('gs-map', { center: [25, 60], zoom: 3, minZoom: 2, maxZoom: 10, attributionControl: false });
        L.tileLayer('https://{s}.basemaps-cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { subdomains: 'abcd' }).addTo(gmap);
        addGridOverlay(gmap);
        storeMap(gmap);

        stations.forEach(s => {
            if (!s.lat || !s.lng) return;
            const isAdv = ['PRC', 'CIS', 'NKOR', 'IRAN'].includes(s.country);
            const col = countryColor(s.country) || (isAdv ? '#FF2020' : '#2080FF');
            L.circleMarker([s.lat, s.lng], {
                radius: isAdv ? 6 : 4,
                fillColor: col, fillOpacity: isAdv ? 0.8 : 0.35,
                color: col, weight: isAdv ? 1.5 : 1, opacity: isAdv ? 0.5 : 0.2,
            }).bindPopup(`<div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#e0e8f0;background:#000;padding:6px;max-width:200px"><div style="color:${col}">${s.name}</div><div>${s.country} | ${s.type||'?'}</div><div style="color:var(--text-dim);margin-top:3px;white-space:normal;font-size:9px">${s.description||''}</div></div>`, { className: 'sat-popup', closeButton: false }).addTo(gmap);
        });
    }, 150);
};


/* ================================================================
   PAGE: MISSILE & ASAT
   ================================================================ */
Pages.missile = async function(el) {
    el.innerHTML = '<div class="loading">LOADING COUNTERSPACE INTELLIGENCE</div>';
    const allSystems = await api('/api/missile-asat');
    if (!allSystems) { el.innerHTML = '<div class="empty-state">DATA UNAVAILABLE</div>'; return; }

    const critical = allSystems.filter(s => s.threat_level === 'critical');
    const high = allSystems.filter(s => s.threat_level === 'high');
    const asatCapable = allSystems.filter(s => s.type?.includes('asat') || s.type?.includes('ASAT') || s.type === 'direct_ascent_asat' || s.type === 'co_orbital_asat');

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${critical.length}</div><div class="tb-lbl">CRITICAL</div></div></div>
                <div class="tb-cell warning"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${high.length}</div><div class="tb-lbl">HIGH</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${allSystems.length}</div><div class="tb-lbl">TOTAL SYSTEMS</div></div></div>
                <div class="tb-cell alert"><div class="tb-icon">&#9650;</div><div><div class="tb-val">${asatCapable.length}</div><div class="tb-lbl">ASAT CAPABLE</div></div></div>
            </div>
            <div class="filter-tabs" id="missile-tabs">
                <div class="filter-tab active" data-filter="all">ALL</div>
                <div class="filter-tab" data-filter="PRC" style="color:#FF2020">CHINA</div>
                <div class="filter-tab" data-filter="Russia" style="color:#FF8C00">RUSSIA</div>
                <div class="filter-tab" data-filter="DPRK" style="color:#C040FF">DPRK</div>
                <div class="filter-tab" data-filter="Iran" style="color:#FFD700">IRAN</div>
                <div class="filter-tab" data-filter="critical">CRITICAL ONLY</div>
            </div>
            <div id="missile-detail"></div>
        </div>
    `;

    function renderSystems(filter) {
        let systems = allSystems;
        if (filter === 'critical') systems = allSystems.filter(s => s.threat_level === 'critical');
        else if (filter !== 'all') systems = allSystems.filter(s => s.country === filter);

        document.getElementById('missile-detail').innerHTML = `
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(480px,1fr));gap:4px">
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
                    <div class="tc-meta">
                        TYPE: ${(s.type||'').replace(/_/g,' ').toUpperCase()} // STATUS: ${(s.status||'?').toUpperCase()}
                        ${s.max_altitude_km ? ' // MAX ALT: ' + s.max_altitude_km.toLocaleString() + ' KM' : ''}
                        ${s.first_tested ? ' // FIRST TESTED: ' + s.first_tested : ''}
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
   PAGE: FVEY POSTURE
   ================================================================ */
Pages.fvey = async function(el) {
    el.innerHTML = '<div class="loading">ASSESSING FVEY POSTURE</div>';
    const [vulns, recs] = await Promise.all([
        api('/api/threat/vulnerabilities'),
        api('/api/threat/recommendations'),
    ]);

    const criticalVulns = (vulns||[]).filter(v => v.severity === 'critical');
    const highVulns = (vulns||[]).filter(v => v.severity === 'high');

    el.innerHTML = `
        <div class="page-wrap">
            <div class="threat-bar mb-2">
                <div class="tb-cell hostile"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${criticalVulns.length}</div><div class="tb-lbl">CRITICAL VULNS</div></div></div>
                <div class="tb-cell warning"><div class="tb-icon">&#9888;</div><div><div class="tb-val">${highVulns.length}</div><div class="tb-lbl">HIGH VULNS</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9881;</div><div><div class="tb-val">${(recs||[]).length}</div><div class="tb-lbl">RECOMMENDATIONS</div></div></div>
                <div class="tb-cell info"><div class="tb-icon">&#9678;</div><div><div class="tb-val">${(vulns||[]).length}</div><div class="tb-lbl">TOTAL VULNS</div></div></div>
            </div>
            <div class="grid-2">
                <div class="panel">
                    <div class="panel-head"><h3>FVEY SPACE ARCHITECTURE VULNERABILITIES</h3><span class="ph-meta"><span class="badge badge-critical">ASSESS</span></span></div>
                    <div class="panel-body" style="max-height:calc(100vh - 200px)">
                        ${(vulns||[]).map(v => `
                            <div class="threat-card severity-${v.severity || 'high'}">
                                <div class="tc-header">${badge(v.severity || 'high')} <span class="tc-title">${v.title}</span></div>
                                <div class="tc-body">${v.description}</div>
                                ${v.impact ? `<div class="tc-meta">IMPACT: ${v.impact}</div>` : ''}
                                ${v.mitigation ? `<div class="tc-source" style="color:var(--green)">MITIGATION: ${v.mitigation}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-head"><h3>POLICY RECOMMENDATIONS</h3><span class="ph-meta"><span class="badge badge-low">ADVISE</span></span></div>
                    <div class="panel-body" style="max-height:calc(100vh - 200px)">
                        ${(recs||[]).map(r => `
                            <div class="threat-card severity-${r.priority || 'medium'}" style="border-left-color:var(--green)">
                                <div class="tc-header">${badge(r.priority || 'medium')} <span class="tc-title">${r.title}</span></div>
                                <div class="tc-body">${r.description}</div>
                                <div class="tc-meta">${r.cost_estimate ? 'COST: ' + r.cost_estimate : ''}${r.timeline ? ' // TIMELINE: ' + r.timeline : ''}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
};


/* ================================================================
   PAGE: STRATEGIC ANALYSIS
   ================================================================ */
Pages.strategy = async function(el) {
    el.innerHTML = '<div class="loading">GENERATING STRATEGIC ANALYSIS</div>';
    const [overview, scenarios] = await Promise.all([
        api('/api/threat/overview'),
        api('/api/threat/scenarios'),
    ]);

    const ov = overview || {};
    const level = (ov.overall_threat_level || ov.threat_level || 'HIGH').toUpperCase();

    el.innerHTML = `
        <div class="page-wrap">
            <!-- Threat Overview -->
            <div class="panel mb-4">
                <div class="panel-head">
                    <h3>GLOBAL SPACE DOMAIN THREAT ASSESSMENT</h3>
                    <span class="ph-meta">UNCLASSIFIED // OSINT // ${zulu()}</span>
                </div>
                <div class="panel-body">
                    <div class="threat-overview-head">
                        <span class="toh-level ${level.toLowerCase()}">${level}</span>
                    </div>
                    <div style="font-size:10px;color:var(--text);line-height:1.6;margin-bottom:12px">${ov.summary || ''}</div>
                    ${ov.key_concerns?.length ? `
                        <div class="section-head" style="margin-bottom:4px">KEY CONCERNS</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px">
                        ${ov.key_concerns.map(c => `
                            <div class="threat-card severity-${c.severity || 'high'}">
                                <div class="tc-header">${badge(c.severity || 'high')} <span class="tc-title">${c.title}</span></div>
                                <div class="tc-body">${c.detail || c.description || ''}</div>
                                ${c.evidence ? `<div class="tc-source">EVIDENCE: ${c.evidence}</div>` : ''}
                            </div>
                        `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>

            <!-- Conflict Scenarios -->
            <div class="panel mb-4">
                <div class="panel-head"><h3>CONFLICT ESCALATION SCENARIOS</h3><span class="ph-meta"><span class="badge badge-critical">WARGAME</span></span></div>
                <div class="panel-body">
                    ${(scenarios || []).map(s => `
                        <div class="threat-card severity-${s.severity || 'high'}" style="margin-bottom:6px">
                            <div class="tc-header">${badge(s.severity || s.probability || 'high')} <span class="tc-title">${s.title || s.name}</span></div>
                            ${s.probability ? `<div style="font-size:9px;color:var(--text-dim);margin:3px 0">PROBABILITY: ${s.probability}${s.timeframe ? ' // TIMEFRAME: ' + s.timeframe : ''}</div>` : ''}
                            <div class="tc-body">${s.description || ''}</div>
                            ${s.phases?.length ? `
                                <div style="margin-top:4px;font-size:10px">
                                    <span style="color:var(--cis)">ESCALATION PHASES:</span>
                                    <ol class="phase-list">${s.phases.map(p => `<li>${p}</li>`).join('')}</ol>
                                </div>
                            ` : ''}
                            ${s.fvey_response ? `
                                <div style="margin-top:4px;font-size:10px">
                                    <span style="color:var(--green)">FVEY RESPONSE:</span>
                                    <span style="color:var(--text)">${s.fvey_response}</span>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
};

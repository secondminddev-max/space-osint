/* ============================================================
   FVEY SDA — Satellite Map (Leaflet)
   Military Command Centre Display
   ============================================================ */

let satMap = null;
let satMarkers = [];
let issTrackLine = null;

function initSatMap(elementId) {
    const id = elementId || 'sat-map';
    const el = document.getElementById(id);
    if (!el) return null;

    const map = L.map(id, {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 10,
        zoomControl: true,
        attributionControl: false,
    });

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    addGridOverlay(map);

    if (!elementId || elementId === 'sat-map') {
        satMap = map;
    }

    return map;
}

function addGridOverlay(map) {
    const target = map || satMap;
    if (!target) return;
    const gridStyle = { color: 'rgba(255,176,0,0.04)', weight: 0.5, dashArray: '3 6' };
    for (let lat = -60; lat <= 60; lat += 30) {
        L.polyline([[lat, -180], [lat, 180]], gridStyle).addTo(target);
    }
    for (let lng = -180; lng <= 180; lng += 60) {
        L.polyline([[-90, lng], [90, lng]], gridStyle).addTo(target);
    }
}

function renderSatellites(positions, map) {
    const target = map || satMap;
    if (!target || !positions) return;

    satMarkers.forEach(m => target.removeLayer(m));
    satMarkers = [];

    positions.forEach(sat => {
        const isISS = sat.norad_id === 25544;
        const isCSS = sat.norad_id === 48274;

        let color = '#2080FF';
        let radius = 3;
        let opacity = 0.4;

        if (isISS) { color = '#20FF60'; radius = 7; opacity = 1; }
        else if (isCSS) { color = '#FFD700'; radius = 6; opacity = 1; }
        else if (sat.object_type === 'DEBRIS') { color = '#FF2020'; radius = 1.5; opacity = 0.2; }
        else if (sat.object_type === 'ROCKET BODY') { color = '#FF8C00'; radius = 2; opacity = 0.3; }

        const marker = L.circleMarker([sat.lat, sat.lng], {
            radius, fillColor: color, fillOpacity: opacity,
            color, weight: isISS || isCSS ? 1.5 : 0, opacity: isISS || isCSS ? 0.6 : 0,
        }).addTo(target);

        marker.bindPopup(`
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#e0e8f0;background:#000;padding:6px;min-width:160px;">
                <div style="color:#FFB000;margin-bottom:4px">${sat.name}</div>
                <div>NORAD: ${sat.norad_id}</div>
                <div>ALT: ${(sat.alt_km || 0).toFixed(0)} KM</div>
                <div>INC: ${(sat.inclination || 0).toFixed(1)}&deg;</div>
                <div>LAT: ${sat.lat.toFixed(2)}&deg; LNG: ${sat.lng.toFixed(2)}&deg;</div>
            </div>
        `, { className: 'sat-popup', closeButton: false });

        satMarkers.push(marker);
    });

    fetchISSTrack(target);
}

async function fetchISSTrack(map) {
    const target = map || satMap;
    if (!target) return;
    try {
        const r = await fetch('/api/satellites/track/25544');
        const track = await r.json();
        if (!track || !track.length) return;

        if (issTrackLine) target.removeLayer(issTrackLine);

        const latlngs = track.map(p => [p.lat, p.lng]);
        const segments = [];
        let current = [latlngs[0]];
        for (let i = 1; i < latlngs.length; i++) {
            if (Math.abs(latlngs[i][1] - latlngs[i - 1][1]) > 180) {
                segments.push(current);
                current = [];
            }
            current.push(latlngs[i]);
        }
        segments.push(current);

        issTrackLine = L.layerGroup();
        segments.forEach(seg => {
            if (seg.length > 1) {
                L.polyline(seg, {
                    color: '#20FF60', weight: 1, opacity: 0.3, dashArray: '4 6',
                }).addTo(issTrackLine);
            }
        });
        issTrackLine.addTo(target);
    } catch (e) {
        console.warn('[SDA] ISS track unavailable:', e);
    }
}

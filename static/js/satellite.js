/* ============================================================
   Space OSINT — Satellite Map (Leaflet)
   ============================================================ */

let satMap = null;
let satMarkers = [];
let issTrackLine = null;
let issMarker = null;

function initSatMap() {
    satMap = L.map('sat-map', {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 10,
        zoomControl: true,
        attributionControl: false,
    });

    // Dark tile layer (CartoDB Dark Matter — free, no key)
    L.tileLayer('https://{s}.basemaps-cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd',
        maxZoom: 19,
    }).addTo(satMap);

    // Terminator (day/night line) — simple equator marker
    // Grid overlay
    addGridOverlay();
}

function addGridOverlay() {
    // Subtle lat/lng grid lines
    const gridStyle = { color: 'rgba(0,200,255,0.06)', weight: 0.5, dashArray: '4 4' };

    for (let lat = -60; lat <= 60; lat += 30) {
        L.polyline([[-90, lat === 0 ? -180 : -180], [90, lat === 0 ? -180 : -180]].map(() =>
            [[lat, -180], [lat, 180]]
        )[0], gridStyle).addTo(satMap);
    }
    for (let lng = -180; lng <= 180; lng += 60) {
        L.polyline([[-90, lng], [90, lng]], gridStyle).addTo(satMap);
    }
}

function updateSatellites(positions) {
    if (!satMap) return;

    // Clear old markers
    satMarkers.forEach(m => satMap.removeLayer(m));
    satMarkers = [];

    if (!positions || !positions.length) return;

    positions.forEach(sat => {
        const isISS = sat.norad_id === 25544;
        const isCSS = sat.norad_id === 48274;

        let color = '#00c8ff';  // default cyan
        let radius = 4;
        let opacity = 0.7;

        if (isISS) {
            color = '#00ff88';
            radius = 8;
            opacity = 1;
        } else if (isCSS) {
            color = '#ffd700';
            radius = 7;
            opacity = 1;
        } else if (sat.object_type === 'DEBRIS') {
            color = '#ff3355';
            radius = 2;
            opacity = 0.3;
        } else if (sat.object_type === 'ROCKET BODY') {
            color = '#ff8c00';
            radius = 3;
            opacity = 0.4;
        }

        const marker = L.circleMarker([sat.lat, sat.lng], {
            radius: radius,
            fillColor: color,
            fillOpacity: opacity,
            color: color,
            weight: isISS || isCSS ? 2 : 0,
            opacity: isISS || isCSS ? 0.8 : 0,
        }).addTo(satMap);

        marker.bindPopup(`
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#e0e8f0;background:#0a0f1e;padding:8px;border-radius:6px;min-width:180px;">
                <div style="color:#00c8ff;font-weight:700;margin-bottom:6px;">${sat.name}</div>
                <div>NORAD: ${sat.norad_id}</div>
                <div>Alt: ${sat.alt_km.toFixed(0)} km</div>
                <div>Inc: ${sat.inclination.toFixed(1)}&deg;</div>
                <div>Period: ${sat.period_min} min</div>
                <div>Lat: ${sat.lat.toFixed(2)}&deg; Lng: ${sat.lng.toFixed(2)}&deg;</div>
            </div>
        `, {
            className: 'sat-popup',
            closeButton: false,
        });

        if (isISS) {
            issMarker = marker;
            // Pulsing effect via CSS class
            marker.getElement()?.classList.add('iss-pulse');
        }

        satMarkers.push(marker);
    });

    // Update ISS ground track
    fetchISSTrack();

    document.getElementById('map-updated').textContent = new Date().toLocaleTimeString('en-GB', { hour12: false });
}

async function fetchISSTrack() {
    try {
        const r = await fetch('/api/satellites/track/25544');
        const track = await r.json();
        if (!track || !track.length) return;

        if (issTrackLine) {
            satMap.removeLayer(issTrackLine);
        }

        const latlngs = track.map(p => [p.lat, p.lng]);

        // Split the track at antimeridian crossings to avoid wrapping lines
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
                    color: '#00ff88',
                    weight: 1.5,
                    opacity: 0.4,
                    dashArray: '6 4',
                }).addTo(issTrackLine);
            }
        });
        issTrackLine.addTo(satMap);
    } catch (e) {
        console.warn('ISS track fetch failed:', e);
    }
}

// Custom popup styles injected
const popupStyle = document.createElement('style');
popupStyle.textContent = `
    .sat-popup .leaflet-popup-content-wrapper {
        background: rgba(10,15,30,0.95) !important;
        border: 1px solid rgba(0,200,255,0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
    }
    .sat-popup .leaflet-popup-tip {
        background: rgba(10,15,30,0.95) !important;
        border: 1px solid rgba(0,200,255,0.2) !important;
    }
    .sat-popup .leaflet-popup-content { margin: 0 !important; }
    .iss-pulse {
        animation: iss-glow 2s ease-in-out infinite;
    }
    @keyframes iss-glow {
        0%, 100% { filter: drop-shadow(0 0 4px #00ff88); }
        50% { filter: drop-shadow(0 0 12px #00ff88); }
    }
`;
document.head.appendChild(popupStyle);

document.addEventListener('DOMContentLoaded', initSatMap);

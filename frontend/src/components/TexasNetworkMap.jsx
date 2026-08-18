import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip, useMap } from 'react-leaflet';
import { Navigation } from 'lucide-react';

const COUNTY_CENTROIDS = {
  "Bexar": { lat: 29.4241, lon: -98.4936, zoom: 10, name: "Bexar County (San Antonio)" },
  "Collin": { lat: 33.1972, lon: -96.6398, zoom: 10, name: "Collin County (Plano/Frisco)" },
  "Dallas": { lat: 32.7767, lon: -96.7970, zoom: 10, name: "Dallas County (Dallas)" },
  "Harris": { lat: 29.7604, lon: -95.3698, zoom: 10, name: "Harris County (Houston)" },
  "Tarrant": { lat: 32.7555, lon: -97.3308, zoom: 10, name: "Tarrant County (Fort Worth)" },
  "Travis": { lat: 30.2672, lon: -97.7431, zoom: 10, name: "Travis County (Austin)" }
};

const CITY_CENTROIDS = {
  "Houston": { lat: 29.7604, lon: -95.3698, county: "Harris" },
  "Dallas": { lat: 32.7767, lon: -96.7970, county: "Dallas" },
  "San Antonio": { lat: 29.4241, lon: -98.4936, county: "Bexar" },
  "Austin": { lat: 30.2672, lon: -97.7431, county: "Travis" },
  "Fort Worth": { lat: 32.7555, lon: -97.3308, county: "Tarrant" },
  "Plano": { lat: 33.0198, lon: -96.6989, county: "Collin" },
  "Frisco": { lat: 33.1507, lon: -96.8236, county: "Collin" },
  "Arlington": { lat: 32.7357, lon: -97.1081, county: "Tarrant" },
  "Irving": { lat: 32.8140, lon: -96.9489, county: "Dallas" },
  "Baytown": { lat: 29.7355, lon: -94.9774, county: "Harris" },
  "Bellaire": { lat: 29.7058, lon: -95.4588, county: "Harris" },
  "Lakeway": { lat: 30.3644, lon: -97.9814, county: "Travis" },
  "Pflugerville": { lat: 30.4548, lon: -97.6223, county: "Travis" },
  "Boerne": { lat: 29.7947, lon: -98.7320, county: "Bexar" },
  "Cedar Hill": { lat: 32.5885, lon: -96.9561, county: "Dallas" }
};

// Component to handle auto-zoom on selection or click
function MapRecenter({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true, duration: 0.9 });
  }, [center, zoom, map]);
  return null;
}

export default function TexasNetworkMap({
  selectedCounty,
  selectedCity,
  selectedSpecialty,
  mapData,
  onSelectCounty,
  onSelectCity
}) {
  const isFullySelected = Boolean(selectedCounty && selectedCity && selectedSpecialty);

  // Progressive map center & auto-zoom:
  // 1. Initial State: Full US / Texas view (center [31.5, -99.0], zoom 6)
  // 2. County selected: zoom 10
  // 3. City selected: zoom 12
  let mapCenter = [31.5, -99.0];
  let mapZoom = 6;

  if (selectedCity && CITY_CENTROIDS[selectedCity]) {
    mapCenter = [CITY_CENTROIDS[selectedCity].lat, CITY_CENTROIDS[selectedCity].lon];
    mapZoom = 12;
  } else if (selectedCounty && COUNTY_CENTROIDS[selectedCounty]) {
    mapCenter = [COUNTY_CENTROIDS[selectedCounty].lat, COUNTY_CENTROIDS[selectedCounty].lon];
    mapZoom = COUNTY_CENTROIDS[selectedCounty].zoom;
  }

  const rawProviders = mapData?.providers || [];
  const rawPatients = mapData?.patients || [];
  const citySummaries = mapData?.city_summaries || {};
  const rawZipcodes = mapData?.zipcodes || [];

  // STRICT SCOPING (Section 5):
  // Once state, city, and specialty are all selected, show data ONLY for that exact selection.
  // Nothing outside the current filter selection is rendered.
  const scopedProviders = useMemo(() => {
    if (!selectedCity) return rawProviders;
    return rawProviders.filter(p => p.city && p.city.toLowerCase() === selectedCity.toLowerCase());
  }, [rawProviders, selectedCity]);

  const scopedPatients = useMemo(() => {
    if (!selectedCity) return rawPatients;
    return rawPatients.filter(p => p.city && p.city.toLowerCase() === selectedCity.toLowerCase());
  }, [rawPatients, selectedCity]);

  const scopedZipcodes = useMemo(() => {
    if (!selectedCity) return rawZipcodes;
    return rawZipcodes.filter(z => z.city && z.city.toLowerCase() === selectedCity.toLowerCase());
  }, [rawZipcodes, selectedCity]);

  const getStatusColor = (score) => {
    const num = Number(score ?? 0);
    if (num >= 80) return '#27AE60'; // GREEN (Adequate)
    if (num >= 50) return '#F39C12'; // YELLOW (Partially Adequate)
    return '#E74C3C';                // RED (Inadequate)
  };

  return (
    <div className="glass-card" style={{ padding: '20px', marginBottom: '24px' }}>
      {/* Map Header (No toggle controls per section 6) */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(108, 92, 231, 0.25) 0%, rgba(15, 52, 96, 0.3) 100%)',
            padding: '8px',
            borderRadius: '8px',
            border: '1px solid rgba(108, 92, 231, 0.4)'
          }}>
            <Navigation size={18} color="#A29BFE" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFF' }}>
              Geospatial Network Adequacy & Access Map
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {isFullySelected
                ? `Strictly Scoped: ${selectedSpecialty} in ${selectedCity}, ${selectedCounty} County (${scopedZipcodes.length} ZIP codes, ${scopedProviders.length} Providers, ${scopedPatients.length} Patients)`
                : selectedCounty
                ? `County Zoom: ${selectedCounty} County • Click a city to zoom further`
                : 'Texas Statewide Overview • Click any county or city on the map to auto-zoom'}
            </p>
          </div>
        </div>
      </div>

      {/* Map Canvas */}
      <div style={{
        height: '480px',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        border: '1px solid var(--border-light)',
        position: 'relative'
      }}>
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%' }}
        >
          <MapRecenter center={mapCenter} zoom={mapZoom} />

          {/* CartoDB Voyager Tile Layer */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          {/* 1. STATEWIDE COUNTY CENTROIDS (Only visible when no city is selected) */}
          {!selectedCity && Object.entries(COUNTY_CENTROIDS).map(([cName, coords]) => {
            const isSelected = selectedCounty === cName;
            return (
              <CircleMarker
                key={`county-marker-${cName}`}
                center={[coords.lat, coords.lon]}
                radius={isSelected ? 20 : 15}
                pathOptions={{
                  fillColor: '#0F3460',
                  color: isSelected ? '#FFFFFF' : '#38BDF8',
                  weight: isSelected ? 3 : 2,
                  fillOpacity: 0.8
                }}
                eventHandlers={{
                  click: () => {
                    if (onSelectCounty) onSelectCounty(cName);
                  }
                }}
              >
                <Tooltip direction="top" offset={[0, -12]}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700 }}>
                    {coords.name} • Click to Zoom
                  </div>
                </Tooltip>
              </CircleMarker>
            );
          })}

          {/* 2. CITY ADEQUACY BOUNDARY SHAPES */}
          {/* If NOT fully selected, show all cities in the county. If fully selected, show ONLY the selected city (Section 5) */}
          {selectedCounty && Object.entries(CITY_CENTROIDS)
            .filter(([cityName, c]) => {
              if (selectedCity) {
                return cityName.toLowerCase() === selectedCity.toLowerCase();
              }
              return c.county === selectedCounty;
            })
            .map(([cityName, cCoords]) => {
              const sumKey = `${selectedCounty}_${cityName}`;
              const sum = citySummaries[sumKey];
              const isCitySelected = selectedCity === cityName;
              const cityAdequacy = sum ? Number(sum.total_adequacy) : 54;
              const cityColor = getStatusColor(cityAdequacy);

              return (
                <CircleMarker
                  key={`city-shape-${cityName}`}
                  center={[cCoords.lat, cCoords.lon]}
                  radius={isCitySelected ? 22 : 14}
                  pathOptions={{
                    fillColor: cityColor,
                    color: '#FFFFFF',
                    weight: isCitySelected ? 3 : 2,
                    fillOpacity: 0.88
                  }}
                  eventHandlers={{
                    click: () => {
                      if (onSelectCity) onSelectCity(cityName);
                    }
                  }}
                >
                  <Tooltip direction="top" offset={[0, -12]}>
                    <div style={{ fontSize: '0.76rem', fontWeight: 700 }}>
                      {cityName} ({selectedCounty} Co.) {sum ? `• ${sum.total_adequacy}%` : ''}
                    </div>
                  </Tooltip>
                  <Popup>
                    <div style={{ minWidth: '180px' }}>
                      <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#FFF' }}>
                        {cityName}, {selectedCounty} County
                      </div>
                      {sum && (
                        <div style={{ fontSize: '0.76rem', marginTop: '4px', lineHeight: '1.4' }}>
                          <div>Total Adequacy: <strong style={{ color: cityColor }}>{sum.total_adequacy}% ({sum.status || sum.adequacy_status})</strong></div>
                          <div>Capacity: <strong>{sum.capacity_adequacy}%</strong> | Distance: <strong>{sum.distance_adequacy}%</strong></div>
                        </div>
                      )}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}

          {/* 3. INDIVIDUAL ZIP CODE ADEQUACY SHAPES (Strictly scoped to selected city only) */}
          {selectedCity && scopedZipcodes.map((z, idx) => {
            if (!z.latitude || !z.longitude) return null;
            const zipTot = Number(z.total_adequacy ?? 54);
            const zipColor = getStatusColor(zipTot);

            return (
              <CircleMarker
                key={`zip-shape-${idx}-${z.zip_code}`}
                center={[z.latitude, z.longitude]}
                radius={11}
                pathOptions={{
                  fillColor: zipColor,
                  color: '#FFFFFF',
                  weight: 2,
                  fillOpacity: 0.92
                }}
              >
                <Tooltip direction="top" offset={[0, -8]}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700 }}>
                    ZIP {z.zip_code} ({z.city}): {zipTot}% ({z.status || (zipTot >= 80 ? 'ADEQUATE' : zipTot >= 50 ? 'PARTIALLY ADEQUATE' : 'INADEQUATE')})
                  </div>
                </Tooltip>
                <Popup>
                  <div style={{ fontSize: '0.8rem', minWidth: '190px' }}>
                    <div style={{ fontWeight: 800, color: '#FFF', marginBottom: '2px' }}>
                      ZIP Code: {z.zip_code}
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                      {z.city}, {z.county} County • {z.specialty || selectedSpecialty}
                    </div>
                    <div style={{ fontSize: '0.75rem', lineHeight: '1.45' }}>
                      <div>Total Adequacy: <strong style={{ color: zipColor }}>{zipTot}%</strong></div>
                      <div>Status: <strong style={{ color: zipColor }}>{z.status || (zipTot >= 80 ? 'Adequate' : zipTot >= 50 ? 'Partially Adequate' : 'Inadequate')}</strong></div>
                      <div>Capacity: <strong>{z.capacity_adequacy}%</strong> | Distance: <strong>{z.distance_adequacy}%</strong></div>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}

          {/* 4. SMALL PATIENT DOTS (Violet, strictly scoped to selection) */}
          {scopedPatients.map((pat, i) => {
            if (!pat.latitude || !pat.longitude) return null;
            return (
              <CircleMarker
                key={`pat-dot-${pat.patient_id || i}`}
                center={[pat.latitude, pat.longitude]}
                radius={2.8}
                pathOptions={{
                  fillColor: '#8B5CF6',
                  color: '#7C3AED',
                  weight: 0.6,
                  fillOpacity: 0.65
                }}
              >
                <Tooltip direction="top" offset={[0, -3]}>
                  <div style={{ fontSize: '0.70rem' }}>
                    Patient • {pat.city}, TX {pat.zip_code || ''}
                  </div>
                </Tooltip>
              </CircleMarker>
            );
          })}

          {/* 5. SMALL PROVIDER DOTS (Cyan, strictly scoped to selection) */}
          {scopedProviders.map((prov, i) => {
            if (!prov.latitude || !prov.longitude) return null;
            return (
              <CircleMarker
                key={`prov-dot-${prov.npi || i}`}
                center={[prov.latitude, prov.longitude]}
                radius={4}
                pathOptions={{
                  fillColor: '#38BDF8',
                  color: '#0284C7',
                  weight: 1,
                  fillOpacity: 0.88
                }}
              >
                <Tooltip direction="top" offset={[0, -5]}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 600 }}>
                    {prov.name} ({prov.specialty}) • {prov.city}
                  </div>
                </Tooltip>
                <Popup>
                  <div style={{ fontSize: '0.8rem' }}>
                    <div style={{ fontWeight: 700, color: '#38BDF8' }}>{prov.name}</div>
                    <div style={{ color: '#FFF' }}>{prov.facility_name}</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', marginTop: '3px' }}>
                      {prov.city}, TX {prov.zip_code}
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* 6. PERMANENT GREEN / YELLOW / RED ADEQUACY COLOR LEGEND */}
        <div style={{
          position: 'absolute',
          bottom: '14px',
          right: '14px',
          background: 'rgba(11, 19, 43, 0.95)',
          backdropFilter: 'blur(10px)',
          padding: '12px 16px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-light)',
          fontSize: '0.74rem',
          zIndex: 400,
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)'
        }}>
          <div style={{ fontWeight: 800, color: '#FFF', letterSpacing: '0.02em', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '4px' }}>
            Adequacy Color Legend
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#27AE60', border: '1px solid #FFF' }}></span>
            <span><strong style={{ color: '#27AE60' }}>Green:</strong> Adequate (≥80%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#F39C12', border: '1px solid #FFF' }}></span>
            <span><strong style={{ color: '#F39C12' }}>Yellow:</strong> Partially Adequate (50–79%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#E74C3C', border: '1px solid #FFF' }}></span>
            <span><strong style={{ color: '#E74C3C' }}>Red:</strong> Inadequate (&lt;50%)</span>
          </div>
          <div style={{ height: '1px', background: 'rgba(255,255,255,0.1)', margin: '2px 0' }}></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#8B5CF6' }}></span>
            <span style={{ color: 'var(--text-muted)' }}>Patient Dot (Violet)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#38BDF8' }}></span>
            <span style={{ color: 'var(--text-muted)' }}>Provider Dot (Cyan)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

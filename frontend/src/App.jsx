import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import FilterBar from './components/FilterBar';
import MetricCards from './components/MetricCards';
import TexasNetworkMap from './components/TexasNetworkMap';
import ExplainModal from './components/ExplainModal';
import ExportModal from './components/ExportModal';

const API_ORIGIN = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const API_BASE = `${API_ORIGIN}/api`;

export default function App() {
  // Filters State — starts empty per user requirement
  const [counties, setCounties] = useState(['Bexar', 'Collin', 'Dallas', 'Harris', 'Tarrant', 'Travis']);
  const [cities, setCities] = useState([]);
  const [specialties, setSpecialties] = useState([
    'Anesthesiology', 'Cardiology', 'Dermatology', 'Gynecology', 'Neurology', 'Ophthalmology', 'Orthopedic Surgery'
  ]);

  const [selectedCounty, setSelectedCounty] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('');

  // Data State
  const [currentMetrics, setCurrentMetrics] = useState(null);
  const [dashboardData, setDashboardData] = useState([]);
  const [mapData, setMapData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Modals State (AI Explanation on Metric Click & PDF Export only)
  const [explainModalOpen, setExplainModalOpen] = useState(false);
  const [explainMetricType, setExplainMetricType] = useState('total');
  const [explanationText, setExplanationText] = useState('');
  const [explainSource, setExplainSource] = useState('claude-api');
  const [explainModel, setExplainModel] = useState('claude-sonnet-5');
  const [explainLoading, setExplainLoading] = useState(false);

  const [exportOpen, setExportOpen] = useState(false);

  // 1. Initial Load: Metadata only & default map overview data
  const fetchMetadata = async () => {
    try {
      const [cRes, sRes, mapRes] = await Promise.all([
        fetch(`${API_BASE}/counties`),
        fetch(`${API_BASE}/specialties`),
        fetch(`${API_BASE}/map-data?specialty=Cardiology`)
      ]);
      const cData = await cRes.json();
      const sData = await sRes.json();
      const mData = await mapRes.json();

      if (Array.isArray(cData)) setCounties(cData);
      if (Array.isArray(sData)) setSpecialties(sData);
      setMapData(mData);
    } catch (err) {
      console.error('Failed to load initial metadata:', err);
    }
  };

  useEffect(() => {
    fetchMetadata();
  }, []);

  // 2. Cascading: When County changes, fetch cities for that county
  useEffect(() => {
    if (!selectedCounty) {
      setCities([]);
      setSelectedCity('');
      setSelectedSpecialty('');
      setCurrentMetrics(null);
      setDashboardData([]);
      return;
    }

    async function loadCities() {
      try {
        const res = await fetch(`${API_BASE}/counties/${selectedCounty}/cities`);
        const cData = await res.json();
        if (Array.isArray(cData)) {
          setCities(cData);
        }
      } catch (err) {
        console.error('Failed to load cities for county:', err);
      }
    }
    loadCities();
  }, [selectedCounty]);

  // 3. When County + City + Specialty are ALL selected, load specific adequacy metrics & strictly scoped map data
  useEffect(() => {
    if (!selectedCounty || !selectedCity || !selectedSpecialty) {
      setCurrentMetrics(null);
      if (selectedCounty || selectedSpecialty) {
        fetch(`${API_BASE}/map-data?county=${selectedCounty || ''}&city=${selectedCity || ''}&specialty=${selectedSpecialty || 'Cardiology'}`)
          .then(r => r.json())
          .then(d => setMapData(d))
          .catch(e => console.error(e));
      }
      return;
    }

    async function loadMetricsData() {
      setLoading(true);
      try {
        const [adeqRes, mapRes] = await Promise.all([
          fetch(`${API_BASE}/adequacy?county=${selectedCounty}&city=${selectedCity}&specialty=${selectedSpecialty}`),
          fetch(`${API_BASE}/map-data?county=${selectedCounty}&city=${selectedCity}&specialty=${selectedSpecialty}`)
        ]);

        if (adeqRes.ok) {
          const adeqData = await adeqRes.json();
          setCurrentMetrics(adeqData);
        }

        if (mapRes.ok) {
          const mapD = await mapRes.json();
          setMapData(mapD);
        }
      } catch (err) {
        console.error('Failed to load metrics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadMetricsData();
  }, [selectedCounty, selectedCity, selectedSpecialty]);

  // Handle Explain click (proxied through backend)
  const handleExplain = async (metricType) => {
    if (!currentMetrics) return;
    setExplainMetricType(metricType);
    setExplainModalOpen(true);
    setExplainLoading(true);
    setExplanationText('');

    try {
      const res = await fetch(`${API_BASE}/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          county: selectedCounty,
          city: selectedCity,
          specialty: selectedSpecialty,
          metric_type: metricType,
          metrics: currentMetrics || {}
        })
      });
      const data = await res.json();
      setExplanationText(data.explanation);
      setExplainSource(data.source || 'claude-api');
      setExplainModel(data.model || 'claude-sonnet-5');
    } catch (err) {
      setExplanationText('Could not generate explanation. Please ensure backend server is running.');
      setExplainSource('fallback');
    } finally {
      setExplainLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedCounty('');
    setSelectedCity('');
    setSelectedSpecialty('');
    setCurrentMetrics(null);
    setDashboardData([]);
    fetchMetadata();
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Navbar with Download as PDF only */}
      <Navbar onOpenExport={() => setExportOpen(true)} />

      {/* Main Container */}
      <main style={{
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '0 24px 60px 24px',
        width: '100%',
        flex: 1
      }}>
        {/* Single Row Cascading Filter Bar */}
        <FilterBar
          counties={counties}
          cities={cities}
          specialties={specialties}
          selectedCounty={selectedCounty}
          selectedCity={selectedCity}
          selectedSpecialty={selectedSpecialty}
          onCountyChange={setSelectedCounty}
          onCityChange={setSelectedCity}
          onSpecialtyChange={setSelectedSpecialty}
          onReset={handleReset}
          loading={loading}
        />

        {/* 3 Minimal Adequacy Cards (Capacity, Distance, Total) */}
        <MetricCards
          metrics={currentMetrics}
          selectedSpecialty={selectedSpecialty}
          selectedCity={selectedCity}
          selectedCounty={selectedCounty}
          onExplain={handleExplain}
          loading={loading}
        />

        {/* Geospatial Map Strictly Scoped to Filters */}
        <TexasNetworkMap
          selectedCounty={selectedCounty}
          selectedCity={selectedCity}
          selectedSpecialty={selectedSpecialty}
          mapData={mapData}
          onSelectCounty={(c) => {
            setSelectedCounty(c);
            setSelectedCity('');
            setSelectedSpecialty('');
          }}
          onSelectCity={(city) => {
            setSelectedCity(city);
          }}
        />
      </main>

      {/* Footer */}
      <footer style={{
        background: 'rgba(11, 19, 43, 0.95)',
        borderTop: '1px solid var(--border-light)',
        padding: '20px 24px',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: 'var(--text-dim)'
      }}>
        <div>CARENET • Healthcare Provider Network Adequacy & Access Intelligence System</div>
        <div style={{ marginTop: '4px' }}>
          Data-Folder Summary Table Engine • Powered by Claude AI
        </div>
      </footer>

      {/* AI Explanation Modal on Metric Click */}
      <ExplainModal
        isOpen={explainModalOpen}
        onClose={() => setExplainModalOpen(false)}
        metricType={explainMetricType}
        specialty={selectedSpecialty}
        city={selectedCity}
        county={selectedCounty}
        explanationText={explanationText}
        source={explainSource}
        model={explainModel}
        loading={explainLoading}
        metrics={currentMetrics}
      />

      {/* PDF Export Modal */}
      <ExportModal
        isOpen={exportOpen}
        onClose={() => setExportOpen(false)}
        selectedCounty={selectedCounty || 'Harris'}
        selectedCity={selectedCity || 'Houston'}
        selectedSpecialty={selectedSpecialty || 'Cardiology'}
        metrics={currentMetrics}
        dashboardData={dashboardData}
      />
    </div>
  );
}

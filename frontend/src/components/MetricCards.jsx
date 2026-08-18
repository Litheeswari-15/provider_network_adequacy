import React from 'react';
import { Sparkles, Layers } from 'lucide-react';

export default function MetricCards({ metrics, selectedSpecialty, selectedCity, selectedCounty, onExplain, loading }) {
  // Initial Empty State (before all filters are selected)
  if (!metrics || !selectedSpecialty || !selectedCity || !selectedCounty) {
    return (
      <div className="glass-card" style={{
        padding: '36px 24px',
        textAlign: 'center',
        marginBottom: '24px',
        border: '1px dashed rgba(255, 255, 255, 0.15)',
        background: 'rgba(30, 41, 59, 0.45)'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, rgba(108, 92, 231, 0.2) 0%, rgba(15, 52, 96, 0.3) 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 12px auto',
          border: '1px solid rgba(108, 92, 231, 0.3)'
        }}>
          <Layers size={22} color="#A29BFE" />
        </div>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#FFF', marginBottom: '6px' }}>
          Select State / County, City, and Specialty to View Network Adequacy
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '520px', margin: '0 auto' }}>
          Adequacy metrics are read directly from the data-folder summary table. Values remain empty until all filters are applied.
        </p>
      </div>
    );
  }

  // Exact 3 values read from summary table
  const capacity_adequacy = Number(metrics.capacity_adequacy ?? 0);
  const distance_adequacy = Number(metrics.distance_adequacy ?? 0);
  const total_adequacy = Number(metrics.total_adequacy ?? 0);

  // Color determination: Green >= 80%, Yellow 50-79%, Red < 50%
  const getStatusColor = (val) => {
    if (val >= 80) return '#27AE60';  // GREEN: Adequate
    if (val >= 50) return '#F39C12';  // YELLOW: Partially Adequate
    return '#E74C3C';                 // RED: Inadequate
  };

  const cap_color = getStatusColor(capacity_adequacy);
  const dist_color = getStatusColor(distance_adequacy);
  const tot_color = getStatusColor(total_adequacy);

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: '20px',
      marginBottom: '24px'
    }}>
      {/* 1. CAPACITY ADEQUACY */}
      <div 
        className="glass-card" 
        onClick={() => onExplain('capacity')}
        style={{
          padding: '22px 24px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          borderLeft: `4px solid ${cap_color}`,
          cursor: 'pointer',
          minHeight: '140px'
        }}
        title="Click to view AI Capacity Explanation"
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>
            Capacity Adequacy
          </span>
          <button 
            className="btn-explain" 
            onClick={(e) => { e.stopPropagation(); onExplain('capacity'); }}
            disabled={loading}
            style={{ padding: '4px 10px', fontSize: '0.72rem' }}
          >
            <Sparkles size={12} />
            <span>Explain</span>
          </button>
        </div>
        <div style={{ fontSize: '2.6rem', fontWeight: 800, color: cap_color, lineHeight: 1.1 }}>
          {capacity_adequacy.toFixed(0)}%
        </div>
      </div>

      {/* 2. DISTANCE ADEQUACY */}
      <div 
        className="glass-card" 
        onClick={() => onExplain('distance')}
        style={{
          padding: '22px 24px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          borderLeft: `4px solid ${dist_color}`,
          cursor: 'pointer',
          minHeight: '140px'
        }}
        title="Click to view AI Distance Explanation"
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>
            Distance Adequacy
          </span>
          <button 
            className="btn-explain" 
            onClick={(e) => { e.stopPropagation(); onExplain('distance'); }}
            disabled={loading}
            style={{ padding: '4px 10px', fontSize: '0.72rem' }}
          >
            <Sparkles size={12} />
            <span>Explain</span>
          </button>
        </div>
        <div style={{ fontSize: '2.6rem', fontWeight: 800, color: dist_color, lineHeight: 1.1 }}>
          {distance_adequacy.toFixed(0)}%
        </div>
      </div>

      {/* 3. TOTAL ADEQUACY */}
      <div 
        className="glass-card" 
        onClick={() => onExplain('total')}
        style={{
          padding: '22px 24px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          borderLeft: `4px solid ${tot_color}`,
          cursor: 'pointer',
          minHeight: '140px'
        }}
        title="Click to view AI Total Adequacy Executive Summary"
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>
            Total Adequacy
          </span>
          <button 
            className="btn-explain" 
            onClick={(e) => { e.stopPropagation(); onExplain('total'); }}
            disabled={loading}
            style={{ padding: '4px 10px', fontSize: '0.72rem' }}
          >
            <Sparkles size={12} />
            <span>Explain</span>
          </button>
        </div>
        <div style={{ fontSize: '2.6rem', fontWeight: 800, color: tot_color, lineHeight: 1.1 }}>
          {total_adequacy.toFixed(0)}%
        </div>
      </div>
    </div>
  );
}

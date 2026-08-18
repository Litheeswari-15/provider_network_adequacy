import React from 'react';
import { MapPin, Stethoscope, RotateCcw, Filter } from 'lucide-react';

export default function FilterBar({
  counties = [],
  cities = [],
  specialties = [],
  selectedCounty = '',
  selectedCity = '',
  selectedSpecialty = '',
  onCountyChange,
  onCityChange,
  onSpecialtyChange,
  onReset,
  loading
}) {
  return (
    <div className="glass-card" style={{ padding: '16px 20px', margin: '20px 0 24px 0' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1.2fr 1.2fr 1.2fr auto',
        gap: '16px',
        alignItems: 'flex-end'
      }}>
        {/* 1. State / County Dropdown */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
            <MapPin size={13} color="#38BDF8" />
            1. State / County
          </label>
          <select
            value={selectedCounty}
            onChange={(e) => {
              const val = e.target.value;
              onCountyChange(val);
              onCityChange('');
              onSpecialtyChange('');
            }}
            disabled={loading}
            style={{
              width: '100%',
              background: 'rgba(11, 19, 43, 0.9)',
              color: selectedCounty ? '#FFF' : 'var(--text-dim)',
              border: selectedCounty ? '1px solid #38BDF8' : '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: 'var(--radius-sm)',
              padding: '10px 14px',
              fontSize: '0.88rem',
              fontWeight: 600,
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <option value="">-- Select County (Texas) --</option>
            {counties.map((c) => (
              <option key={c} value={c}>{c} County, TX</option>
            ))}
          </select>
        </div>

        {/* 2. City / Submarket Dropdown */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: selectedCounty ? 'var(--text-muted)' : 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
            <MapPin size={13} color={selectedCounty ? "#A78BFA" : "var(--text-dim)"} />
            2. City / Submarket
          </label>
          <select
            value={selectedCity}
            onChange={(e) => {
              const val = e.target.value;
              onCityChange(val);
              onSpecialtyChange('');
            }}
            disabled={!selectedCounty || loading}
            style={{
              width: '100%',
              background: selectedCounty ? 'rgba(11, 19, 43, 0.9)' : 'rgba(15, 23, 42, 0.4)',
              color: selectedCity ? '#FFF' : 'var(--text-dim)',
              border: selectedCity ? '1px solid #A78BFA' : '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: 'var(--radius-sm)',
              padding: '10px 14px',
              fontSize: '0.88rem',
              fontWeight: 600,
              cursor: selectedCounty ? 'pointer' : 'not-allowed',
              opacity: selectedCounty ? 1 : 0.6,
              outline: 'none'
            }}
          >
            <option value="">{selectedCounty ? '-- Select City --' : 'Select County First'}</option>
            {cities.map((city) => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
        </div>

        {/* 3. Medical Specialty Dropdown */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: selectedCity ? 'var(--text-muted)' : 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
            <Stethoscope size={13} color={selectedCity ? "#27AE60" : "var(--text-dim)"} />
            3. Medical Specialty
          </label>
          <select
            value={selectedSpecialty}
            onChange={(e) => onSpecialtyChange(e.target.value)}
            disabled={!selectedCity || loading}
            style={{
              width: '100%',
              background: selectedCity ? 'rgba(11, 19, 43, 0.9)' : 'rgba(15, 23, 42, 0.4)',
              color: selectedSpecialty ? '#FFF' : 'var(--text-dim)',
              border: selectedSpecialty ? '1px solid #27AE60' : '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: 'var(--radius-sm)',
              padding: '10px 14px',
              fontSize: '0.88rem',
              fontWeight: 600,
              cursor: selectedCity ? 'pointer' : 'not-allowed',
              opacity: selectedCity ? 1 : 0.6,
              outline: 'none'
            }}
          >
            <option value="">{selectedCity ? '-- Select Specialty --' : 'Select City First'}</option>
            {specialties.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Reset Button */}
        <div>
          <button
            onClick={onReset}
            className="btn-secondary"
            style={{
              height: '42px',
              padding: '0 16px',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.85rem'
            }}
            title="Reset selections"
          >
            <RotateCcw size={15} />
            <span>Reset</span>
          </button>
        </div>
      </div>
    </div>
  );
}

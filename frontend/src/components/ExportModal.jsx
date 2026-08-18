import React from 'react';
import { X, Download, Printer, FileText, CheckCircle2, AlertTriangle, Building, Users } from 'lucide-react';

export default function ExportModal({
  isOpen,
  onClose,
  selectedCounty,
  selectedCity,
  selectedSpecialty,
  metrics,
  dashboardData
}) {
  if (!isOpen) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadCsv = () => {
    if (!dashboardData || dashboardData.length === 0) return;

    const headers = [
      'County',
      'City',
      'Specialty',
      'Total Adequacy (%)',
      'Adequacy Status',
      'Capacity Adequacy (%)',
      'Distance Adequacy (%)',
      'Market Concentration (HHI)',
      'HHI Interpretation',
      'Total Providers',
      'Total Patients',
      'Top Provider',
      'Top Provider Share (%)'
    ];

    const rows = dashboardData.map((d) => [
      d.county,
      d.city,
      d.specialty,
      d.total_adequacy,
      d.adequacy_status,
      d.capacity_adequacy,
      d.distance_adequacy,
      d.market_concentration_hhi,
      d.hhi_interpretation,
      d.total_providers,
      d.total_patients,
      `"${d.top_provider_name || ''}"`,
      d.top_provider_market_share || 0
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `CARENET_Adequacy_Report_${selectedCounty}_${selectedCity}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-content" 
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '800px' }}
      >
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-light)',
          paddingBottom: '14px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={22} color="#38BDF8" />
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFF' }}>
                Executive Network Adequacy Briefing Packet
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Generated for {selectedCity}, {selectedCounty} County • {new Date().toLocaleDateString()}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={handlePrint}
              className="btn-secondary"
              style={{ fontSize: '0.78rem', padding: '6px 12px' }}
            >
              <Printer size={14} />
              <span>Print / PDF</span>
            </button>
            <button
              onClick={handleDownloadCsv}
              className="btn-primary"
              style={{ fontSize: '0.78rem', padding: '6px 12px' }}
            >
              <Download size={14} />
              <span>Download CSV</span>
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Printable Report Body */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-sm)',
          padding: '20px',
          fontSize: '0.85rem',
          color: 'var(--text-main)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '12px', marginBottom: '16px' }}>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#FFF' }}>
                CARENET Healthcare Network Intelligence Audit
              </h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Focus: {selectedSpecialty} in {selectedCity} ({selectedCounty} County)
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{
                display: 'inline-block',
                padding: '4px 10px',
                borderRadius: '99px',
                fontSize: '0.75rem',
                fontWeight: 700,
                background: metrics?.adequacy_status === 'GREEN' ? 'rgba(46,204,113,0.2)' : 'rgba(241,196,15,0.2)',
                color: metrics?.adequacy_status === 'GREEN' ? '#2ECC71' : '#F1C40F'
              }}>
                Status: {metrics?.adequacy_status || 'YELLOW'} ({metrics?.total_adequacy || 0}%)
              </div>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '12px',
            marginBottom: '20px'
          }}>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>TOTAL ADEQUACY</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FFF' }}>{metrics?.total_adequacy}%</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>CAPACITY ADEQUACY</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#38BDF8' }}>{metrics?.capacity_adequacy}%</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>DISTANCE ADEQUACY</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#A78BFA' }}>{metrics?.distance_adequacy}%</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>MARKET HHI</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FFF' }}>{metrics?.market_concentration_hhi}</div>
            </div>
          </div>

          {/* All Specialties Table */}
          <h5 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
            Regional Specialty Performance Matrix:
          </h5>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', marginBottom: '16px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-dim)' }}>
                <th style={{ padding: '6px', textAlign: 'left' }}>Specialty</th>
                <th style={{ padding: '6px', textAlign: 'center' }}>Total Adeq</th>
                <th style={{ padding: '6px', textAlign: 'center' }}>Status</th>
                <th style={{ padding: '6px', textAlign: 'center' }}>Capacity</th>
                <th style={{ padding: '6px', textAlign: 'center' }}>Distance</th>
                <th style={{ padding: '6px', textAlign: 'center' }}>HHI</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData?.map((row) => (
                <tr key={row.specialty} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                  <td style={{ padding: '8px 6px', fontWeight: 600 }}>{row.specialty}</td>
                  <td style={{ padding: '8px 6px', textAlign: 'center' }}>{row.total_adequacy}%</td>
                  <td style={{ padding: '8px 6px', textAlign: 'center' }}>
                    <span style={{ color: row.adequacy_status === 'GREEN' ? '#2ECC71' : '#F1C40F', fontWeight: 700 }}>
                      {row.adequacy_status}
                    </span>
                  </td>
                  <td style={{ padding: '8px 6px', textAlign: 'center' }}>{row.capacity_adequacy}%</td>
                  <td style={{ padding: '8px 6px', textAlign: 'center' }}>{row.distance_adequacy}%</td>
                  <td style={{ padding: '8px 6px', textAlign: 'center' }}>{row.market_concentration_hhi}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Compliance & Attestation */}
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '10px' }}>
            Attestation: Prepared via CARENET Network Intelligence Engine according to CMS Title 42 CFR § 438.68 & Texas Insurance Code § 1301 provider access standards.
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
          <button onClick={onClose} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}

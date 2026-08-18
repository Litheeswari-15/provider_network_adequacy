import React from 'react';
import { Activity, Download } from 'lucide-react';

export default function Navbar({ onOpenExport }) {
  return (
    <header style={{
      background: 'rgba(11, 19, 43, 0.96)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-light)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '14px 24px'
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        {/* Brand & Identity */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6C5CE7 0%, #0F3460 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(108, 92, 231, 0.4)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <Activity size={22} color="#FFF" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFF' }}>
                CARENET
              </h1>
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
              Healthcare Provider Network Adequacy & Access Intelligence
            </p>
          </div>
        </div>

        {/* Top-of-Page Controls: Download as PDF only */}
        <div>
          <button 
            className="btn-secondary" 
            onClick={onOpenExport}
            style={{ 
              fontSize: '0.85rem', 
              padding: '8px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              border: '1px solid rgba(56, 189, 248, 0.4)',
              color: '#38BDF8'
            }}
          >
            <Download size={16} />
            <span>Download as PDF</span>
          </button>
        </div>
      </div>
    </header>
  );
}

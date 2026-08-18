import React from 'react';
import { X, Sparkles, Copy, Check, ShieldAlert, Clock, TrendingUp, Users, MapPin, Building, Cpu, Bot } from 'lucide-react';

export default function ExplainModal({
  isOpen,
  onClose,
  metricType,
  specialty,
  city,
  county,
  explanationText,
  source,
  model,
  loading,
  metrics
}) {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (explanationText) {
      navigator.clipboard.writeText(explanationText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getMetricTitle = () => {
    if (metricType === 'capacity') {
      return `Why is ${specialty} Capacity in ${city} at ${metrics?.capacity_adequacy || 0}%?`;
    } else if (metricType === 'distance') {
      return `Geographic Access Analysis: ${metrics?.distance_adequacy || 0}% Have Reasonable Access`;
    } else if (metricType === 'total') {
      return `Executive Summary: Overall ${specialty} Adequacy in ${city} (${metrics?.total_adequacy || 0}%)`;
    } else if (metricType === 'hhi') {
      return `Market Concentration Analysis: ${specialty} HHI in ${county} County (${metrics?.market_concentration_hhi || 0})`;
    }
    return `AI Network Intelligence: ${specialty} in ${city}, ${county} County`;
  };

  const formatContent = (text) => {
    if (!text) return null;
    
    const sections = text.split(/###\s+/);
    
    return sections.map((sec, idx) => {
      if (!sec.trim()) return null;
      
      const lines = sec.split('\n');
      const heading = lines[0];
      const body = lines.slice(1).join('\n');

      return (
        <div 
          key={idx} 
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 'var(--radius-sm)',
            padding: '16px',
            marginBottom: '14px'
          }}
        >
          {heading && (
            <h4 style={{
              fontSize: '0.92rem',
              fontWeight: 700,
              color: '#A29BFE',
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              {heading}
            </h4>
          )}
          <div style={{
            fontSize: '0.85rem',
            lineHeight: '1.6',
            color: 'var(--text-main)',
            whiteSpace: 'pre-line'
          }}>
            {body.trim()}
          </div>
        </div>
      );
    });
  };

  const isClaudeApi = source === 'claude-api';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-content" 
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '780px' }}
      >
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '16px',
          borderBottom: '1px solid var(--border-light)',
          paddingBottom: '16px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              background: isClaudeApi 
                ? 'linear-gradient(135deg, #6C5CE7 0%, #D97706 100%)'
                : 'linear-gradient(135deg, #6C5CE7 0%, #0F3460 100%)',
              padding: '10px',
              borderRadius: '10px',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <Sparkles size={20} color="#FFF" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  color: isClaudeApi ? '#FBBF24' : '#A29BFE',
                  background: isClaudeApi ? 'rgba(245, 158, 11, 0.2)' : 'rgba(108, 92, 231, 0.2)',
                  border: isClaudeApi ? '1px solid rgba(245, 158, 11, 0.4)' : '1px solid rgba(108, 92, 231, 0.4)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  {isClaudeApi ? <Bot size={12} /> : <Cpu size={12} />}
                  <span>{isClaudeApi ? `Claude API (${model || 'claude-sonnet-5'})` : 'Rule-Based Fallback Engine'}</span>
                </span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                  {specialty} • {city}, {county} County
                </span>
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFF' }}>
                {getMetricTitle()}
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '6px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <div className="pulse-dot" style={{ width: '16px', height: '16px', margin: '0 auto 16px auto' }}></div>
            <p style={{ fontWeight: 600, color: '#FFF' }}>Synthesizing Network Intelligence via Claude...</p>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '4px' }}>
              Executing root-cause diagnosis and recruitment modeling for {city}
            </p>
          </div>
        ) : (
          <div>
            {formatContent(explanationText)}
          </div>
        )}

        {/* Footer Actions */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderTop: '1px solid var(--border-light)',
          paddingTop: '16px',
          marginTop: '20px'
        }}>
          <button
            onClick={handleCopy}
            className="btn-secondary"
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            {copied ? <Check size={14} color="#2ECC71" /> : <Copy size={14} />}
            <span>{copied ? 'Copied Insights!' : 'Copy to Clipboard'}</span>
          </button>

          <button
            onClick={onClose}
            className="btn-primary"
            style={{ fontSize: '0.82rem', padding: '7px 18px' }}
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
}

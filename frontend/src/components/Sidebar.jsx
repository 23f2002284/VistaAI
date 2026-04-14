import React from 'react';

export default function Sidebar({ activeRoute, onNavigate, theme, toggleTheme }) {
  const links = [
    { id: 'overview', label: 'Overview ✨' },
    { id: 'create', label: 'Create Tour 🎬' },
    { id: 'projects', label: 'Projects File 📁' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">VistaAI</div>
      <nav className="nav-links">
        {links.map((link) => (
          <div 
            key={link.id}
            className={`nav-item ${activeRoute === link.id ? 'active' : ''}`}
            onClick={() => onNavigate(link.id)}
          >
            {link.label}
          </div>
        ))}
      </nav>
      
      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <button 
          onClick={toggleTheme} 
          style={{
            background: 'var(--bg-app)', 
            color: 'var(--text-main)', 
            border: '1px solid var(--border)',
            padding: '0.8rem',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontWeight: '600',
            transition: 'all 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
        >
          {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center' }}>
          <p>VistaAI Premium | 2026</p>
        </div>
      </div>
    </aside>
  );
}

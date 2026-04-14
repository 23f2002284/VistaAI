import React, { useState, useEffect } from 'react';

export default function ProjectsManagement({ onNavigate }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeVideo, setActiveVideo] = useState(null);

  useEffect(() => {
    const fetchProjects = () => {
      fetch('http://localhost:8000/tours')
        .then(res => res.json())
        .then(data => {
          setProjects(data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error fetching tours:", err);
          setLoading(false);
        });
    };
    
    fetchProjects();
    const interval = setInterval(fetchProjects, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bento-card">
      <h1>Projects Management 📁</h1>
      <p className="subtitle">View and manage all your generated properties.</p>
      
      {loading ? <p>Loading projects...</p> : (
      <div className="projects-grid">
        {projects.map(p => (
          <div key={p.id} className="bento-card project-card">
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
                <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{p.id}</span>
                <span className={`badge ${p.status.toLowerCase()}`}>{p.status}</span>
              </div>
              
              {/* Dynamic Thumbnail Layer */}
              {p.thumbnail_url ? (
                <div style={{ 
                  height: '140px', width: '100%', marginBottom: '1rem', 
                  borderRadius: 'var(--radius-sm)', overflow: 'hidden', 
                  backgroundImage: `url(${p.thumbnail_url})`, backgroundSize: 'cover', backgroundPosition: 'center',
                  boxShadow: 'inset 0px 0px 20px rgba(0,0,0,0.5)', border: '1px solid var(--border)'
                }} />
              ) : (
                <div style={{ height: '140px', width: '100%', marginBottom: '1rem', borderRadius: 'var(--radius-sm)', background: 'rgba(0,0,0,0.2)' }} />
              )}
              
              <h3 style={{ textTransform: 'capitalize', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.address}</h3>
              <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{p.date}</p>
            </div>
            
            <div style={{ marginTop: '2rem' }}>
              <button 
                className="btn secondary" 
                style={{ width: '100%', padding: '0.8rem' }}
                onClick={() => {
                  if (p.status === 'Complete' && p.video_url) {
                    setActiveVideo(p.video_url);
                  } else {
                    alert('Currently processing on the AI Pipeline. The dashboard will automatically update when finished.');
                  }
                }}
              >
                {p.status === 'Complete' ? 'View Tour 🎬' : 'Check Status'}
              </button>
            </div>
          </div>
        ))}
        
        <div 
          className="bento-card project-card" 
          onClick={() => onNavigate('create')}
          style={{ borderStyle: 'dashed', background: 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
        >
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: 'var(--primary)' }}>+</div>
            <p style={{ color: 'var(--text-main)', fontWeight: 600 }}>New Project</p>
          </div>
        </div>
      </div>
      )}
                 
      {activeVideo && (
        <div 
          onClick={() => setActiveVideo(null)}
          style={{ 
            position: 'fixed', inset: 0, 
            backgroundColor: 'rgba(0, 0, 0, 0.85)', 
            backdropFilter: 'blur(8px)',
            zIndex: 9999, display: 'flex', 
            alignItems: 'center', justifyContent: 'center',
            padding: '2rem'
          }}
        >
          <div 
            onClick={e => e.stopPropagation()}
            style={{ 
              position: 'relative', width: '100%', maxWidth: '850px',
              background: '#ffffff', borderRadius: '16px',
              padding: '0.8rem',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
              display: 'flex', flexDirection: 'column'
            }}
          >
            <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0.5rem 1rem 0.5rem' }}>
              <h3 style={{ color: '#1a1a1a', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>🎥 Tour Playback</h3>
              <button 
                onClick={() => setActiveVideo(null)} 
                title="Close Player"
                style={{ 
                  background: '#fee2e2', color: '#ef4444', border: 'none', 
                  borderRadius: '50%', width: '32px', height: '32px', 
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 'bold', fontSize: '1rem'
                }}
              >
                ✕
              </button>
            </div>
            
            <div style={{ width: '100%', borderRadius: '10px', overflow: 'hidden', background: '#000' }}>
              <video 
                src={activeVideo} 
                controls 
                autoPlay 
                style={{ width: '100%', display: 'block', outline: 'none', maxHeight: '70vh' }} 
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

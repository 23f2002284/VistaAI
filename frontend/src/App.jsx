import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ProjectsManagement from './components/ProjectsManagement'
import CreateTourWizard from './components/CreateTourWizard'

function App() {
  const [activeRoute, setActiveRoute] = useState("create");
  const [theme, setTheme] = useState("dark"); // Default to the Classy Midnight theme upon boot up
  const [metrics, setMetrics] = useState({ total: 0, successRate: '--' });

  // Hook into the browser DOM to apply the class mappings simultaneously
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
  }, [theme]);
  
  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  useEffect(() => {
    if (activeRoute === 'overview') {
      fetch('http://localhost:8000/tours')
        .then(res => res.json())
        .then(data => {
          const total = data.length;
          const successful = data.filter(t => t.status === 'Complete').length;
          const failed = data.filter(t => t.status === 'Failed').length;
          const finished = successful + failed;
          
          let rate = '--';
          if (finished > 0) {
            rate = Math.round((successful / finished) * 100) + '%';
          }
          setMetrics({ total, successRate: rate });
        })
        .catch(err => console.error("Could not fetch metrics:", err));
    }
  }, [activeRoute]);
  
  return (
    <div className="app-layout">
      <Sidebar 
        activeRoute={activeRoute} 
        onNavigate={setActiveRoute}
        theme={theme}
        toggleTheme={toggleTheme}
      />
      
      <main className="main-content">
        {activeRoute === 'projects' && <ProjectsManagement onNavigate={setActiveRoute} />}
        {activeRoute === 'create' && <CreateTourWizard onComplete={() => setActiveRoute('projects')} />}
        {activeRoute === 'overview' && (
          <div className="bento-card">
            <h1>Welcome to VistaAI 🚀</h1>
            <p className="subtitle">Your ultimate AI-powered property tour generator.</p>
            <div className="projects-grid">
              <div className="bento-card" style={{background: 'var(--primary-light)'}}>
                <h2 style={{color: 'var(--primary)'}}>Tours Generated</h2>
                <div style={{fontSize: '3rem', fontWeight: 800, color: 'var(--primary)'}}>
                  {metrics.total}
                </div>
              </div>
              <div className="bento-card" style={{background: '#c6f6d5'}}>
                <h2 style={{color: '#22543d'}}>Success Rate</h2>
                <div style={{fontSize: '3rem', fontWeight: 800, color: '#22543d'}}>
                  {metrics.successRate}
                </div>
                <p style={{color: '#22543d', marginTop: '0.5rem'}}>Waiting for first projects to calibrate.</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

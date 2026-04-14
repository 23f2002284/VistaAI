import React, { useState, useRef } from 'react';

export default function CreateTourWizard({ onComplete }) {
  const [selectedStyle, setSelectedStyle] = useState('Modern Minimalist');
  const [selectedVoice, setSelectedVoice] = useState('kore');
  const [generationMode, setGenerationMode] = useState('Premium');
  const [step, setStep] = useState(1);
  const [images, setImages] = useState([]);
  const [address, setAddress] = useState('');
  const [roughNotes, setRoughNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const audioRef = useRef(null);
  const totalSteps = 4;

  const playVoiceSample = (e) => {
    e.preventDefault();
    if (audioRef.current) {
      audioRef.current.load();
      audioRef.current.play();
    }
  };

  const handleImageUpload = (e) => {
    if(e.target.files && e.target.files.length > 0) {
        const newImages = Array.from(e.target.files).map(file => ({
            id: Math.random().toString(36).substr(2, 9),
            file: file,
            preview: URL.createObjectURL(file)
        }));
        setImages(prev => [...prev, ...newImages]);
    }
  };

  const moveImage = (index, direction) => {
    const newImages = [...images];
    if (direction === 'up' && index > 0) {
      [newImages[index - 1], newImages[index]] = [newImages[index], newImages[index - 1]];
    } else if (direction === 'down' && index < newImages.length - 1) {
      [newImages[index + 1], newImages[index]] = [newImages[index], newImages[index + 1]];
    }
    setImages(newImages);
  };

  const nextStep = () => setStep(s => Math.min(s + 1, totalSteps));
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const handleGenerateScript = async (e) => {
    e.preventDefault();
    if (images.length === 0) {
      alert("Please upload at least one image in Step 2 so the AI can physically analyze the property.");
      return;
    }
    
    setIsGeneratingScript(true);
    const formData = new FormData();
    formData.append('address', address);
    formData.append('preference', selectedStyle);
    formData.append('rough_notes', roughNotes);
    images.forEach(img => formData.append('images', img.file));

    try {
      const res = await fetch('http://localhost:8000/generate-wizard-script', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.status === 'success' && data.script) {
        setRoughNotes(data.script);
      } else {
        alert("Failed to generate script.");
      }
    } catch (err) {
      console.error(err);
      alert("Error connecting to script generator API.");
    } finally {
      setIsGeneratingScript(false);
    }
  };

  return (
    <div className="bento-card">
      <div className="wizard-header">
        <div>
          <h1>Create New Tour 🎬</h1>
          <p className="subtitle">From static images to cinematic tours in minutes.</p>
        </div>
        <div className="wizard-step-indicator">
          Step {step} of {totalSteps}
        </div>
      </div>

      <div className="wizard-content">
        {step === 1 && (
          <div className="step-panel" key="step-1">
            <h2>1. Property Details</h2>
            <div className="form-group">
              <label>Address <span style={{color: 'red'}}>*</span></label>
              <input type="text" placeholder="Start typing address..." value={address} onChange={e => setAddress(e.target.value)} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              <div className="form-group"><label>Beds</label><input type="number" placeholder="2" /></div>
              <div className="form-group"><label>Baths</label><input type="number" placeholder="1" /></div>
              <div className="form-group"><label>Land sqft</label><input type="number" placeholder="1200" /></div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="step-panel" key="step-2">
            <h2>2. Upload Room Imagery</h2>
            <p style={{color: 'var(--text-muted)', marginBottom: '1rem'}}>Upload empty photos. Vertical order defines the tour sequence.</p>
            
            {images.length === 0 && (
              <label className="drag-zone" style={{ display: 'block', padding: '2rem' }}>
                <input type="file" multiple accept="image/*" style={{ display: 'none' }} title="Upload files" onChange={handleImageUpload} />
                <span style={{ fontSize: '2rem' }}>📸</span>
                <p style={{marginTop: '0.5rem'}}>Click or drag photos here</p>
              </label>
            )}
            
            {images.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '1.5rem', maxHeight: 'max-content', padding: '0.5rem' }}>
                {images.map((img, index) => (
                  <div key={img.id} className="bento-card" style={{ padding: '0.6rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', border: '1px solid var(--border)' }}>
                    <div style={{ position: 'relative' }}>
                      <img src={img.preview} style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '8px', background: '#e2e4e9' }} alt="preview" />
                      <div style={{ position: 'absolute', top: '5px', left: '5px', background: 'var(--primary)', color: 'white', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '0.85rem', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' }}>{index + 1}</div>
                      <button onClick={() => setImages(images.filter((_, i) => i !== index))} style={{ position: 'absolute', top: '5px', right: '5px', background: '#fee2e2', border: 'none', borderRadius: '50%', width: '24px', height: '24px', cursor: 'pointer', color: '#ef4444', fontWeight: 'bold' }} title="Remove Image">✕</button>
                    </div>
                    <span style={{ fontSize: '0.85rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: 'var(--text-main)', fontWeight: 600 }}>{img.file.name}</span>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button onClick={() => moveImage(index, 'up')} disabled={index === 0} className="btn secondary" style={{ flex: 1, padding: '0.3rem', fontSize: '0.9rem', opacity: index === 0 ? 0.3 : 1 }}>Move ◀</button>
                      <button onClick={() => moveImage(index, 'down')} disabled={index === images.length - 1} className="btn secondary" style={{ flex: 1, padding: '0.3rem', fontSize: '0.9rem', opacity: index === images.length - 1 ? 0.3 : 1 }}>▶ Move</button>
                    </div>
                  </div>
                ))}
                
                <label className="bento-card" style={{ padding: '0.6rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', border: '2px dashed var(--border)', cursor: 'pointer', background: 'transparent', minHeight: '180px' }}>
                  <input type="file" multiple accept="image/*" style={{ display: 'none' }} onChange={handleImageUpload} />
                  <span style={{ fontSize: '2rem', color: 'var(--primary)' }}>+</span>
                  <p style={{ color: 'var(--text-main)', fontWeight: 600, fontSize: '0.9rem' }}>Add More</p>
                </label>
              </div>
            )}
          </div>
        )}

        {step === 3 && (
          <div className="step-panel" key="step-3">
            <h2>3. Virtual Staging & Vibes</h2>
            <div className="form-group">
              <label>Interior Aesthetic</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {[
                  { name: 'Neobrutalist Bold', img: 'https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?auto=format&fit=crop&q=80&w=300&h=150' },
                  { name: 'Modern Minimalist', img: 'https://images.unsplash.com/photo-1593696140826-c58b021acf8b?auto=format&fit=crop&q=80&w=300&h=150' },
                  { name: 'Cozy Rustic', img: 'https://images.unsplash.com/photo-1726090401458-7abb00f7450c?auto=format&fit=crop&q=80&w=300&h=150' },
                  { name: 'Japandi Calm', img: 'https://images.unsplash.com/photo-1604578762246-41134e37f9cc?auto=format&fit=crop&q=80&w=300&h=150' }
                ].map(style => (
                  <div 
                    key={style.name} 
                    onClick={() => setSelectedStyle(style.name)}
                    className="bento-card" 
                    style={{ 
                      padding: '0.8rem', 
                      cursor: 'pointer', 
                      display: 'flex', 
                      flexDirection: 'column', 
                      gap: '0.8rem', 
                      border: selectedStyle === style.name ? '2px solid var(--primary)' : '2px solid transparent' 
                    }}>
                    <img src={style.img} alt={style.name} style={{ width: '100%', borderRadius: '12px', objectFit: 'cover' }} />
                    <span style={{ fontWeight: 600, textAlign: 'center', color: selectedStyle === style.name ? 'var(--primary)' : 'var(--text-main)' }}>{style.name}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="form-group">
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem'}}>
                <label style={{marginBottom: 0}}>Rough Script Notes</label>
                <button 
                  className="btn secondary" 
                  style={{padding: '0.4rem 0.8rem', fontSize: '0.85rem'}} 
                  onClick={handleGenerateScript}
                  disabled={isGeneratingScript}
                >
                  {isGeneratingScript ? '✨ Analyzing Images...' : '✨ Generate Script with AI'}
                </button>
              </div>
              <textarea rows={3} placeholder="Mention the beautiful morning sunlight in the kitchen..." value={roughNotes} onChange={e => setRoughNotes(e.target.value)} />
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="step-panel" key="step-4">
            <h2>4. AI Voice Over & Generation Mode</h2>
            <div className="form-group">
              <label>Processing Engine</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div 
                  className="bento-card"
                  onClick={() => setGenerationMode('Premium')}
                  style={{ padding: '1rem', cursor: 'pointer', border: generationMode === 'Premium' ? '2px solid var(--primary)' : '2px solid transparent', background: generationMode === 'Premium' ? 'rgba(79, 70, 229, 0.05)' : 'var(--bg-app)' }}
                >
                  <h4 style={{ margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem', color: generationMode === 'Premium' ? 'var(--primary)' : 'var(--text-main)' }}>✨ Google Veo (Premium)</h4>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>Dynamically synthesize hyper-realistic 3D cinematic video transitions using GenAI. Highest quality.</p>
                </div>
                <div 
                  className="bento-card"
                  onClick={() => setGenerationMode('Basic')}
                  style={{ padding: '1rem', cursor: 'pointer', border: generationMode === 'Basic' ? '2px solid var(--primary)' : '2px solid transparent', background: generationMode === 'Basic' ? 'rgba(79, 70, 229, 0.05)' : 'var(--bg-app)' }}
                >
                  <h4 style={{ margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem', color: generationMode === 'Basic' ? 'var(--primary)' : 'var(--text-main)' }}>⚡ Fast Styler (Basic)</h4>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>Animate static images with cinematic pan & zooms via FFmpeg. Extremely fast processing.</p>
                </div>
              </div>
            </div>

            <div className="bento-card" style={{ background: 'var(--bg-app)', padding: '1.5rem', marginBottom: '1.5rem' }}>
              <label style={{display: 'flex', alignItems: 'center', gap: '0.8rem', cursor: 'pointer', fontSize: '1.1rem'}}>
                <input type="checkbox" defaultChecked style={{width: '20px', height: '20px'}} />
                Include Auto-Generated Voice Narration
              </label>
            </div>
            <div className="form-group">
              <label>Voice Selection (Max 15 words per scene)</label>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <select style={{ flex: 1 }} value={selectedVoice} onChange={e => setSelectedVoice(e.target.value)}>
                  <option value="kore">Kore (Friendly, Warm)</option>
                  <option value="puck">Puck (Professional, Sharp)</option>
                  <option value="aoede">Aoede (Soft, Calm)</option>
                </select>
                <button className="btn secondary" style={{ whiteSpace: 'nowrap' }} onClick={playVoiceSample}>
                  ▶️ Play Sample
                </button>
                {/* Dynamically bound native AI voice samples */}
                <audio ref={audioRef} src={`/${selectedVoice}.mp3`} style={{display: 'none'}} />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="wizard-footer">
        <button 
          className="btn secondary" 
          onClick={prevStep}
          disabled={step === 1}
          style={{ opacity: step === 1 ? 0 : 1 }}
        >
          Back
        </button>
        
        {step < totalSteps ? (
          <button className="btn" onClick={nextStep}>Next Step ➔</button>
        ) : (
          <button className="btn" disabled={isSubmitting} onClick={async () => {
            if (!address.trim()) { alert("Validation Error: Please step back to Step 1 and provide a valid Property Address."); return; }
            if (images.length === 0) { alert("Validation Error: Please step back to Step 2 and upload at least one room image."); return; }
            
            setIsSubmitting(true);
            const formData = new FormData();
            formData.append('address', address);
            formData.append('preference', selectedStyle);
            formData.append('rough_notes', roughNotes);
            formData.append('voice', selectedVoice);
            formData.append('mode', generationMode);
            images.forEach(img => formData.append('images', img.file));

            try {
              const res = await fetch('http://localhost:8000/generate-full-property-tour', { method: 'POST', body: formData });
              const data = await res.json();
              if (data.status === 'success') {
                alert("Success! Tour has been pushed to the AI Pipeline.");
                onComplete();
              } else {
                alert("Creation failed.");
              }
            } catch (err) {
              console.error(err);
              alert("Error connecting to backend API.");
            } finally {
              setIsSubmitting(false);
            }
          }}>
            {isSubmitting ? 'Loading...' : 'Generate Magic ✨'}
          </button>
        )}
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Save } from 'lucide-react';

const API_BASE = 'http://localhost:8081/api';

export default function Config() {
  const [config, setConfig] = useState({
    target_url: '',
    max_likes: 1,
    min_delay: 3,
    max_delay: 8,
    headless: false,
  });

  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await axios.get(`${API_BASE}/config`);
      setConfig({
        target_url: res.data.target_url || '',
        max_likes: res.data.max_likes || 1,
        min_delay: res.data.min_delay || 3,
        max_delay: res.data.max_delay || 8,
        headless: res.data.headless || false,
      });
    } catch (error) {
      console.error(error);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await axios.post(`${API_BASE}/config`, config);
      alert('Configuration saved successfully!');
    } catch (error) {
      alert('Error saving configuration');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Configuration</h1>
        <p className="page-subtitle">Configure bot behavior and target URL</p>
      </div>

      <div className="glass-panel" style={{ maxWidth: '800px' }}>
        <form onSubmit={handleSave}>
          <div className="form-group">
            <label className="form-label">Target Facebook Post URL</label>
            <input 
              type="url" 
              className="form-input" 
              placeholder="https://www.facebook.com/share/p/..."
              value={config.target_url}
              onChange={e => setConfig({...config, target_url: e.target.value})}
              required 
            />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Max Likes (per account)</label>
              <input 
                type="number" 
                className="form-input" 
                min="1"
                value={config.max_likes}
                onChange={e => setConfig({...config, max_likes: parseInt(e.target.value)})}
                required 
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Run in Headless Mode (Hidden Browser)</label>
              <select 
                className="form-input"
                value={config.headless ? 'true' : 'false'}
                onChange={e => setConfig({...config, headless: e.target.value === 'true'})}
              >
                <option value="false">False (Show Browser)</option>
                <option value="true">True (Hidden)</option>
              </select>
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Minimum Delay (seconds)</label>
              <input 
                type="number" 
                className="form-input" 
                min="1"
                value={config.min_delay}
                onChange={e => setConfig({...config, min_delay: parseInt(e.target.value)})}
                required 
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Maximum Delay (seconds)</label>
              <input 
                type="number" 
                className="form-input" 
                min="1"
                value={config.max_delay}
                onChange={e => setConfig({...config, max_delay: parseInt(e.target.value)})}
                required 
              />
            </div>
          </div>

          <div style={{ marginTop: '2rem' }}>
            <button type="submit" className="btn btn-primary" disabled={isSaving}>
              <Save size={18} /> {isSaving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

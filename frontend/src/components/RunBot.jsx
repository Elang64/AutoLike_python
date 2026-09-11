import { useState } from 'react';
import axios from 'axios';
import { Play, Square, Activity } from 'lucide-react';

const API_BASE = 'http://localhost:8081/api';

export default function RunBot() {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState([
    { type: 'info', text: 'System ready.' },
    { type: 'info', text: 'Waiting for command...' }
  ]);

  const handleStart = async () => {
    try {
      setIsRunning(true);
      addLog('info', 'Sending start command to backend...');
      
      const res = await axios.post(`${API_BASE}/run`);
      
      addLog('ok', res.data.message);
      addLog('warn', 'NOTE: This basic frontend does not stream real-time logs yet.');
      addLog('info', 'Please check your Python terminal/command prompt to see the live bot process.');
      
      // Simulate stopping after a while for the UI
      setTimeout(() => setIsRunning(false), 5000);
      
    } catch (error) {
      setIsRunning(false);
      addLog('err', error.response?.data?.detail || 'Error starting bot');
    }
  };

  const addLog = (type, text) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { type, text: `[${timestamp}] ${text}` }]);
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Run Bot</h1>
        <p className="page-subtitle">Start the auto-like process</p>
      </div>

      <div className="grid-2">
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
          
          <div style={{ marginBottom: '2rem', color: isRunning ? 'var(--accent)' : 'var(--text-muted)' }}>
            <Activity size={64} className={isRunning ? 'pulse-animation' : ''} style={{ borderRadius: '50%' }} />
          </div>

          <h2 style={{ marginBottom: '1rem' }}>{isRunning ? 'Bot is Running...' : 'Ready to Start'}</h2>
          
          <button 
            className={`btn ${isRunning ? 'btn-danger' : 'btn-primary'}`} 
            style={{ padding: '1rem 3rem', fontSize: '1.25rem' }}
            onClick={handleStart}
            disabled={isRunning}
          >
            {isRunning ? (
              <><Square size={24} /> Processing</>
            ) : (
              <><Play size={24} /> START BOT</>
            )}
          </button>
        </div>

        <div className="glass-panel">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Terminal Output
          </h3>
          <div className="terminal">
            {logs.map((log, idx) => (
              <div key={idx} className={`terminal-line ${log.type}`}>
                {log.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

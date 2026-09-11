import { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, CheckCircle, Clock } from 'lucide-react';

const API_BASE = 'http://localhost:8081/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    accounts: 0,
    withCookies: 0,
    targetUrl: 'Not Set',
  });
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetchData();
    
    // Poll results every 5 seconds to get updates when bot finishes
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [accountsRes, configRes, resultsRes] = await Promise.all([
        axios.get(`${API_BASE}/accounts`),
        axios.get(`${API_BASE}/config`),
        axios.get(`${API_BASE}/results`).catch(() => ({ data: [] })),
      ]);
      
      const accounts = accountsRes.data;
      setStats({
        accounts: accounts.length,
        withCookies: accounts.filter(a => a.has_cookies).length,
        targetUrl: configRes.data.target_url || 'Not Set',
      });
      setResults(resultsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Overview of your Auto-Like Bot</p>
      </div>

      <div className="grid-3" style={{ marginBottom: '2rem' }}>
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(99, 102, 241, 0.1)', borderRadius: '12px', color: 'var(--primary)' }}>
              <Users size={32} />
            </div>
            <div>
              <h3 style={{ fontSize: '2rem', margin: 0 }}>{stats.accounts}</h3>
              <p className="page-subtitle">Total Accounts</p>
            </div>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px', color: 'var(--accent)' }}>
              <CheckCircle size={32} />
            </div>
            <div>
              <h3 style={{ fontSize: '2rem', margin: 0 }}>{stats.withCookies}</h3>
              <p className="page-subtitle">Ready with Cookies</p>
            </div>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', color: 'var(--danger)' }}>
              <Clock size={32} />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', margin: 0, wordBreak: 'break-all', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {stats.targetUrl}
              </h3>
              <p className="page-subtitle">Current Target URL</p>
            </div>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ marginTop: '2rem' }}>
        <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle size={24} color="var(--primary)" /> Run Results
        </h2>
        
        {results.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No run results found. Start the bot to see logs here.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Account Name</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {results.map((res, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 500 }}>{res.account}</td>
                    <td>{res.email || '-'}</td>
                    <td>
                      {res.success ? (
                        <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle size={14} /> Berhasil Like
                        </span>
                      ) : (
                        <span className="badge badge-error" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={14} /> Gagal
                        </span>
                      )}
                    </td>
                    <td style={{ color: 'var(--text-muted)' }}>{res.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

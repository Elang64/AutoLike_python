import { useState, useEffect } from 'react';
import axios from 'axios';
import { UserPlus, Key, Trash2 } from 'lucide-react';

const API_BASE = 'http://localhost:8081/api';

export default function Accounts() {
  const [accounts, setAccounts] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCookieModalOpen, setIsCookieModalOpen] = useState(false);
  
  const [newAccount, setNewAccount] = useState({ name: '', email: '', password: '' });
  const [cookieData, setCookieData] = useState({ name: '', cookies: '' });

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const res = await axios.get(`${API_BASE}/accounts`);
      setAccounts(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleAddAccount = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/accounts`, newAccount);
      setIsModalOpen(false);
      setNewAccount({ name: '', email: '', password: '' });
      fetchAccounts();
    } catch (error) {
      alert(error.response?.data?.detail || 'Error adding account');
    }
  };

  const handleDelete = async (name) => {
    if (confirm(`Are you sure you want to delete ${name}?`)) {
      try {
        await axios.delete(`${API_BASE}/accounts/${name}`);
        fetchAccounts();
      } catch (error) {
        console.error(error);
      }
    }
  };

  const handleSaveCookies = async (e) => {
    e.preventDefault();
    try {
      const parsedCookies = JSON.parse(cookieData.cookies);
      await axios.post(`${API_BASE}/cookies`, {
        name: cookieData.name,
        cookies: parsedCookies
      });
      setIsCookieModalOpen(false);
      setCookieData({ name: '', cookies: '' });
      fetchAccounts();
    } catch (error) {
      alert(error.response?.data?.detail || 'Invalid JSON format or missing required cookies');
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Accounts</h1>
          <p className="page-subtitle">Manage your Facebook accounts and cookies</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <UserPlus size={18} /> Add Account
        </button>
      </div>

      <div className="glass-panel">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Account Name</th>
                <th>Email</th>
                <th>Cookies Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {accounts.length === 0 ? (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                    No accounts added yet.
                  </td>
                </tr>
              ) : (
                accounts.map((acc, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 500 }}>{acc.name}</td>
                    <td>{acc.email}</td>
                    <td>
                      {acc.has_cookies ? (
                        <span className="badge badge-success">Valid</span>
                      ) : (
                        <span className="badge badge-error">Missing</span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button 
                          className="btn btn-outline" 
                          style={{ padding: '6px 10px' }}
                          onClick={() => { setCookieData({ name: acc.name, cookies: '' }); setIsCookieModalOpen(true); }}
                        >
                          <Key size={16} /> Input Cookies
                        </button>
                        <button 
                          className="btn btn-danger" 
                          style={{ padding: '6px 10px' }}
                          onClick={() => handleDelete(acc.name)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Add Account */}
      {isModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 50
        }}>
          <div className="glass-panel" style={{ width: '400px', animation: 'fadeIn 0.3s ease-out' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>Add New Account</h2>
            <form onSubmit={handleAddAccount}>
              <div className="form-group">
                <label className="form-label">Account Name (Unique)</label>
                <input 
                  type="text" 
                  className="form-input" 
                  value={newAccount.name}
                  onChange={e => setNewAccount({...newAccount, name: e.target.value})}
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Facebook Email</label>
                <input 
                  type="email" 
                  className="form-input" 
                  value={newAccount.email}
                  onChange={e => setNewAccount({...newAccount, email: e.target.value})}
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input 
                  type="password" 
                  className="form-input" 
                  value={newAccount.password}
                  onChange={e => setNewAccount({...newAccount, password: e.target.value})}
                  required 
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '2rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Account</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Input Cookies */}
      {isCookieModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 50
        }}>
          <div className="glass-panel" style={{ width: '600px', animation: 'fadeIn 0.3s ease-out' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>Input Cookies for {cookieData.name}</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.875rem' }}>
              Export cookies as JSON from "Cookie-Editor" extension and paste here.
            </p>
            <form onSubmit={handleSaveCookies}>
              <div className="form-group">
                <textarea 
                  className="form-input" 
                  placeholder="[{...}, {...}]"
                  value={cookieData.cookies}
                  onChange={e => setCookieData({...cookieData, cookies: e.target.value})}
                  required 
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setIsCookieModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-accent">Validate & Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

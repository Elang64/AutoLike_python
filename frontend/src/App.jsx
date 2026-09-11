import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Settings, PlaySquare } from 'lucide-react';
import Dashboard from './components/Dashboard';
import Accounts from './components/Accounts';
import Config from './components/Config';
import RunBot from './components/RunBot';

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="logo-container">
            <PlaySquare className="logo-icon" size={32} />
            <span className="logo-text">Auto-Like Bot</span>
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
              <LayoutDashboard size={20} /> Dashboard
            </NavLink>
            <NavLink to="/accounts" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Users size={20} /> Accounts
            </NavLink>
            <NavLink to="/config" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Settings size={20} /> Configuration
            </NavLink>
            <NavLink to="/run" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <PlaySquare size={20} /> Run Bot
            </NavLink>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/accounts" element={<Accounts />} />
            <Route path="/config" element={<Config />} />
            <Route path="/run" element={<RunBot />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

import { NavLink, useLocation } from 'react-router-dom';
import {
  MessageSquare,
  LayoutDashboard,
  Database,
  History,
  Zap,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: MessageSquare, label: 'Soru Sor', desc: 'AI ile sorgula' },
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', desc: 'İstatistikler' },
  { to: '/schema', icon: Database, label: 'Şema', desc: 'Tablo yapıları' },
  { to: '/history', icon: History, label: 'Geçmiş', desc: 'Sorgu logları' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🤖</div>
        <div>
          <h1>Bruin</h1>
          <span>AI Veri Asistanı</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
            end={item.to === '/'}
          >
            <item.icon />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <div className="status-dot"></div>
          <Zap size={12} />
          <span>Gemini AI bağlı</span>
        </div>
      </div>
    </aside>
  );
}

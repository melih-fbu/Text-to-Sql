import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, CheckCircle, XCircle, Clock } from 'lucide-react';
import Header from '../components/Layout/Header';
import { getQueryStats, getQueryHistory } from '../utils/api';

const CHART_COLORS = ['#8ab4f8', '#c58af9', '#81c995', '#fdd663', '#f28b82', '#78d9ec'];

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [s, h] = await Promise.all([getQueryStats(), getQueryHistory(10)]);
      setStats(s);
      setHistory(h);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <>
        <Header title="📊 Dashboard" subtitle="Kullanım istatistikleri" />
        <div className="page-content">
          <div className="empty-state">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        </div>
      </>
    );
  }

  const statCards = [
    {
      title: 'Toplam Sorgu',
      value: stats?.total_queries || 0,
      icon: <Activity size={20} />,
      color: 'var(--accent-blue)',
      bg: 'rgba(138, 180, 248, 0.1)',
    },
    {
      title: 'Başarılı',
      value: stats?.successful_queries || 0,
      icon: <CheckCircle size={20} />,
      color: 'var(--accent-green)',
      bg: 'rgba(129, 201, 149, 0.1)',
    },
    {
      title: 'Hatalı',
      value: stats?.failed_queries || 0,
      icon: <XCircle size={20} />,
      color: 'var(--accent-red)',
      bg: 'rgba(242, 139, 130, 0.1)',
    },
    {
      title: 'Ort. Yanıt Süresi',
      value: `${(stats?.avg_execution_time_ms || 0).toFixed(0)}ms`,
      icon: <Clock size={20} />,
      color: 'var(--accent-purple)',
      bg: 'rgba(197, 138, 249, 0.1)',
    },
  ];

  const pieData = [
    { name: 'Başarılı', value: stats?.successful_queries || 0 },
    { name: 'Hatalı', value: stats?.failed_queries || 0 },
  ];

  return (
    <>
      <Header title="📊 Dashboard" subtitle="Bruin kullanım istatistikleri" />
      <div className="page-content">
        {/* Stats Cards */}
        <div className="stats-grid animate-in">
          {statCards.map((card, i) => (
            <div
              key={card.title}
              className="card"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="card-header">
                <span className="card-title">{card.title}</span>
                <div
                  className="card-icon"
                  style={{ background: card.bg, color: card.color }}
                >
                  {card.icon}
                </div>
              </div>
              <div className="card-value" style={{ color: card.color }}>
                {card.value}
              </div>
              {card.title === 'Toplam Sorgu' && stats?.success_rate != null && (
                <div className="card-change positive">
                  %{stats.success_rate} başarı oranı
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Charts */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20, marginBottom: 32 }}>
          <div className="card">
            <div className="card-title" style={{ marginBottom: 20 }}>Son Sorgular</div>
            {history.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={history.slice(0, 10).reverse()}>
                  <XAxis dataKey="id" stroke="var(--text-muted)" fontSize={11} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar
                    dataKey="execution_time_ms"
                    name="Süre (ms)"
                    fill="var(--accent-blue)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: 40, textAlign: 'center' }}>
                Henüz sorgu yok. Soru Sor sayfasından başlayın!
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-title" style={{ marginBottom: 20 }}>Başarı Oranı</div>
            {(stats?.total_queries || 0) > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, idx) => (
                      <Cell key={idx} fill={idx === 0 ? 'var(--accent-green)' : 'var(--accent-red)'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: 40, textAlign: 'center' }}>
                Veri bekleniyor...
              </div>
            )}
          </div>
        </div>

        {/* Recent Queries */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Son Sorular</div>
          {history.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Soru</th>
                    <th>Durum</th>
                    <th>Süre</th>
                    <th>Satır</th>
                  </tr>
                </thead>
                <tbody>
                  {history.slice(0, 5).map((q) => (
                    <tr key={q.id}>
                      <td style={{ maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {q.question}
                      </td>
                      <td>
                        <span className={`status-badge ${q.status}`}>
                          {q.status === 'success' ? '✓ Başarılı' : '✗ Hata'}
                        </span>
                      </td>
                      <td>{q.execution_time_ms ? `${q.execution_time_ms.toFixed(0)}ms` : '-'}</td>
                      <td>{q.row_count ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: 20 }}>
              Henüz sorgu yapılmamış.
            </div>
          )}
        </div>
      </div>
    </>
  );
}

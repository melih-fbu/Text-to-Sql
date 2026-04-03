import { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import Header from '../components/Layout/Header';
import { getQueryHistory } from '../utils/api';

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuery, setSelectedQuery] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getQueryHistory(100);
      setHistory(data);
    } catch (err) {
      console.error('History load error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Header title="📜 Sorgu Geçmişi" subtitle={`${history.length} sorgu kaydı`} />
      <div className="page-content">
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
          <button
            className="suggestion-chip"
            onClick={loadHistory}
            style={{ display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <RefreshCw size={14} />
            Yenile
          </button>
        </div>

        {loading ? (
          <div className="empty-state">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        ) : history.length === 0 ? (
          <div className="empty-state animate-in">
            <div className="empty-state-icon">📜</div>
            <div className="empty-state-title">Henüz sorgu yok</div>
            <div className="empty-state-desc">
              Soru Sor sayfasından ilk sorunuzu sorun, burada görünecek.
            </div>
          </div>
        ) : (
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ overflowX: 'auto' }}>
              <table className="history-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Soru</th>
                    <th>Durum</th>
                    <th>Süre</th>
                    <th>Satır</th>
                    <th>Kanal</th>
                    <th>Tarih</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((q) => (
                    <tr
                      key={q.id}
                      onClick={() => setSelectedQuery(selectedQuery?.id === q.id ? null : q)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td style={{ color: 'var(--text-muted)' }}>{q.id}</td>
                      <td style={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {q.question}
                      </td>
                      <td>
                        <span className={`status-badge ${q.status}`}>
                          {q.status === 'success' ? '✓' : '✗'} {q.status === 'success' ? 'Başarılı' : 'Hata'}
                        </span>
                      </td>
                      <td>{q.execution_time_ms ? `${q.execution_time_ms.toFixed(0)}ms` : '-'}</td>
                      <td>{q.row_count ?? '-'}</td>
                      <td>
                        <span style={{
                          fontSize: '0.7rem',
                          background: 'var(--bg-input)',
                          padding: '2px 8px',
                          borderRadius: 8,
                          color: 'var(--text-muted)',
                        }}>
                          {q.channel}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                        {q.created_at ? new Date(q.created_at).toLocaleString('tr-TR') : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Query Detail Drawer */}
        {selectedQuery && (
          <div className="card animate-in" style={{ marginTop: 20 }}>
            <div className="card-header">
              <span className="card-title">Sorgu Detayı #{selectedQuery.id}</span>
              <button
                className="suggestion-chip"
                onClick={() => setSelectedQuery(null)}
              >
                ✕ Kapat
              </button>
            </div>
            <div style={{ fontSize: '0.85rem' }}>
              <p style={{ marginBottom: 12 }}>
                <strong style={{ color: 'var(--text-secondary)' }}>Soru:</strong>{' '}
                {selectedQuery.question}
              </p>
              {selectedQuery.generated_sql && (
                <div>
                  <strong style={{ color: 'var(--text-secondary)' }}>SQL:</strong>
                  <div className="message-sql">{selectedQuery.generated_sql}</div>
                </div>
              )}
              {selectedQuery.result_summary && (
                <p style={{ marginTop: 12 }}>
                  <strong style={{ color: 'var(--text-secondary)' }}>Özet:</strong>{' '}
                  {selectedQuery.result_summary}
                </p>
              )}
              {selectedQuery.error_message && (
                <p style={{ marginTop: 12, color: 'var(--accent-red)' }}>
                  <strong>Hata:</strong> {selectedQuery.error_message}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}

import { useState, useEffect } from 'react';
import { Database, Key, Hash } from 'lucide-react';
import Header from '../components/Layout/Header';
import { getSchema } from '../utils/api';

export default function SchemaPage() {
  const [schema, setSchema] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSchema();
  }, []);

  const loadSchema = async () => {
    try {
      const data = await getSchema();
      setSchema(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <>
        <Header title="🗄️ Veritabanı Şeması" subtitle="Tablo ve kolon yapıları" />
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

  if (error) {
    return (
      <>
        <Header title="🗄️ Veritabanı Şeması" subtitle="Tablo ve kolon yapıları" />
        <div className="page-content">
          <div className="empty-state">
            <div className="empty-state-icon">⚠️</div>
            <div className="empty-state-title">Şema yüklenemedi</div>
            <div className="empty-state-desc">{error}</div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header
        title="🗄️ Veritabanı Şeması"
        subtitle={`${schema?.tables?.length || 0} tablo keşfedildi`}
      />
      <div className="page-content">
        <div className="schema-grid">
          {schema?.tables?.map((table, i) => (
            <div
              key={table.table_name}
              className="schema-card animate-in"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="schema-card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Database size={16} style={{ color: 'var(--accent-blue)' }} />
                  <span className="schema-table-name">{table.table_name}</span>
                </div>
                <span className="schema-row-count">
                  {table.row_count?.toLocaleString()} satır
                </span>
              </div>
              <div className="schema-columns">
                {table.columns.map((col) => (
                  <div key={col.name} className="schema-column">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {col.pk ? (
                        <Key size={12} style={{ color: 'var(--accent-orange)' }} />
                      ) : (
                        <Hash size={12} style={{ color: 'var(--text-muted)' }} />
                      )}
                      <span className="schema-col-name">{col.name}</span>
                      {col.pk && <span className="schema-col-pk">PK</span>}
                    </div>
                    <span className="schema-col-type">{col.type}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

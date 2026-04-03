import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import Header from '../components/Layout/Header';
import { askBruin } from '../utils/api';

const SUGGESTIONS = [
  "Bu çeyrekte kaç anlaşma kapattık?",
  "En çok gelir getiren 5 temsilci kim?",
  "Satış hunimiz ne durumda?",
  "Geçen ay toplam gelirimiz ne kadar?",
  "Müşteri sağlık skoru ortalaması nedir?",
  "Hangi ürün en çok satılıyor?",
  "Bölgelere göre gelir dağılımı nasıl?",
  "Ortalama satış döngüsü kaç gün?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (question) => {
    const q = question || input.trim();
    if (!q || loading) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    setLoading(true);

    try {
      const res = await askBruin(q);
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: res.interpretation || res.message || 'Yanıt alınamadı.',
          sql: res.sql,
          data: res.data,
          confidence: res.confidence,
          executionTime: res.execution_time_ms,
          visualizationHint: res.visualization_hint,
          type: res.type,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'bot', text: `❌ Hata: ${err.message}`, type: 'error' },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <Header title="💬 Bruin'e Sor" subtitle="Doğal dil ile verilerinizi sorgulayın" />
      <div className="page-content">
        <div className="chat-container">
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty-state animate-in">
                <div className="empty-state-icon">🤖</div>
                <div className="empty-state-title">Merhaba! Ben Bruin.</div>
                <div className="empty-state-desc">
                  Şirket verileriniz hakkında herhangi bir soru sorun. SQL yazmaya gerek yok — ben hallederim!
                </div>
                <div className="suggestions">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      className="suggestion-chip"
                      onClick={() => handleSend(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className="message">
                <div className={`message-avatar ${msg.role}`}>
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-name">
                    {msg.role === 'user' ? 'Sen' : 'Bruin'}
                  </div>
                  <div className="message-text">
                    {msg.text.split('\n').map((line, j) => (
                      <p key={j}>{line || '\u00A0'}</p>
                    ))}
                  </div>

                  {/* Result table */}
                  {msg.data && msg.data.columns && msg.data.rows && msg.data.rows.length > 0 && (
                    <div className="result-table-wrapper">
                      <table className="result-table">
                        <thead>
                          <tr>
                            {msg.data.columns.map((col) => (
                              <th key={col}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {msg.data.rows.slice(0, 15).map((row, ri) => (
                            <tr key={ri}>
                              {row.map((cell, ci) => (
                                <td key={ci}>
                                  {cell != null ? String(cell) : 'NULL'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {msg.data.row_count > 15 && (
                        <div style={{ padding: '8px 12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          ... ve {msg.data.row_count - 15} satır daha
                        </div>
                      )}
                    </div>
                  )}

                  {/* SQL preview */}
                  {msg.sql && (
                    <details>
                      <summary style={{ fontSize: '0.75rem', color: 'var(--text-muted)', cursor: 'pointer', marginTop: 8 }}>
                        🔍 SQL Sorgusunu Göster
                      </summary>
                      <div className="message-sql">{msg.sql}</div>
                    </details>
                  )}

                  {/* Meta info */}
                  {msg.role === 'bot' && msg.type !== 'error' && (
                    <div className="message-meta">
                      {msg.executionTime && (
                        <span>⏱️ {msg.executionTime.toFixed(0)}ms</span>
                      )}
                      {msg.confidence != null && msg.confidence > 0 && (
                        <span>🎯 %{(msg.confidence * 100).toFixed(0)} güven</span>
                      )}
                      {msg.data?.row_count != null && (
                        <span>📋 {msg.data.row_count} satır</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message">
                <div className="message-avatar bot">🤖</div>
                <div className="message-content">
                  <div className="message-name">Bruin</div>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <div className="chat-input-wrapper">
              <textarea
                ref={inputRef}
                className="chat-input"
                placeholder='Bir soru sorun... Ör: "Bu çeyrekte toplam gelir ne kadar?"'
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={loading}
              />
              <button
                className="chat-send-btn"
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
                id="send-button"
              >
                <Send />
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

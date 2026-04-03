const API_BASE = '/api/v1';

export async function askBruin(question) {
  const res = await fetch(`${API_BASE}/chat/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getSchema() {
  const res = await fetch(`${API_BASE}/schemas/discover`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getQueryHistory(limit = 50) {
  const res = await fetch(`${API_BASE}/queries/history?limit=${limit}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getQueryStats() {
  const res = await fetch(`${API_BASE}/queries/stats`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

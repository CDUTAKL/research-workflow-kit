export async function postAction(endpoint: string, payload: object = {}) {
  const response = await fetch(`http://127.0.0.1:8765${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.error || data.output || 'dashboard action failed');
  }
  return data as { ok: boolean; output?: string; id?: string; target?: string };
}

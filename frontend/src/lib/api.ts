// API client for Chronicler
export const API_BASE = 'http://localhost:8004';

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  return res.json();
}

export async function fetchDocuments(type?: string) {
  const url = type ? `${API_BASE}/documents?doc_type=${type}` : `${API_BASE}/documents`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchDocument(path: string) {
  const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(path)}`);
  return res.json();
}

export async function fetchCharacters() {
  const res = await fetch(`${API_BASE}/characters`);
  return res.json();
}

export async function fetchLocations() {
  const res = await fetch(`${API_BASE}/locations`);
  return res.json();
}

export async function fetchElements() {
  const res = await fetch(`${API_BASE}/elements`);
  return res.json();
}

export async function searchVault(query: string) {
  const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  return res.json();
}

export async function fetchEntityMentions(entityType: string, entityName: string) {
  const res = await fetch(`${API_BASE}/entity/${entityType}/${encodeURIComponent(entityName)}`);
  return res.json();
}

export async function updateDocument(path: string, content: string, append: boolean = false) {
  const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(path)}/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, append }),
  });
  return res.json();
}

export async function createDocument(title: string, content: string, docType: string = 'note') {
  const res = await fetch(`${API_BASE}/documents/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, doc_type: docType }),
  });
  return res.json();
}

import { getApiBase, getToken } from './auth.js';

export async function apiFetch(path, options = {}) {
  const apiBase = getApiBase();
  const token = getToken();

  const url = apiBase.replace(/\/$/, '') + path;

  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');

  if (!(options.body instanceof FormData)) {
    if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  }

  if (token) headers.set('Authorization', `Bearer ${token}`);

  const res = await fetch(url, { ...options, headers });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const detail = (data && data.detail) ? data.detail : (typeof data === 'string' ? data : JSON.stringify(data));
    throw new Error(`HTTP ${res.status} ${res.statusText}\n${detail}`);
  }

  return data;
}

export function getHealth() {
  return apiFetch('/health', { method: 'GET' });
}

export function listLeads(params = {}) {
  const qs = new URLSearchParams();
  if (params.status) qs.set('status', params.status);
  if (params.intent) qs.set('intent', params.intent);
  if (params.min_score !== undefined && params.min_score !== '') qs.set('min_score', params.min_score);
  if (params.limit) qs.set('limit', params.limit);
  return apiFetch('/api/leads/?' + qs.toString(), { method: 'GET' });
}

export function getLead(leadId) {
  return apiFetch(`/api/leads/${encodeURIComponent(leadId)}`, { method: 'GET' });
}

export function addLeadNote(leadId, note) {
  return apiFetch(`/api/leads/${encodeURIComponent(leadId)}/notes`, {
    method: 'POST',
    body: JSON.stringify({ note }),
  });
}

export function addLeadEvent(leadId, event_type, metadata = {}) {
  return apiFetch(`/api/leads/${encodeURIComponent(leadId)}/events`, {
    method: 'POST',
    body: JSON.stringify({ event_type, metadata }),
  });
}

export function addLeadTask(leadId, title) {
  return apiFetch(`/api/leads/${encodeURIComponent(leadId)}/tasks`, {
    method: 'POST',
    body: JSON.stringify({ title }),
  });
}

export function recalcLeadScore(leadId) {
  return apiFetch(`/api/leads/${encodeURIComponent(leadId)}/score/recalculate`, { method: 'POST' });
}

export function listCampaigns(params = {}) {
  const qs = new URLSearchParams();
  if (params.region) qs.set('region', params.region);
  if (params.status) qs.set('status', params.status);
  if (params.limit) qs.set('limit', params.limit);
  return apiFetch('/api/campaigns?' + qs.toString(), { method: 'GET' });
}

export function createCampaign(payload) {
  return apiFetch('/api/campaigns', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listApprovedContent(limit = 20) {
  return apiFetch(`/api/content/approved?limit=${encodeURIComponent(limit)}`, { method: 'GET' });
}

export function approveContentPack(contentPackId, isApproved) {
  return apiFetch(`/api/content/${encodeURIComponent(contentPackId)}/approve`, {
    method: 'POST',
    body: JSON.stringify({ is_approved: !!isApproved }),
  });
}

export function listRecentHandoffs(limit = 20) {
  return apiFetch(`/api/handoff/recent?limit=${encodeURIComponent(limit)}`, { method: 'GET' });
}

export function createHandoff(payload) {
  return apiFetch('/api/handoff/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

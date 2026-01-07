export const TOKEN_KEY = 'splendid_api_token';
export const API_BASE_KEY = 'splendid_api_base';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token || '');
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getApiBase() {
  const stored = localStorage.getItem(API_BASE_KEY);
  if (stored && stored.trim()) return stored.trim().replace(/\/$/, '');
  return window.location.origin;
}

export function setApiBase(base) {
  const cleaned = (base || '').trim().replace(/\/$/, '');
  localStorage.setItem(API_BASE_KEY, cleaned);
}

export function requireAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = 'index.html';
  }
}

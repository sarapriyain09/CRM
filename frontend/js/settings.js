import { requireAuth, getApiBase, getToken, setApiBase, setToken, clearToken, API_BASE_KEY } from './auth.js';
import { getHealth } from './api.js';
import { renderHeader, toast } from './ui.js';

requireAuth();
renderHeader('settings');

const apiBaseEl = document.getElementById('apiBase');
const tokenEl = document.getElementById('token');
const healthResult = document.getElementById('healthResult');

apiBaseEl.value = localStorage.getItem(API_BASE_KEY) || '';
tokenEl.value = getToken() || '';

document.getElementById('saveBtn').addEventListener('click', () => {
  setApiBase(apiBaseEl.value);
  setToken(tokenEl.value.trim());
  toast('Saved.');
});

document.getElementById('clearBtn').addEventListener('click', () => {
  clearToken();
  localStorage.removeItem(API_BASE_KEY);
  apiBaseEl.value = '';
  tokenEl.value = '';
  toast('Cleared.');
  setTimeout(() => { window.location.href = 'index.html'; }, 200);
});

document.getElementById('healthBtn').addEventListener('click', async () => {
  healthResult.textContent = '';
  try {
    const out = await getHealth();
    healthResult.textContent = out.status || 'ok';
    toast('Health OK.');
  } catch (e) {
    toast(e.message || String(e));
  }
});

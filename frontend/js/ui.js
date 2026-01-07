import { clearToken, getApiBase, getToken } from './auth.js';

export function setActiveNav(current) {
  document.querySelectorAll('[data-nav]')?.forEach((a) => {
    if (a.getAttribute('data-nav') === current) a.classList.add('active');
  });
}

export function renderHeader(current) {
  const header = document.getElementById('appHeader');
  if (!header) return;

  const token = getToken();
  const apiBase = getApiBase();

  header.innerHTML = `
    <div class="header">
      <div class="brand">Splendid CRM</div>
      <nav class="nav">
        <a href="dashboard.html" data-nav="dashboard">Dashboard</a>
        <a href="leads.html" data-nav="leads">Leads</a>
        <a href="campaigns.html" data-nav="campaigns">Campaigns</a>
        <a href="handoffs.html" data-nav="handoffs">Handoffs</a>
        <a href="settings.html" data-nav="settings">Settings</a>
      </nav>
      <div style="display:flex; gap:10px; align-items:center;">
        <span class="badge">${escapeHtml(apiBase)}</span>
        <span class="badge">${token ? 'token: set' : 'token: missing'}</span>
        <button id="logoutBtn" class="secondary" type="button">Logout</button>
      </div>
    </div>
  `;

  setActiveNav(current);
  const btn = document.getElementById('logoutBtn');
  btn?.addEventListener('click', () => {
    clearToken();
    window.location.href = 'index.html';
  });
}

export function toast(msg) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = String(msg);
  el.style.display = 'block';
  setTimeout(() => (el.style.display = 'none'), 4500);
}

export function qs(name) {
  const u = new URL(window.location.href);
  return u.searchParams.get(name);
}

export function escapeHtml(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

export function formatDate(d) {
  if (!d) return '';
  try {
    return new Date(d).toLocaleString();
  } catch {
    return String(d);
  }
}

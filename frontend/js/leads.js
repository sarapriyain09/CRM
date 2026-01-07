import { requireAuth } from './auth.js';
import { listLeads } from './api.js';
import { renderHeader, toast, escapeHtml } from './ui.js';

requireAuth();
renderHeader('leads');

const statusEl = document.getElementById('status');
const intentEl = document.getElementById('intent');
const minScoreEl = document.getElementById('minScore');
const limitEl = document.getElementById('limit');
const tbody = document.querySelector('#leadTable tbody');
const countBadge = document.getElementById('countBadge');

async function load() {
  try {
    const resp = await listLeads({
      status: statusEl.value,
      intent: intentEl.value,
      min_score: minScoreEl.value,
      limit: limitEl.value || 50,
    });

    const items = resp.items || [];
    countBadge.textContent = String(items.length);

    tbody.innerHTML = items.map((l) => {
      return `<tr>
        <td>${escapeHtml(l.lead_id)}</td>
        <td>${escapeHtml(l.email || '')}</td>
        <td><span class="badge">${escapeHtml(l.status)}</span></td>
        <td><span class="badge">${escapeHtml(l.intent)}</span></td>
        <td>${escapeHtml(l.score)}</td>
        <td><a href="lead.html?id=${encodeURIComponent(l.lead_id)}">Open</a></td>
      </tr>`;
    }).join('');
  } catch (e) {
    toast(e.message || String(e));
  }
}

document.getElementById('applyBtn').addEventListener('click', load);
document.getElementById('refreshBtn').addEventListener('click', load);

load();

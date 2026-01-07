import { requireAuth } from './auth.js';
import { listRecentHandoffs } from './api.js';
import { renderHeader, toast, escapeHtml, formatDate } from './ui.js';

requireAuth();
renderHeader('handoffs');

const tbody = document.querySelector('#handoffTable tbody');

async function load() {
  try {
    const resp = await listRecentHandoffs(50);
    const items = resp.items || [];
    tbody.innerHTML = items.map((h) => {
      return `<tr>
        <td>${escapeHtml(h.handoff_id)}</td>
        <td><a href="lead.html?id=${encodeURIComponent(h.lead_id)}">${escapeHtml(h.lead_id)}</a></td>
        <td><span class="badge">${escapeHtml(h.target)}</span></td>
        <td>${escapeHtml(formatDate(h.created_at))}</td>
      </tr>`;
    }).join('');
  } catch (e) {
    toast(e.message || String(e));
  }
}

document.getElementById('refreshBtn').addEventListener('click', load);

load();

import { requireAuth } from './auth.js';
import { listLeads, listCampaigns, listRecentHandoffs } from './api.js';
import { renderHeader, toast, formatDate, escapeHtml } from './ui.js';

requireAuth();
renderHeader('dashboard');

const cardsEl = document.getElementById('cards');
const handoffTbody = document.querySelector('#handoffTable tbody');

function card(title, value) {
  return `<div class="card"><div class="h2">${escapeHtml(title)}</div><div style="font-size:26px;font-weight:800;">${escapeHtml(value)}</div></div>`;
}

async function load() {
  try {
    const [leadsResp, campaignsResp, handoffsResp] = await Promise.all([
      listLeads({ limit: 50 }),
      listCampaigns({ limit: 50 }),
      listRecentHandoffs(10),
    ]);

    const leads = leadsResp.items || [];
    const campaigns = campaignsResp.items || [];
    const handoffs = handoffsResp.items || [];

    const handoffsToday = handoffs.filter((h) => {
      const d = new Date(h.created_at);
      const now = new Date();
      return d.toDateString() === now.toDateString();
    }).length;

    cardsEl.innerHTML = [
      card('Total leads (latest 50)', leads.length),
      card('Campaigns (latest 50)', campaigns.length),
      card('Handoffs today', handoffsToday),
    ].join('');

    handoffTbody.innerHTML = handoffs.map((h) => {
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

load();

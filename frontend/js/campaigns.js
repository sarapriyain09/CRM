import { requireAuth } from './auth.js';
import { createCampaign, listCampaigns } from './api.js';
import { renderHeader, toast, escapeHtml } from './ui.js';

requireAuth();
renderHeader('campaigns');

const tbody = document.querySelector('#campaignTable tbody');

async function load() {
  try {
    const resp = await listCampaigns({ limit: 50 });
    const items = resp.items || [];
    tbody.innerHTML = items.map((c) => {
      return `<tr>
        <td>${escapeHtml(c.campaign_id)}</td>
        <td>${escapeHtml(c.name)}</td>
        <td>${escapeHtml(c.slug)}</td>
        <td>${escapeHtml(c.region)}</td>
        <td><span class="badge">${escapeHtml(c.target)}</span></td>
        <td><span class="badge">${escapeHtml(c.status)}</span></td>
      </tr>`;
    }).join('');
  } catch (e) {
    toast(e.message || String(e));
  }
}

document.getElementById('refreshBtn').addEventListener('click', load);

document.getElementById('createBtn').addEventListener('click', async () => {
  const payload = {
    name: document.getElementById('name').value.trim(),
    slug: document.getElementById('slug').value.trim(),
    region: document.getElementById('region').value.trim(),
    target: document.getElementById('target').value,
    offer: document.getElementById('offer').value.trim() || null,
    niche: document.getElementById('niche').value.trim() || null,
    status: document.getElementById('status').value.trim() || 'active',
  };

  if (!payload.name || !payload.slug || !payload.region) {
    toast('Name, Slug, and Region are required');
    return;
  }

  try {
    const out = await createCampaign(payload);
    document.getElementById('createResult').textContent = `campaign_id: ${out.campaign_id}`;
    toast('Campaign created.');
    await load();
  } catch (e) {
    toast(e.message || String(e));
  }
});

load();

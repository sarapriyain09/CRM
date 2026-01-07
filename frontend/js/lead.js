import { requireAuth } from './auth.js';
import { addLeadEvent, addLeadNote, addLeadTask, createHandoff, getLead, recalcLeadScore } from './api.js';
import { renderHeader, toast, qs, escapeHtml } from './ui.js';

requireAuth();
renderHeader('leads');

const leadId = qs('id');
const kv = document.getElementById('leadKv');
const scoreBadge = document.getElementById('scoreBadge');

function kvRow(k, v) {
  return `<div class="key">${escapeHtml(k)}</div><div class="val">${escapeHtml(v ?? '')}</div>`;
}

async function load() {
  if (!leadId) {
    toast('Missing lead id (use lead.html?id=123)');
    return;
  }
  try {
    const lead = await getLead(leadId);
    kv.innerHTML = [
      kvRow('ID', lead.id),
      kvRow('Email', lead.email),
      kvRow('Name', lead.full_name),
      kvRow('Phone', lead.phone),
      kvRow('Company', lead.company),
      kvRow('Region', lead.region),
      kvRow('Status', lead.status),
      kvRow('Intent', lead.intent),
      kvRow('Score', lead.score),
      kvRow('Source', lead.source_platform),
      kvRow('Source detail', lead.source_detail),
    ].join('');
    scoreBadge.textContent = `score: ${lead.score}`;
  } catch (e) {
    toast(e.message || String(e));
  }
}

document.getElementById('recalcBtn').addEventListener('click', async () => {
  try {
    const out = await recalcLeadScore(leadId);
    scoreBadge.textContent = `score: ${out.score}`;
    toast('Score recalculated.');
    await load();
  } catch (e) {
    toast(e.message || String(e));
  }
});

document.getElementById('addEventBtn').addEventListener('click', async () => {
  const eventType = document.getElementById('eventType').value.trim();
  if (!eventType) return toast('Event type is required');
  try {
    const out = await addLeadEvent(leadId, eventType, {});
    toast(`Event created: ${out.event_id}`);
    await load();
  } catch (e) {
    toast(e.message || String(e));
  }
});

document.getElementById('addNoteBtn').addEventListener('click', async () => {
  const note = document.getElementById('note').value.trim();
  if (!note) return toast('Note is required');
  try {
    const out = await addLeadNote(leadId, note);
    document.getElementById('noteResult').textContent = `note_id: ${out.note_id}`;
    toast('Note saved.');
    document.getElementById('note').value = '';
  } catch (e) {
    toast(e.message || String(e));
  }
});

document.getElementById('addTaskBtn').addEventListener('click', async () => {
  const title = document.getElementById('taskTitle').value.trim();
  if (!title) return toast('Task title is required');
  try {
    const out = await addLeadTask(leadId, title);
    document.getElementById('taskResult').textContent = `task_id: ${out.task_id}`;
    toast('Task created.');
    document.getElementById('taskTitle').value = '';
  } catch (e) {
    toast(e.message || String(e));
  }
});

document.getElementById('handoffBtn').addEventListener('click', async () => {
  const target = document.getElementById('handoffTarget').value;
  try {
    const out = await createHandoff({ lead_id: Number(leadId), target, reason: 'Manual handoff (UI)', payload: {} });
    document.getElementById('handoffResult').textContent = `handoff_id: ${out.handoff_id}`;
    toast('Handoff created.');
  } catch (e) {
    toast(e.message || String(e));
  }
});

load();

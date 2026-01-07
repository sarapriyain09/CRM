# Splendid CRM (MVP)

FastAPI + PostgreSQL backend for:
- Trend intelligence ingestion
- Campaign/content/post tracking (schema-ready)
- Lightweight CRM (leads, events, notes, tasks)
- Lead scoring + handoff to Splendid/CodLearn

## 1) Start PostgreSQL (Docker)

```powershell
cd d:\Five_Pillar\07Software\SplendidTechnology\CRM

docker compose up -d
```

This uses:
- DB: `crm`
- User: `crm_user`
- Pass: `crm_pass`
- Port: `5432`

## 2) Create Python env + install

Recommended Python: 3.12 or 3.13.

Note: Python 3.14 may fail to install dependencies (e.g. `pydantic-core`) until upstream wheels/tooling catch up.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3) Configure env

```powershell
Copy-Item .env.example .env
```

Edit `.env` if needed.

## 4) Run migrations

```powershell
.\.venv\Scripts\alembic upgrade head
```

## 5) Run API

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:
- `GET http://127.0.0.1:8000/health`

OpenAPI:
- `http://127.0.0.1:8000/docs`

## Auth (API key)

All `/api/*` endpoints require a Bearer token:

- Header: `Authorization: Bearer <API_KEY>`
- If missing/invalid: `401 {"detail":"..."}`

Set `API_KEY` in your `.env` (see `.env.example`).

Example:

```powershell
$API_BASE = 'http://127.0.0.1:8000'
$API_KEY = 'change_me'

curl -Method POST "$API_BASE/api/trends/ingest" `
	-Headers @{ Authorization = "Bearer $API_KEY"; "Content-Type" = "application/json" } `
	-Body '{"region":"UK","items":[{"source":"manual","topic":"AI website builder","metrics":{"interest":78},"features":{"recency_hours":6}}]}'
```

For n8n, set environment variables:

- `API_BASE` (example: `http://host.docker.internal:8000` if n8n runs in Docker)
- `API_KEY`

## n8n workflows

Workflow JSON exports live in `n8n/` and can be imported into n8n.

### Environment variables

- `API_BASE` (example: `http://host.docker.internal:8000` if n8n runs in Docker)
- `API_KEY`
- Optional (only if you use the included Email nodes):
	- `NOTIFY_FROM_EMAIL`
	- `NOTIFY_TO_EMAIL`

### Workflows

- `n8n/W1_Daily_Trends_To_ContentPacks.json`
	- Daily flow: ingest trends → create campaign(s) → generate content packs.
	- Uses a manual “Set (Items Manually)” placeholder instead of `/api/trends/fetch`.

- `n8n/W2_Approved_Content_To_Scheduled_Posts.json`
	- Every 2 hours: fetch approved content packs → schedule posts via `/api/posts/schedule`.

- `n8n/W3_Leads_Events_To_CRM_And_Handoff.json`
	- Webhooks → upsert lead → append lead event → recalculate score → if score ≥ 60 create handoff + create a follow-up task.
	- Webhook paths:
		- `POST /webhook/codlearn-webhook`
		- `POST /webhook/splendid-contact-webhook`

## Smoke test

- Automated API smoke test: `scripts/smoke.ps1`
- Runbook: `doc/runbook_smoke_test.md`

Tip: Run the script by its real path (e.g. `\.\scripts\smoke.ps1`) and pass `-ApiBase` as the server root (e.g. `http://127.0.0.1:8000`, not `.../api`).

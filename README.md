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

```powershell
python -m venv .venv
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
alembic upgrade head
```

## 5) Run API

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
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

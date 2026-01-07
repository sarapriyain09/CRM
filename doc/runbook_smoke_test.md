# Runbook: MVP smoke test (API + n8n)

This runbook helps you validate the end-to-end MVP flow on a fresh machine:

- Trends ingest → campaigns → content packs → approval → scheduling
- Lead upsert → events → score recalculation → (optional) handoff

## Preconditions

- Python 3.12 or 3.13
- PostgreSQL is running (via Docker Compose)
- Dependencies installed (`pip install -r requirements.txt`)
- Migrations are applied (`.\.venv\Scripts\alembic upgrade head`)
- API is running (`.\.venv\Scripts\python -m uvicorn app.main:app --reload`)
- You know your API key (`API_KEY` in `.env`)

Note: Python 3.14 may fail to install dependencies (e.g. `pydantic-core`) until upstream wheels/tooling catch up.

## Option A — Automated API smoke test (recommended)

Run the PowerShell smoke script.

```powershell
cd d:\Five_Pillar\07Software\SplendidTechnology\CRM

# Either set env var...
$env:API_KEY = 'change_me'

# ...or pass -ApiKey explicitly
.\scripts\smoke.ps1 -ApiBase "http://127.0.0.1:8000"
```

Notes:
- If your API is not on localhost, set `-ApiBase`.
- The script will create a new campaign slug each run.
- If the scoring rules don’t produce a score ≥ 60, it will skip the handoff step (that is still considered a pass for smoke testing).

To force the handoff path (score ≥ 60) in a single run:

```powershell
.\scripts\smoke.ps1 -ApiBase "http://127.0.0.1:8000" -ForceHandoff
```

Useful flags:

```powershell
.\scripts\smoke.ps1 -SkipTrends
.\scripts\smoke.ps1 -SkipContent
.\scripts\smoke.ps1 -SkipPosts
.\scripts\smoke.ps1 -SkipLead
.\scripts\smoke.ps1 -ForceHandoff
```

## Option B — Validate the n8n workflows

1) Import workflows from `n8n/`:
- `W1_Daily_Trends_To_ContentPacks.json`
- `W2_Approved_Content_To_Scheduled_Posts.json`
- `W3_Leads_Events_To_CRM_And_Handoff.json`

2) Configure n8n environment variables:
- `API_BASE`
- `API_KEY`
- Optional (Email node): `NOTIFY_FROM_EMAIL`, `NOTIFY_TO_EMAIL`

3) Run W1 once
- W1 currently uses a manual “Set (Items Manually)” node instead of `/api/trends/fetch`.
- This should create a campaign and generate content packs.

4) Approve at least one content pack
- You can do this from your admin tooling, or via the API:

```powershell
$API_BASE='http://127.0.0.1:8000'
$API_KEY='change_me'

# get approved candidates (or list packs from DB/admin)
$approved = Invoke-RestMethod -Method GET "$API_BASE/api/content/approved?limit=10" -Headers @{ Authorization = "Bearer $API_KEY" }

# approve a specific pack id (replace 123)
Invoke-RestMethod -Method POST "$API_BASE/api/content/123/approve" `
  -Headers @{ Authorization = "Bearer $API_KEY"; 'Content-Type'='application/json' } `
  -Body '{"is_approved":true}'
```

5) Run W2
- W2 should schedule posts via `/api/posts/schedule`.

6) Trigger W3 webhooks
- In n8n, open W3 and copy the production webhook URLs.
- Use the sample payloads in `scripts/sample_payloads/` to test.

## Troubleshooting

- 401 Unauthorized: confirm `Authorization: Bearer <API_KEY>` is sent.
- 400 on content generate: ensure `platforms` is a non-empty array.
- If content packs aren’t returned: check server logs; the generate endpoint returns `packs` and the script expects `packs[0].id`.

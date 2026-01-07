param(
  [string]$ApiBase = "http://127.0.0.1:8000",
  [string]$ApiKey = $env:API_KEY,
  [switch]$SkipTrends,
  [switch]$SkipContent,
  [switch]$SkipPosts,
  [switch]$SkipLead
)

$ErrorActionPreference = 'Stop'

function Assert-NotEmpty([string]$Value, [string]$Name) {
  if ([string]::IsNullOrWhiteSpace($Value)) {
    throw "$Name is required (pass -$Name or set env var $Name)."
  }
}

function Invoke-Api(
  [Parameter(Mandatory=$true)][ValidateSet('GET','POST','PUT','DELETE')][string]$Method,
  [Parameter(Mandatory=$true)][string]$Path,
  [Parameter(Mandatory=$false)]$Body
) {
  $uri = ($ApiBase.TrimEnd('/') + $Path)
  $headers = @{ Authorization = "Bearer $ApiKey" }

  if ($null -ne $Body) {
    $json = $Body | ConvertTo-Json -Depth 20
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType 'application/json' -Body $json
  }

  return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

Assert-NotEmpty $ApiBase 'ApiBase'
Assert-NotEmpty $ApiKey 'ApiKey'

Write-Host "== Splendid CRM smoke test ==" -ForegroundColor Cyan
Write-Host "API_BASE: $ApiBase" 

# 0) Basic health check (no auth)
try {
  $health = Invoke-RestMethod -Method GET -Uri ($ApiBase.TrimEnd('/') + '/health')
  Write-Host "Health: OK" -ForegroundColor Green
} catch {
  Write-Host "Health check failed. Is the API running at $ApiBase ?" -ForegroundColor Red
  throw
}

# 1) Trends ingest + top
if (-not $SkipTrends) {
  Write-Host "\n[1] Trends ingest" -ForegroundColor Cyan
  $ingestBody = @{ 
    region = 'UK'
    items = @(
      @{ source = 'manual'; topic = 'AI website builder'; metrics = @{ interest = 78 }; features = @{ recency_hours = 6 } },
      @{ source = 'manual'; topic = 'CRM for small business'; metrics = @{ interest = 65 }; features = @{ recency_hours = 12 } }
    )
  }

  $ingestResp = Invoke-Api -Method POST -Path '/api/trends/ingest' -Body $ingestBody
  Write-Host ("Ingested: {0}" -f ($ingestResp.ingested))

  Write-Host "[1b] Trends top" -ForegroundColor Cyan
  $topResp = Invoke-Api -Method GET -Path '/api/trends/top?region=UK&limit=5'
  Write-Host ("Top items: {0}" -f ($topResp.items | Measure-Object).Count)
}

# 2) Campaign create
Write-Host "\n[2] Create campaign" -ForegroundColor Cyan
$stamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$slug = "uk_smoke_$stamp"

$campaignBody = @{ 
  name = "UK Smoke Campaign $stamp"
  slug = $slug
  region = 'UK'
  target = 'codlearn'
  offer = 'Free prototype'
  niche = 'small_business'
  status = 'active'
}

$campaignResp = Invoke-Api -Method POST -Path '/api/campaigns' -Body $campaignBody
$campaignId = $campaignResp.campaign_id
Write-Host "Campaign: id=$campaignId slug=$slug" -ForegroundColor Green

# 3) Content generate + approve
$contentPackId = $null
$contentPackPlatform = $null

if (-not $SkipContent) {
  Write-Host "\n[3] Generate content packs" -ForegroundColor Cyan
  $contentBody = @{ 
    campaign_slug = $slug
    platforms = @('instagram','linkedin')
    target = 'codlearn'
    cta = @{ codlearn_url_template = 'https://www.codlearn.com/app/?utm_source={{platform}}&utm_campaign={{campaign_slug}}&utm_content={{variant}}' }
  }

  $contentResp = Invoke-Api -Method POST -Path '/api/content/generate' -Body $contentBody
  Write-Host ("Content packs created: {0}" -f $contentResp.created) -ForegroundColor Green

  if (($contentResp.packs | Measure-Object).Count -gt 0) {
    $first = $contentResp.packs[0]
    $contentPackId = $first.id
    if (-not $contentPackId) { $contentPackId = $first.content_pack_id }
    $contentPackPlatform = $first.platform
  }

  if (-not $contentPackId) {
    throw "No content pack id returned from /api/content/generate (expected packs[0].id)."
  }

  Write-Host "Approving content_pack_id=$contentPackId" -ForegroundColor Cyan
  $approveResp = Invoke-Api -Method POST -Path ("/api/content/{0}/approve" -f $contentPackId) -Body @{ is_approved = $true }
  Write-Host ("Approved: {0}" -f $approveResp.is_approved) -ForegroundColor Green

  Write-Host "[3b] List approved content" -ForegroundColor Cyan
  $approvedResp = Invoke-Api -Method GET -Path '/api/content/approved?limit=10'
  Write-Host ("Approved packs returned: {0}" -f ($approvedResp.packs | Measure-Object).Count)
}

# 4) Schedule a post
$postId = $null
if (-not $SkipPosts) {
  if (-not $contentPackId) {
    Write-Host "Skipping posts: no content_pack_id (use -SkipContent to skip both)." -ForegroundColor Yellow
  } else {
    Write-Host "\n[4] Schedule post" -ForegroundColor Cyan
    $platform = $contentPackPlatform
    if ([string]::IsNullOrWhiteSpace($platform)) { $platform = 'linkedin' }

    $scheduleBody = @{ 
      campaign_id = $campaignId
      content_pack_id = $contentPackId
      platform = $platform
      scheduled_at = (Get-Date).AddMinutes(10).ToString('o')
    }

    $scheduleResp = Invoke-Api -Method POST -Path '/api/posts/schedule' -Body $scheduleBody
    $postId = $scheduleResp.post_id
    Write-Host "Scheduled post_id=$postId status=$($scheduleResp.status)" -ForegroundColor Green
  }
}

# 5) Lead upsert + event + score recalc (+ optional handoff)
if (-not $SkipLead) {
  Write-Host "\n[5] Lead upsert" -ForegroundColor Cyan
  $email = "smoke_$stamp@example.com"
  $leadUpsertBody = @{ 
    email = $email
    full_name = 'Smoke Test Lead'
    region = 'UK'
    source_platform = 'other'
    source_detail = $slug
    intent = 'small_business'
    attributes = @{ campaign_slug = $slug; post_id = $postId }
  }

  $leadResp = Invoke-Api -Method POST -Path '/api/leads/upsert' -Body $leadUpsertBody
  $leadId = $leadResp.lead_id
  Write-Host "Lead: id=$leadId created=$($leadResp.created)" -ForegroundColor Green

  Write-Host "[5b] Add lead event" -ForegroundColor Cyan
  $eventBody = @{ 
    event_type = 'cta_clicked'
    event_at = (Get-Date).ToString('o')
    metadata = @{ campaign_slug = $slug; post_id = $postId; url = 'https://www.codlearn.com/app/' }
  }
  $eventResp = Invoke-Api -Method POST -Path ("/api/leads/{0}/events" -f $leadId) -Body $eventBody
  Write-Host "Event created: event_id=$($eventResp.event_id)" -ForegroundColor Green

  Write-Host "[5c] Recalculate score" -ForegroundColor Cyan
  $scoreResp = Invoke-Api -Method POST -Path ("/api/leads/{0}/score/recalculate" -f $leadId)
  Write-Host "Score: $($scoreResp.score) status=$($scoreResp.status) intent=$($scoreResp.intent)" -ForegroundColor Green

  if ($scoreResp.score -ge 60) {
    Write-Host "[5d] Create handoff (score >= 60)" -ForegroundColor Cyan
    $handoffBody = @{ 
      lead_id = $leadId
      target = 'splendid'
      reason = "Smoke test: score=$($scoreResp.score)"
      payload = @{ score = $scoreResp.score; campaign_slug = $slug }
    }
    $handoffResp = Invoke-Api -Method POST -Path '/api/handoff/create' -Body $handoffBody
    Write-Host "Handoff created: handoff_id=$($handoffResp.handoff_id)" -ForegroundColor Green

    Write-Host "[5e] Create follow-up task" -ForegroundColor Cyan
    $taskBody = @{ title = 'Follow up (sales-ready lead)'; due_at = (Get-Date).AddHours(2).ToString('o') }
    $taskResp = Invoke-Api -Method POST -Path ("/api/leads/{0}/tasks" -f $leadId) -Body $taskBody
    Write-Host "Task created: task_id=$($taskResp.task_id)" -ForegroundColor Green
  } else {
    Write-Host "Score < 60: skipping handoff/task (this is OK for smoke test)." -ForegroundColor Yellow
  }
}

Write-Host "\nSmoke test complete." -ForegroundColor Cyan

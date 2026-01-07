param(
  [string]$ApiHost = "127.0.0.1",
  [int]$Port = 8000,
  [int]$FallbackPort = 8001,
  [switch]$SkipDocker,
  [switch]$SkipMigrate,
  [switch]$InstallDeps,
  [switch]$NoReload,
  [switch]$OpenDocs
)

$ErrorActionPreference = 'Stop'

function Assert-FileExists([string]$Path, [string]$Help) {
  if (-not (Test-Path $Path)) {
    throw "$Help (missing: $Path)"
  }
}

function Try-Run([ScriptBlock]$Block) {
  try {
    & $Block
    return $true
  } catch {
    return $false
  }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $repoRoot

Write-Host "== Splendid CRM: run dev ==" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot"

# 0) Ensure .env exists (don't overwrite)
if (-not (Test-Path (Join-Path $repoRoot '.env'))) {
  if (Test-Path (Join-Path $repoRoot '.env.example')) {
    Copy-Item (Join-Path $repoRoot '.env.example') (Join-Path $repoRoot '.env')
    Write-Host "Created .env from .env.example" -ForegroundColor Yellow
  } else {
    Write-Host "No .env found (and no .env.example to copy)." -ForegroundColor Yellow
  }
}

# 1) Start Postgres (Docker)
if (-not $SkipDocker) {
  Assert-FileExists (Join-Path $repoRoot 'docker-compose.yml') "docker-compose.yml not found"
  Write-Host "\n[1] Starting PostgreSQL via docker compose..." -ForegroundColor Cyan
  $started = Try-Run { docker compose up -d }
  if (-not $started) {
    Write-Host "Docker compose failed. If you're using local PostgreSQL, rerun with -SkipDocker." -ForegroundColor Yellow
  } else {
    Write-Host "PostgreSQL container started (or already running)." -ForegroundColor Green
  }
}

# 2) Ensure venv exists
$venvPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
$venvPip = Join-Path $repoRoot '.venv\Scripts\pip.exe'
$venvAlembic = Join-Path $repoRoot '.venv\Scripts\alembic.exe'

Assert-FileExists $venvPython "Virtualenv not found. Create it first: py -3.13 -m venv .venv"

# 3) Optional: install deps
if ($InstallDeps) {
  Assert-FileExists (Join-Path $repoRoot 'requirements.txt') "requirements.txt not found"
  Write-Host "\n[2] Installing dependencies..." -ForegroundColor Cyan
  & $venvPip install -r (Join-Path $repoRoot 'requirements.txt')
  Write-Host "Dependencies installed." -ForegroundColor Green
}

# 4) Migrate
if (-not $SkipMigrate) {
  Assert-FileExists (Join-Path $repoRoot 'alembic.ini') "alembic.ini not found"
  Write-Host "\n[3] Running migrations..." -ForegroundColor Cyan
  & $venvAlembic upgrade head
  Write-Host "Migrations complete." -ForegroundColor Green
}

# 5) Run API (try Port, then fallback)
$reloadFlag = "--reload"
if ($NoReload) { $reloadFlag = $null }

function Run-Uvicorn([int]$p) {
  $args = @(' -m', 'uvicorn', 'app.main:app', '--host', $ApiHost, '--port', "$p")
  if ($reloadFlag) { $args += $reloadFlag }

  $url = "http://$ApiHost`:$p"
  Write-Host "\n[4] Starting API at $url" -ForegroundColor Cyan
  Write-Host "Docs: $url/docs" -ForegroundColor DarkCyan

  if ($OpenDocs) {
    Start-Process "$url/docs" | Out-Null
  }

  & $venvPython @args
}

try {
  Run-Uvicorn -p $Port
} catch {
  if ($Port -ne $FallbackPort) {
    Write-Host "\nAPI failed to start on port $Port. Trying fallback port $FallbackPort..." -ForegroundColor Yellow
    Run-Uvicorn -p $FallbackPort
  } else {
    throw
  }
}

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [switch]$SkipLive
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

$backendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $backendRoot

Write-Step "Checking /health"
$health = Invoke-RestMethod -Uri "$BaseUrl/health"
$health | ConvertTo-Json -Depth 6

Write-Step "Checking frozen primary demo"
$demoPrimary = Invoke-RestMethod -Uri "$BaseUrl/demo"
$demoPrimary | ConvertTo-Json -Depth 8

Write-Step "Checking frozen secondary demo"
$demoSecondary = Invoke-RestMethod -Uri "$BaseUrl/demo?dataset=secondary"
$demoSecondary | ConvertTo-Json -Depth 8

if ($SkipLive) {
    Write-Host "`nSkipped live upload/analyze flow." -ForegroundColor Yellow
    exit 0
}

$primaryFiles = @(
    (Resolve-Path ".\demo_papers\chextransfer_excerpt.pdf").Path,
    (Resolve-Path ".\demo_papers\supervised_transfer_scale_excerpt.pdf").Path,
    (Resolve-Path ".\demo_papers\finetuning_excerpt.pdf").Path
)

Write-Step "Uploading primary live sample"
$uploadJson = curl.exe -s -X POST "$BaseUrl/upload" `
    -F "files=@$($primaryFiles[0]);type=application/pdf" `
    -F "files=@$($primaryFiles[1]);type=application/pdf" `
    -F "files=@$($primaryFiles[2]);type=application/pdf"

$upload = $uploadJson | ConvertFrom-Json
$sessionId = $upload.session_id
$upload | ConvertTo-Json -Depth 8

if (-not $sessionId) {
    throw "Upload did not return a session_id."
}

Write-Step "Running /analyze for session $sessionId"
$analysis = Invoke-RestMethod -Uri "$BaseUrl/analyze/$sessionId" -Method Post
$analysis | ConvertTo-Json -Depth 10

Write-Step "Checking cached /results"
$results = Invoke-RestMethod -Uri "$BaseUrl/results/$sessionId"
$results | ConvertTo-Json -Depth 10

Write-Step "Running semantic search"
$search = Invoke-RestMethod -Uri "$BaseUrl/search/$sessionId?q=transfer%20learning"
$search | ConvertTo-Json -Depth 8

# 빠른 실행 래퍼 - 더블클릭 또는 PowerShell에서 .\run.ps1
$env:ANTHROPIC_API_KEY = "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"
$env:SLACK_BOT_TOKEN   = "xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAKrkEj"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Node.js 있는지 확인
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js가 없습니다. https://nodejs.org 에서 설치하세요." -ForegroundColor Red
    Read-Host "엔터를 누르면 종료"
    exit
}

Write-Host "어떻게 실행할까요?" -ForegroundColor Cyan
Write-Host "[1] 팀 CLI 터미널 (대화형)" -ForegroundColor White
Write-Host "[2] 전체 파이프라인 바로 실행 (Slack 전송)" -ForegroundColor White
Write-Host "[3] 연구만 실행" -ForegroundColor White
$choice = Read-Host "선택 (1/2/3)"

switch ($choice) {
    "1" { & "$scriptDir\team-cli.ps1" }
    "2" { node "$scriptDir\agent-team.js" run }
    "3" { node "$scriptDir\agent-team.js" research }
    default { & "$scriptDir\team-cli.ps1" }
}

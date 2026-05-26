# GitHub Actions 완전 자동 설정 스크립트
# 실행 방법: powershell -ExecutionPolicy Bypass -File setup_github_complete.ps1

$ErrorActionPreference = "Continue"
$ghPath = "C:\Program Files\GitHub CLI\gh.exe"

Write-Host "=== GitHub Actions 자동 설정 시작 ===" -ForegroundColor Cyan

# Step 1: GitHub 로그인
Write-Host "`n[1/6] GitHub 로그인..." -ForegroundColor Yellow
& $ghPath auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "브라우저가 열립니다. GitHub에서 Authorize 버튼을 클릭하세요." -ForegroundColor Green
    & $ghPath auth login --web --git-protocol https
}

# Step 2: 사용자명 가져오기
$username = & $ghPath api user --jq ".login" 2>$null
Write-Host "[2/6] GitHub 사용자: $username" -ForegroundColor Yellow

# Step 3: repo 생성 (이미 있으면 스킵)
Write-Host "`n[3/6] Repo 생성..." -ForegroundColor Yellow
$repoExists = & $ghPath repo view "$username/claude-routines" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $ghPath repo create claude-routines --private --description "Claude Code 자동화 루틴"
    Write-Host "Repo 생성 완료" -ForegroundColor Green
} else {
    Write-Host "Repo 이미 존재함" -ForegroundColor Green
}

# Step 4: remote 설정 및 push
Write-Host "`n[4/6] 코드 Push..." -ForegroundColor Yellow
Set-Location "C:\Users\wnsdu\OneDrive\Desktop\claude code"
$remotes = git remote -v 2>$null
if ($remotes -notmatch "origin") {
    git remote add origin "https://github.com/$username/claude-routines.git"
}
git push -u origin main --force 2>&1

# Step 5: Secrets 설정
Write-Host "`n[5/6] GitHub Secrets 설정..." -ForegroundColor Yellow
& $ghPath secret set NOTION_TOKEN --body "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"
& $ghPath secret set BEEMINDER_TOKEN --body "UqEa8mBaBXXxYvKfkHJU"
& $ghPath secret set ANTHROPIC_API_KEY --body "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"
& $ghPath secret set SLACK_BOT_TOKEN --body "xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAKrkEj"
Write-Host "Secrets 설정 완료" -ForegroundColor Green

# Step 6: Workflow 테스트 실행
Write-Host "`n[6/6] Workflow 테스트..." -ForegroundColor Yellow
& $ghPath workflow run notion-beeminder-daily.yml
Start-Sleep -Seconds 8
$runs = & $ghPath run list --workflow=notion-beeminder-daily.yml --limit=1 --json status,conclusion,url | ConvertFrom-Json
Write-Host "실행 상태: $($runs[0].status)" -ForegroundColor Green
Write-Host "URL: $($runs[0].url)" -ForegroundColor Cyan

Write-Host "`n=== 설정 완료! ===" -ForegroundColor Cyan
Write-Host "GitHub Actions가 활성화되었습니다." -ForegroundColor Green
Write-Host "- notion-beeminder-daily: 매일 23:00 KST 자동 실행" -ForegroundColor White
Write-Host "- self-growth-weekly: 매주 수요일 04:00 KST 자동 실행" -ForegroundColor White
Write-Host "컴퓨터가 꺼져있어도 GitHub 서버에서 실행됩니다." -ForegroundColor Green

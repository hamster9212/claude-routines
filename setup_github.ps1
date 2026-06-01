# GitHub 자동 설정 스크립트
# 실행 방법: PowerShell에서 .\setup_github.ps1 -GitHubPAT "ghp_xxxx" -GitHubUsername "your-username"

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubPAT,

    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,

    [string]$RepoName = "claude-routines"
)

$GH = "C:\Program Files\GitHub CLI\gh.exe"
$WorkDir = "C:\Users\wnsdu\OneDrive\Desktop\claude code"

Write-Host "=== GitHub 자동 설정 시작 ===" -ForegroundColor Green

# Step 1: gh CLI 인증
Write-Host "`n[1/5] GitHub CLI 인증..." -ForegroundColor Cyan
$env:GH_TOKEN = $GitHubPAT
& $GH auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "인증 확인 중..." -ForegroundColor Yellow
}

# Step 2: repo 생성
Write-Host "`n[2/5] GitHub repo 생성..." -ForegroundColor Cyan
Set-Location $WorkDir

# 이미 repo가 있는지 확인
$repoExists = & $GH repo view "$GitHubUsername/$RepoName" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Repo already exists: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Yellow
} else {
    # repo 생성
    & $GH repo create $RepoName --private --description "Claude AI 자동 루틴 (Notion, Beeminder, Slack)" 2>&1
    Write-Host "Repo created: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor Green
}

# Step 3: remote 설정 및 push
Write-Host "`n[3/5] git remote 설정 및 push..." -ForegroundColor Cyan
Set-Location $WorkDir

# main 브랜치로 변경
git branch -M main 2>&1

# remote 설정
$remoteExists = git remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0) {
    git remote set-url origin "https://$GitHubUsername`:$GitHubPAT@github.com/$GitHubUsername/$RepoName.git"
    Write-Host "Remote URL updated" -ForegroundColor Yellow
} else {
    git remote add origin "https://$GitHubUsername`:$GitHubPAT@github.com/$GitHubUsername/$RepoName.git"
    Write-Host "Remote added" -ForegroundColor Green
}

# push
git push -u origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Push 완료!" -ForegroundColor Green
} else {
    Write-Host "Push 실패. 에러 확인 필요" -ForegroundColor Red
}

# Step 4: GitHub Secrets 설정
Write-Host "`n[4/5] GitHub Secrets 설정..." -ForegroundColor Cyan
Set-Location $WorkDir

$secrets = @{
    "NOTION_TOKEN" = "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"
    "BEEMINDER_TOKEN" = "UqEa8mBaBXXxYvKfkHJU"
    "ANTHROPIC_API_KEY" = "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"
    "SLACK_BOT_TOKEN" = "xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAK"
    "SLACK_CHANNEL_ID" = "PENDING_USER_ID"  # Slack 토큰 갱신 후 User ID로 교체 필요
}

foreach ($secret in $secrets.GetEnumerator()) {
    $name = $secret.Key
    $value = $secret.Value
    Write-Host "  Setting secret: $name" -NoNewline
    echo $value | & $GH secret set $name --repo "$GitHubUsername/$RepoName" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
    }
}

# Step 5: workflow 수동 트리거 테스트
Write-Host "`n[5/5] Workflow 수동 실행 테스트..." -ForegroundColor Cyan
& $GH workflow run notion-beeminder-daily.yml --repo "$GitHubUsername/$RepoName" 2>&1
Start-Sleep -Seconds 3
& $GH run list --workflow=notion-beeminder-daily.yml --repo "$GitHubUsername/$RepoName" --limit=1 2>&1

Write-Host "`n=== 설정 완료 ===" -ForegroundColor Green
Write-Host "Repo URL: https://github.com/$GitHubUsername/$RepoName" -ForegroundColor White
Write-Host "Actions: https://github.com/$GitHubUsername/$RepoName/actions" -ForegroundColor White
Write-Host "`n주의: SLACK_CHANNEL_ID는 Slack 토큰 갱신 후 재설정 필요" -ForegroundColor Yellow

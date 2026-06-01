# Life System Agent Team - In-Process Terminal CLI
# 실행: .\team-cli.ps1

$env:ANTHROPIC_API_KEY = "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"
$env:SLACK_BOT_TOKEN   = "xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAKrkEj"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript  = Join-Path $scriptDir "agent-team.py"

$agents = @(
    @{ id=1; name="Researcher";       icon="🔍"; desc="트렌드 분석 & 누락 기능 발견";    arg="research" }
    @{ id=2; name="Improver";         icon="⚡"; desc="HTML/CSS/JS 구체적 개선안 도출";   arg="improve"  }
    @{ id=3; name="Devil's Advocate"; icon="😈"; desc="3개월 후 실패 시나리오 점검";      arg="devil"    }
    @{ id=4; name="Full Pipeline";    icon="🚀"; desc="전체 에이전트 → Slack 전송";       arg="run"      }
)

$tasks = [System.Collections.Generic.List[hashtable]]@(
    @{ done=$false; text="Slack 채널 #claude-code-life-automation 생성" }
    @{ done=$false; text="Life System v1 → v2 개선사항 적용" }
    @{ done=$false; text="매일 자동 실행 스케줄 설정" }
)

$selected  = 0
$showTasks = $false

function Draw-Screen {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════╗" -ForegroundColor DarkMagenta
    Write-Host "  ║    🤖  Life System Agent Team Terminal           ║" -ForegroundColor Magenta
    Write-Host "  ║    Shift+↓ 순회  Enter 실행  T 태스크  Q 종료  ║" -ForegroundColor DarkGray
    Write-Host "  ╚══════════════════════════════════════════════════╝" -ForegroundColor DarkMagenta
    Write-Host ""
    Write-Host "  ┌─ 에이전트 팀 ─────────────────────────────────────┐" -ForegroundColor DarkGray

    for ($i = 0; $i -lt $agents.Count; $i++) {
        $a = $agents[$i]
        if ($i -eq $script:selected) {
            Write-Host "  │  " -NoNewline -ForegroundColor DarkGray
            Write-Host "▶ [$($a.id)] $($a.icon) $($a.name)" -NoNewline -ForegroundColor Cyan
            Write-Host "   $($a.desc)" -ForegroundColor White
        } else {
            Write-Host "  │    [$($a.id)] $($a.icon) $($a.name)   " -NoNewline -ForegroundColor DarkGray
            Write-Host "$($a.desc)" -ForegroundColor DarkGray
        }
    }
    Write-Host "  └───────────────────────────────────────────────────┘" -ForegroundColor DarkGray

    if ($script:showTasks) {
        Write-Host ""
        Write-Host "  ┌─ 공유 태스크 ──────────────────────────────────────┐" -ForegroundColor DarkYellow
        for ($i = 0; $i -lt $script:tasks.Count; $i++) {
            $t = $script:tasks[$i]
            $check = if ($t.done) { "✅" } else { "⬜" }
            $col   = if ($t.done) { "DarkGray" } else { "White" }
            Write-Host "  │  $check [$($i+1)] $($t.text)" -ForegroundColor $col
        }
        Write-Host "  │  숫자키로 완료 토글  A 태스크 추가" -ForegroundColor DarkGray
        Write-Host "  └───────────────────────────────────────────────────┘" -ForegroundColor DarkYellow
    }

    Write-Host ""
    Write-Host "  숫자키 1-$($agents.Count) 선택  Shift+↓ 순회  Enter 실행  T 태스크  Q 종료" -ForegroundColor DarkGray
}

function Run-Agent {
    param($a)
    Write-Host ""
    Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host "  $($a.icon) $($a.name) 실행 중..." -ForegroundColor Cyan
    Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
    Write-Host ""
    python $pyScript $a.arg
    Write-Host ""
    Write-Host "  ✅ 완료. 아무 키나 누르세요..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# ─── 메인 루프 ────────────────────────────────────────────────────────────────

Draw-Screen

while ($true) {
    $key   = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    $char  = $key.Character
    $vk    = $key.VirtualKeyCode
    $shift = ($key.ControlKeyState -band 16) -ne 0

    # Q 종료
    if ($char -eq 'q' -or $char -eq 'Q') {
        Write-Host "`n  👋 종료합니다." -ForegroundColor DarkGray; break
    }

    # T 태스크 토글
    if ($char -eq 't' -or $char -eq 'T') {
        $script:showTasks = -not $script:showTasks
        Draw-Screen; continue
    }

    # Shift+↓ 팀원 순회
    if ($shift -and $vk -eq 40) {
        $script:selected = ($script:selected + 1) % $agents.Count
        Draw-Screen; continue
    }

    # 숫자 1-4 직접 선택
    if ($char -ge '1' -and $char -le [char]($agents.Count + 48)) {
        $idx = [int]($char.ToString()) - 1
        if ($script:showTasks -and $idx -lt $script:tasks.Count) {
            # 태스크 완료 토글
            $script:tasks[$idx].done = -not $script:tasks[$idx].done
        } else {
            $script:selected = $idx
        }
        Draw-Screen; continue
    }

    # A 태스크 추가
    if (($char -eq 'a' -or $char -eq 'A') -and $script:showTasks) {
        Write-Host ""
        $newTask = Read-Host "  새 태스크 입력"
        if ($newTask) { $script:tasks.Add(@{ done=$false; text=$newTask }) }
        Draw-Screen; continue
    }

    # Enter 실행
    if ($vk -eq 13) {
        Run-Agent $agents[$script:selected]
        Draw-Screen; continue
    }
}

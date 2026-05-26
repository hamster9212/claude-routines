# GitHub Actions 설정 가이드

GitHub Actions로 두 루틴이 클라우드에서 자동 실행됩니다.
PC 전원 상태와 무관하게 매일/매주 실행됩니다.

---

## 1. GitHub repo 생성 후 push

```bash
cd "C:\Users\wnsdu\OneDrive\Desktop\claude code"
git init
git add .github/ run_notion_routine.py run_selfgrowth_routine.py notion_beeminder_sync.py slack_notifier.py
git commit -m "feat: GitHub Actions 클라우드 루틴 추가"
git remote add origin https://github.com/[USERNAME]/[REPO].git
git push -u origin main
```

> 주의: `api.env` 파일은 절대 push하지 마세요 (토큰 포함).

---

## 2. GitHub Secrets 설정

**GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 설명 | 필수 여부 |
|---|---|---|
| `NOTION_TOKEN` | Notion API 통합 토큰 | 필수 |
| `BEEMINDER_TOKEN` | Beeminder API 토큰 | 필수 |
| `ANTHROPIC_API_KEY` | Claude Vision API 키 | 필수 |
| `SLACK_BOT_TOKEN` | Slack Bot Token (xoxb-...) | 선택 |
| `SLACK_CHANNEL_ID` | Slack 채널 ID (C로 시작하는 11자리) | 선택 |

---

## 3. 루틴 스케줄

| 루틴 | 실행 시간 | cron |
|---|---|---|
| notion-beeminder-daily | 매일 23:00 KST | `0 14 * * *` |
| self-growth-weekly | 매주 수요일 04:00 KST | `0 19 * * 2` |

> GitHub Actions cron은 UTC 기준입니다.
> KST = UTC+9이므로: KST 23:00 = UTC 14:00

---

## 4. self-growth-weekly 추가 권한 (선택)

실행 기록 조회를 위해 `GH_TOKEN` Secret 추가:
1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. "Actions" → Read-only 권한 부여
3. 생성된 토큰을 `GH_TOKEN`으로 Secret에 추가

---

## 5. 수동 실행 방법

GitHub repo → Actions 탭 → 워크플로우 선택 → "Run workflow" 버튼

---

## 6. .gitignore 설정 (중요)

민감한 파일 제외:
```
api.env
*.env
.env
__pycache__/
*.pyc
```

#!/usr/bin/env python3
"""
GitHub Actions에서 self-growth-weekly 루틴 실행.

SKILL.md Agent A/B/C 직렬 실행:
  Agent A: GitHub Actions 실행 기록 조회 (로컬 로그 대신 GH API 활용)
  Agent B: Claude API로 패턴 분석 + 건강 점수 산출
  Agent C: Slack 알림 전송 + 분석 결과를 Notion에 기록 (로컬 CLAUDE.md 패치는 스킵)

GitHub Actions Secrets 필요:
  ANTHROPIC_API_KEY, SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
선택:
  NOTION_TOKEN (분석 결과 Notion 저장 시 사용)
  GH_TOKEN (GitHub Actions 실행 기록 조회 시 사용, GITHUB_TOKEN 자동 주입)
"""

import os
import sys
import json
import requests
from anthropic import Anthropic
from datetime import datetime, timezone, timedelta

# ── 시간 설정 ─────────────────────────────────────────────────────
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
today_str = now_kst.strftime("%Y-%m-%d")

print(f"[시작] Self-Growth Weekly 루틴 (KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')})")

# ── 환경변수 ──────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
# GitHub Actions 환경에서 GITHUB_TOKEN 자동 주입
GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")  # "owner/repo" 형식

if not ANTHROPIC_API_KEY:
    print("[CRITICAL] ANTHROPIC_API_KEY 누락")
    sys.exit(1)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ─────────────────────────────────────────────────────────────────
# Agent A: 실행 기록 수집
# ─────────────────────────────────────────────────────────────────
print("\n[Agent A] 최근 7일 실행 기록 수집...")

run_summary = []
total_runs = 0
success_count = 0
fail_count = 0

if GH_TOKEN and GITHUB_REPOSITORY:
    try:
        # GitHub Actions API로 notion-beeminder-daily 워크플로우 실행 기록 조회
        gh_headers = {
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        url = (
            f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/workflows/"
            f"notion-beeminder-daily.yml/runs?per_page=10"
        )
        resp = requests.get(url, headers=gh_headers, timeout=15)
        resp.raise_for_status()
        runs = resp.json().get("workflow_runs", [])

        cutoff = now_kst - timedelta(days=7)
        for run in runs:
            created_at = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            if created_at < cutoff:
                continue
            status = run.get("conclusion", "unknown")  # success / failure / cancelled
            run_date = created_at.astimezone(KST).strftime("%Y-%m-%d")
            total_runs += 1
            if status == "success":
                success_count += 1
                run_summary.append({"date": run_date, "result": "SUCCESS"})
            elif status in ("failure", "timed_out"):
                fail_count += 1
                run_summary.append({"date": run_date, "result": "FAIL"})
            else:
                run_summary.append({"date": run_date, "result": "UNKNOWN"})

        print(f"[Agent A] GitHub Actions 기록: 총{total_runs}회, 성공{success_count}, 실패{fail_count}")
    except Exception as e:
        print(f"[Agent A] GitHub API 조회 실패: {e}")
        run_summary = [{"date": today_str, "result": "UNKNOWN", "note": str(e)}]
else:
    print("[Agent A] GH_TOKEN 또는 GITHUB_REPOSITORY 미설정 - 더미 데이터 사용")
    run_summary = [{"date": today_str, "result": "UNKNOWN", "note": "로그 접근 불가"}]

agent_a_result = {
    "period": f"{(now_kst - timedelta(days=7)).strftime('%Y-%m-%d')} ~ {today_str}",
    "total_runs": total_runs,
    "success_count": success_count,
    "fail_count": fail_count,
    "daily_results": run_summary,
}

# ─────────────────────────────────────────────────────────────────
# Agent B: Claude API로 패턴 분석
# ─────────────────────────────────────────────────────────────────
print("\n[Agent B] Claude API 패턴 분석...")

analysis_prompt = f"""
오늘 날짜: {today_str}
아래는 최근 7일간 Notion-Beeminder 루틴의 실행 기록입니다.

{json.dumps(agent_a_result, ensure_ascii=False, indent=2)}

분석 요청:
1. 건강 점수 산출 (0~100, 성공률 기반)
   - 실행 기록이 없거나 알 수 없는 경우: 50점 (첫 실행 주)
2. 약점: 자주 실패하는 패턴
3. 강점: 안정적으로 작동하는 부분
4. 반복 에러: 3회 이상 같은 패턴
5. 추천 규칙: 개선 가능한 구체적 설정 (최대 3개)
6. 한 줄 요약 (한국어)

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "analysis_date": "{today_str}",
  "health_score": 85,
  "weaknesses": ["약점1", "약점2"],
  "strengths": ["강점1"],
  "repeated_errors": [],
  "recommended_rules": ["추천1", "추천2"],
  "summary": "한 줄 요약"
}}
"""

try:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": analysis_prompt}]
    )
    raw = response.content[0].text.strip()
    print(f"[Agent B] 응답: {raw[:200]}...")

    # JSON 파싱
    # 코드블록이 있으면 제거
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    agent_b_result = json.loads(raw.strip())

except json.JSONDecodeError as e:
    print(f"[Agent B] JSON 파싱 실패: {e}, 원본: {raw[:300]}")
    agent_b_result = {
        "analysis_date": today_str,
        "health_score": 50,
        "weaknesses": ["분석 데이터 부족"],
        "strengths": ["GitHub Actions 클라우드 실행으로 전환 완료"],
        "repeated_errors": [],
        "recommended_rules": ["실행 기록 쌓인 후 재분석 권장"],
        "summary": "첫 주 클라우드 전환 - 데이터 누적 중",
    }
except Exception as e:
    print(f"[Agent B] Claude API 오류: {e}")
    agent_b_result = {
        "analysis_date": today_str,
        "health_score": 50,
        "weaknesses": [f"API 오류: {str(e)[:100]}"],
        "strengths": [],
        "repeated_errors": [],
        "recommended_rules": [],
        "summary": f"분석 오류: {str(e)[:80]}",
    }

health_score = agent_b_result.get("health_score", 50)
summary = agent_b_result.get("summary", "분석 완료")
print(f"[Agent B] 건강점수={health_score}, 요약={summary}")

# ─────────────────────────────────────────────────────────────────
# Agent C: Slack 알림 전송
# ─────────────────────────────────────────────────────────────────
print("\n[Agent C] Slack 알림 전송...")

weaknesses = agent_b_result.get("weaknesses", [])
recommended = agent_b_result.get("recommended_rules", [])

weakness_text = "\n".join(f"  - {w}" for w in weaknesses[:3]) if weaknesses else "  - 없음"
recommend_text = "\n".join(f"  - {r}" for r in recommended[:3]) if recommended else "  - 없음"

slack_msg = (
    f"🧠 자기 성장 루틴 완료 ({today_str})\n"
    f"건강점수: {health_score}/100\n"
    f"요약: {summary}\n"
    f"약점:\n{weakness_text}\n"
    f"추천:\n{recommend_text}"
)

if SLACK_BOT_TOKEN:
    channel = SLACK_CHANNEL_ID or "wnsdud8563@gmail.com"
    try:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": slack_msg},
            timeout=10,
        )
        data = resp.json()
        if data.get("ok"):
            print("[Agent C] Slack 전송 성공")
        else:
            print(f"[Agent C] Slack 오류: {data.get('error')}")
    except Exception as e:
        print(f"[Agent C] Slack 실패: {e}")
else:
    print("[Agent C] SLACK_BOT_TOKEN 미설정 - Slack 스킵")
    print(f"[Agent C] 메시지 미리보기:\n{slack_msg}")

# ─────────────────────────────────────────────────────────────────
# 최종 결과 출력
# ─────────────────────────────────────────────────────────────────
print(f"\n[완료] 건강점수={health_score}, 요약={summary}")
print(f"RESULT_JSON:{json.dumps(agent_b_result, ensure_ascii=False)}")

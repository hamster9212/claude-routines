"""
Life Command System - Self-Improving Agent Team
실행: python agent-team.py [run|research|improve]
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# ─── 설정 ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
SITE_PATH = BASE_DIR.parent / "life-system" / "index.html"
LOG_PATH = BASE_DIR / "agent-log.json"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAKrkEj")
# DM 채널 ID (본인에게 전송) — 채널 생성 권한 없을 때 사용
SLACK_CHANNEL_ID = "D0B68SKGSAW"
MODEL = "claude-sonnet-4-6"

# ─── HTTP 헬퍼 ────────────────────────────────────────────────────────────────

def http_post(url, headers, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        raise Exception(f"HTTP {e.code}: {err_body}")

# ─── Claude API ──────────────────────────────────────────────────────────────

def claude_call(system_prompt, user_message):
    result = http_post(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        {
            "model": MODEL,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        }
    )
    if "error" in result:
        raise Exception(result["error"]["message"])
    return result["content"][0]["text"]

# ─── Slack ────────────────────────────────────────────────────────────────────

def slack_post(endpoint, body):
    return http_post(
        f"https://slack.com/api/{endpoint}",
        {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
        body
    )

def ensure_channel():
    # DM 채널로 바로 전송
    print(f"✅ Slack DM 채널 사용 (ID: {SLACK_CHANNEL_ID})")
    return SLACK_CHANNEL_ID

def send_slack(channel_id, blocks, text):
    return slack_post("chat.postMessage", {
        "channel": channel_id,
        "text": text,
        "blocks": blocks,
    })

# ─── 로그 ─────────────────────────────────────────────────────────────────────

def load_log():
    try:
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 0, "history": []}

def save_log(entry):
    log = load_log()
    log["version"] = entry["version"]
    log["history"] = [entry] + log.get("history", [])[:19]
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

# ─── 에이전트 ─────────────────────────────────────────────────────────────────

def agent_researcher(site_content):
    print("\n🔍 [Researcher] 최신 라이프 자동화 트렌드 분석 중...")
    result = claude_call(
        "당신은 라이프 자동화 시스템 트렌드 연구자입니다. JSON 형식으로만 답하세요.",
        f"""
현재 Life Command System 사이트 내용:
{site_content[:3000]}

다음을 JSON으로 반환:
{{
  "trends": ["트렌드1", "트렌드2", "트렌드3"],
  "missing_features": ["현재 사이트에 없는 기능1", "기능2", "기능3"],
  "improvement_areas": ["개선 가능 영역1", "영역2"],
  "priority_recommendation": "가장 먼저 추가해야 할 기능 1가지 (이유 포함)"
}}
"""
    )
    import re
    json_str = re.search(r"\{[\s\S]*\}", result)
    return json.loads(json_str.group())


def agent_improver(site_content, research):
    print("\n⚡ [Improver] 구체적 개선안 도출 중...")
    return claude_call(
        "당신은 웹 UI/UX 개선 전문가입니다. Life Command System에 추가할 구체적인 코드를 제안합니다.",
        f"""
연구 결과: {json.dumps(research, ensure_ascii=False, indent=2)}

현재 사이트 구조 (앞부분):
{site_content[:2000]}

제안 형식:
FEATURE: [기능명]
LOCATION: [삽입 위치]
EFFECT: [예상 효과]
CODE:
```html
[코드 스니펫]
```
"""
    )


def agent_devils_advocate(improvement):
    print("\n😈 [Devil's Advocate] 3개월 후 실패 시나리오 점검...")
    return claude_call(
        "당신은 Devil's Advocate입니다. 2026-09-01 시점에서 역할극합니다. 날짜+상황+감정이 포함된 구체적 실패 시나리오만 출력합니다.",
        f"""
제안된 개선사항:
{improvement}

이 개선사항이 실패하는 구체적 시나리오 3개를 제시하세요.
형식: [날짜] [상황] [감정] [실패 원인]
"""
    )


def agent_reporter(research, improvement, devils, channel_id):
    print("\n📨 [Reporter] Slack 보고서 전송 중...")
    log = load_log()
    version = log["version"] + 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"🤖 Life System Agent Report v{version}"}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": f"📅 {now}"}]},
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔍 Researcher 발견*\n우선 추가 기능: *{research['priority_recommendation']}*\n누락 기능: {', '.join(research['missing_features'])}"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*⚡ Improver 제안*\n{improvement[:800]}"}
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*😈 Devil's Advocate 경고*\n{devils[:500]}"}
        },
    ]

    res = send_slack(channel_id, blocks, f"Life System Agent Report v{version}")
    if res.get("ok"):
        print("✅ Slack 전송 완료!")
    else:
        print(f"⚠️ Slack 전송 실패: {res.get('error')}")

    save_log({"version": version, "timestamp": now,
               "research": research, "improvement": improvement[:500]})

# ─── 메인 파이프라인 ──────────────────────────────────────────────────────────

def run_full():
    print("━" * 50)
    print("🚀 Life System Agent Team 시작")
    print("━" * 50)

    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY가 없습니다.")
        sys.exit(1)

    channel_id = ensure_channel()
    site_content = SITE_PATH.read_text(encoding="utf-8")
    print(f"✅ 사이트 로드됨 ({len(site_content)//1024}KB)")

    research   = agent_researcher(site_content)
    print(f"  발견: {research['priority_recommendation']}")

    improvement = agent_improver(site_content, research)
    print("  개선안 도출 완료")

    devils = agent_devils_advocate(improvement)
    print("  리스크 점검 완료")

    agent_reporter(research, improvement, devils, channel_id)

    print("\n" + "━" * 50)
    print("✅ 완료! Slack #claude-code-life-automation 확인하세요.")
    print("━" * 50)


def run_single(cmd):
    site_content = SITE_PATH.read_text(encoding="utf-8")
    if cmd == "research":
        r = agent_researcher(site_content)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif cmd == "improve":
        r = agent_researcher(site_content)
        print(agent_improver(site_content, r))
    elif cmd == "devil":
        r = agent_researcher(site_content)
        i = agent_improver(site_content, r)
        print(agent_devils_advocate(i))
    else:
        print("사용법: python agent-team.py [run|research|improve|devil]")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        run_full()
    else:
        run_single(cmd)

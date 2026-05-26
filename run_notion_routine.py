#!/usr/bin/env python3
"""
GitHub Actions에서 notion-beeminder-daily 루틴 실행.

SKILL.md STEP 1-4 내용을 직접 구현:
  STEP 1   : Notion 할일 DB 조회 (미완료 카운트, 날짜 범위 기준 적용)
  STEP 1-B : 대기중 뷰 확인
  STEP 2   : 패키지 DB 조회 (has_package_keyword=True 인 경우만)
  STEP 3   : notion_beeminder_sync.py 실행 (JSON 인자 전달)
  STEP 4   : Slack 알림 전송

GitHub Actions Secrets 필요:
  NOTION_TOKEN, BEEMINDER_TOKEN, ANTHROPIC_API_KEY, SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime, timezone, timedelta, date

# ── 시간 설정 ─────────────────────────────────────────────────────
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
today_str = now_kst.strftime("%Y-%m-%d")
today_date = now_kst.date()

print(f"[시작] Notion-Beeminder 루틴 (KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')})")

# ── 환경변수 ──────────────────────────────────────────────────────
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
BEEMINDER_TOKEN = os.environ.get("BEEMINDER_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "")

# 필수 환경변수 검증
missing = [k for k, v in {
    "NOTION_TOKEN": NOTION_TOKEN,
    "BEEMINDER_TOKEN": BEEMINDER_TOKEN,
}.items() if not v]

if missing:
    print(f"[CRITICAL] 필수 환경변수 누락: {', '.join(missing)}")
    sys.exit(1)

# ── Notion API 공통 헤더 ──────────────────────────────────────────
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

TODO_DB_ID = "6e5e0fc8-1e56-82f9-b751-87a3cf6d4f7a"
PACKAGE_DB_ID = "91d9e574-1704-4e69-bb7c-c2cc04465f2d"


def query_notion_db(db_id: str, filter_body: dict = None) -> list:
    """Notion DB 전체 조회 (pagination 처리)"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    body = filter_body or {}
    results = []
    while True:
        resp = requests.post(url, headers=NOTION_HEADERS, json=body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        body["start_cursor"] = data["next_cursor"]
    return results


def get_date_end(props: dict, field: str = "진행할 날짜") -> date | None:
    """날짜 속성의 end 날짜 반환 (없으면 None)"""
    date_prop = props.get(field, {})
    date_val = date_prop.get("date") or {}
    end_str = date_val.get("end")
    if end_str:
        try:
            return date.fromisoformat(end_str[:10])
        except ValueError:
            pass
    return None


def get_select_name(props: dict, field: str) -> str:
    """select 속성 값 반환"""
    select = props.get(field, {}).get("select") or {}
    return select.get("name", "")


# ── STEP 1: 할일 DB 미완료 카운트 ────────────────────────────────
print("[STEP 1] Notion 할일 DB 조회...")

pages = query_notion_db(TODO_DB_ID, {
    "filter": {
        "property": "완료",
        "checkbox": {"equals": False}
    }
})

company_count = 0
personal_count = 0
has_package_keyword = False

for page in pages:
    props = page.get("properties", {})

    # 민채 일정 제외
    schedule_type = get_select_name(props, "할일? 일정?")
    if schedule_type == "민채 일정":
        continue

    # 날짜 범위 확인: end 날짜가 내일 이후면 카운트 제외
    end_date = get_date_end(props)
    if end_date and end_date > today_date:
        continue  # 기한이 아직 안 됨 - 제외

    category = get_select_name(props, "할일 구분")

    if category == "회사 할 일":
        company_count += 1

        # 오늘 날짜 패키지 키워드 확인
        date_prop = props.get("진행할 날짜", {}).get("date") or {}
        start_str = date_prop.get("start", "")
        if start_str.startswith(today_str):
            title_parts = props.get("내용", {}).get("title", [])
            title_text = "".join(t.get("plain_text", "") for t in title_parts)
            if "패키지" in title_text:
                has_package_keyword = True

    elif category == "기타 할 일":
        personal_count += 1

print(f"[STEP 1] 회사 미완료={company_count}, 기타 미완료={personal_count}, 패키지키워드={has_package_keyword}")

# ── STEP 1-B: 대기중 DB 확인 ─────────────────────────────────────
print("[STEP 1-B] 대기중 할일 확인...")

# "대기중" 상태 필터 (완료=False + 상태=대기중)
try:
    waiting_pages = query_notion_db(TODO_DB_ID, {
        "filter": {
            "and": [
                {"property": "완료", "checkbox": {"equals": False}},
                {"property": "상태", "select": {"equals": "대기중"}}
            ]
        }
    })
    waiting_count = len(waiting_pages)
except Exception as e:
    print(f"[WARNING] 대기중 조회 실패 (상태 필드 없을 수 있음): {e}")
    # 상태 필드가 없을 수 있으므로 0으로 처리
    waiting_count = 0

print(f"[STEP 1-B] 대기중={waiting_count}개")

# ── STEP 2: 패키지 DB 조회 ───────────────────────────────────────
packages = []
if has_package_keyword:
    print("[STEP 2] 패키지 DB 조회...")
    try:
        pkg_pages = query_notion_db(PACKAGE_DB_ID)
        for pkg_page in pkg_pages:
            props = pkg_page.get("properties", {})

            def get_text(field):
                items = props.get(field, {})
                rich = items.get("rich_text") or items.get("title") or []
                return "".join(t.get("plain_text", "") for t in rich)

            packages.append({
                "name": get_text("패키지명"),
                "trigger": get_text("발동조건"),
                "step1": get_text("1단계"),
                "step2": get_text("2단계"),
                "step3": get_text("3단계"),
            })
        print(f"[STEP 2] 패키지 {len(packages)}개 로드")
    except Exception as e:
        print(f"[WARNING] 패키지 DB 조회 실패: {e}")
else:
    print("[STEP 2] 패키지 키워드 없음 - 스킵")

# ── STEP 3: notion_beeminder_sync.py 실행 ────────────────────────
print("[STEP 3] notion_beeminder_sync.py 실행...")

input_data = {
    "company_count": company_count,
    "personal_count": personal_count,
    "waiting_count": waiting_count,
    "has_package_keyword": has_package_keyword,
    "packages": packages,
}
json_arg = json.dumps(input_data, ensure_ascii=False)

result = subprocess.run(
    [sys.executable, "notion_beeminder_sync.py", json_arg],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)

print(result.stdout)
if result.stderr:
    print("[STDERR]", result.stderr[:2000])

# RESULT_JSON 파싱
slack_message = ""
result_json = {}
for line in result.stdout.splitlines():
    if line.startswith("RESULT_JSON:"):
        try:
            result_json = json.loads(line[len("RESULT_JSON:"):])
            slack_message = result_json.get("slack_message", "")
        except json.JSONDecodeError:
            pass

if result.returncode != 0:
    print(f"[ERROR] notion_beeminder_sync.py 종료코드: {result.returncode}")
    slack_message = slack_message or f"루틴 실행 오류 (종료코드: {result.returncode})"

# ── STEP 4: Slack 알림 ────────────────────────────────────────────
print("[STEP 4] Slack 알림 전송...")

if SLACK_BOT_TOKEN and (SLACK_CHANNEL_ID or True):
    condition1 = result_json.get("condition1_pass", False)
    condition2 = result_json.get("condition2_result", "skip")

    if condition1 and condition2 in ("pass", "skip"):
        emoji = "✅"
    else:
        emoji = "❌"

    final_msg = (
        f"{emoji} Notion-Beeminder 루틴 완료 ({today_str} KST)\n"
        f"회사 미완료: {company_count}개 | 기타 미완료: {personal_count}개 | 대기중: {waiting_count}개\n"
        f"{slack_message}"
    )

    channel = SLACK_CHANNEL_ID or "wnsdud8563@gmail.com"
    try:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": final_msg},
            timeout=10,
        )
        data = resp.json()
        if data.get("ok"):
            print("[Slack] 전송 성공")
        else:
            print(f"[Slack] 오류: {data.get('error')}")
    except Exception as e:
        print(f"[Slack] 실패: {e}")
else:
    print("[Slack] SLACK_BOT_TOKEN 미설정 - 스킵")

print(f"[완료] company={company_count}, personal={personal_count}, waiting={waiting_count}")
sys.exit(result.returncode)

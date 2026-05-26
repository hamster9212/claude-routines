#!/usr/bin/env python3
"""
GitHub Actions / Task Scheduler에서 notion-beeminder-daily 루틴 실행.

SKILL.md STEP 1-4 내용을 직접 구현:
  STEP 1   : Notion 할일 DB 조회 (미완료 카운트, 날짜 범위 기준 적용)
  STEP 1-B : 대기중 뷰 확인
  STEP 2   : 패키지 DB 조회 (has_package_keyword=True 인 경우만)
  STEP 3   : notion_beeminder_sync.py 실행 (JSON 인자 전달)
  STEP 4   : Slack 알림 전송

GitHub Actions Secrets / 환경변수 필요:
  NOTION_TOKEN, BEEMINDER_TOKEN, ANTHROPIC_API_KEY, SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
"""

import os
import sys
import json
import subprocess
import requests
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

# ── 다중 소스 환경변수 로드 ────────────────────────────────────────
def load_env():
    """여러 위치에서 환경변수 로드 (우선순위 순). Task Scheduler 환경에서도 동작."""
    sources = [
        Path.home() / ".claude" / "settings.json",
        Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/.claude/settings.local.json"),
        Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/.claude/settings.json"),
        Path.cwd() / ".claude" / "settings.local.json",
        Path.cwd() / ".claude" / "settings.json",
    ]

    for path in sources:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                for k, v in data.get("env", {}).items():
                    if v and not os.environ.get(k):
                        os.environ[k] = str(v)
        except Exception:
            pass

    # Hardcoded fallback (최후 수단)
    fallbacks = {
        "NOTION_TOKEN": "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",
        "BEEMINDER_TOKEN": "UqEa8mBaBXXxYvKfkHJU",
        "ANTHROPIC_API_KEY": "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",
        "SLACK_BOT_TOKEN": "xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAKrkEj",
        "SLACK_CHANNEL_ID": "U0B66D6H12S",
    }
    for k, v in fallbacks.items():
        if not os.environ.get(k):
            os.environ[k] = v

load_env()

# ── 시간 설정 ─────────────────────────────────────────────────────
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
today_str = now_kst.strftime("%Y-%m-%d")
today_date = now_kst.date()

# ── 로그 설정 ─────────────────────────────────────────────────────
def setup_logging():
    """로그 핸들러 설정: 콘솔 + ~/.claude/ + desktop logs/"""
    _logger = logging.getLogger("notion_routine")
    _logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # 콘솔
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    _logger.addHandler(ch)

    # ~/.claude/notion_beeminder.log
    try:
        p1 = Path.home() / ".claude" / "notion_beeminder.log"
        p1.parent.mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(p1, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
        fh.setFormatter(fmt)
        _logger.addHandler(fh)
    except Exception:
        pass

    # Desktop logs/ 날짜별
    try:
        log_dir = Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        dated = log_dir / f"notion_routine_{now_kst.strftime('%Y%m%d')}.log"
        fh2 = RotatingFileHandler(dated, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
        fh2.setFormatter(fmt)
        _logger.addHandler(fh2)
    except Exception:
        pass

    return _logger

logger = setup_logging()

def log(msg: str):
    try:
        logger.info(msg)
    except UnicodeEncodeError:
        logger.info(msg.encode("ascii", errors="replace").decode("ascii"))

log(f"[시작] Notion-Beeminder 루틴 (KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')})")

# ── 환경변수 ──────────────────────────────────────────────────────
NOTION_TOKEN    = os.environ.get("NOTION_TOKEN", "")
BEEMINDER_TOKEN = os.environ.get("BEEMINDER_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "U0B66D6H12S")

# 필수 환경변수 검증
missing = [k for k, v in {
    "NOTION_TOKEN": NOTION_TOKEN,
    "BEEMINDER_TOKEN": BEEMINDER_TOKEN,
}.items() if not v]

if missing:
    log(f"[CRITICAL] 필수 환경변수 누락: {', '.join(missing)}")
    sys.exit(1)

# ── Notion API 공통 헤더 ──────────────────────────────────────────
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

TODO_DB_ID    = "6e5e0fc8-1e56-82f9-b751-87a3cf6d4f7a"
PACKAGE_DB_ID = "91d9e574-1704-4e69-bb7c-c2cc04465f2d"


# ── 유틸 ─────────────────────────────────────────────────────────
def with_retry(func, max_retries=3, base_delay=2):
    """재시도 로직"""
    last_exc = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exc = e
            if attempt < max_retries - 1:
                wait = base_delay ** attempt
                log(f"[RETRY] 시도 {attempt+1}/{max_retries} 실패 ({type(e).__name__}), {wait}초 후 재시도")
                time.sleep(wait)
    raise last_exc


def query_notion_db(db_id: str, filter_body: dict = None) -> list:
    """Notion DB 전체 조회 (pagination 완전 처리, 재시도 포함)"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    body = filter_body or {}
    results = []

    while True:
        def _query(b=body):
            resp = requests.post(url, headers=NOTION_HEADERS, json=b, timeout=15)
            resp.raise_for_status()
            return resp.json()

        data = with_retry(_query)
        results.extend(data.get("results", []))

        if not data.get("has_more"):
            break
        body = dict(body)  # 복사본 생성
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
log("[STEP 1] Notion 할일 DB 조회...")

company_count = 0
personal_count = 0
has_package_keyword = False

try:
    pages = query_notion_db(TODO_DB_ID, {
        "filter": {
            "property": "완료",
            "checkbox": {"equals": False}
        }
    })

    for page in pages:
        try:
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

        except Exception as e:
            log(f"[STEP 1] 개별 페이지 처리 오류 (건너뜀): {e}")
            continue

except Exception as e:
    log(f"[STEP 1 ERROR] 할일 DB 조회 실패: {e}")
    log("[STEP 1] 카운트 0으로 계속 진행")

log(f"[STEP 1] 회사 미완료={company_count}, 기타 미완료={personal_count}, 패키지키워드={has_package_keyword}")


# ── STEP 1-B: 대기중 DB 확인 ─────────────────────────────────────
log("[STEP 1-B] 대기중 할일 확인...")
waiting_count = 0

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
    log(f"[STEP 1-B WARNING] 대기중 조회 실패 (상태 필드 없을 수 있음): {e}")
    waiting_count = 0

log(f"[STEP 1-B] 대기중={waiting_count}개")


# ── STEP 2: 패키지 DB 조회 ───────────────────────────────────────
packages = []

if has_package_keyword:
    log("[STEP 2] 패키지 DB 조회...")
    try:
        pkg_pages = query_notion_db(PACKAGE_DB_ID)
        for pkg_page in pkg_pages:
            try:
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
            except Exception as e:
                log(f"[STEP 2] 개별 패키지 처리 오류 (건너뜀): {e}")
                continue

        log(f"[STEP 2] 패키지 {len(packages)}개 로드")
    except Exception as e:
        log(f"[STEP 2 WARNING] 패키지 DB 조회 실패: {e}")
else:
    log("[STEP 2] 패키지 키워드 없음 - 스킵")


# ── STEP 3: notion_beeminder_sync.py 실행 ────────────────────────
log("[STEP 3] notion_beeminder_sync.py 실행...")

input_data = {
    "company_count": company_count,
    "personal_count": personal_count,
    "waiting_count": waiting_count,
    "has_package_keyword": has_package_keyword,
    "packages": packages,
}
json_arg = json.dumps(input_data, ensure_ascii=False)

# 스크립트 경로 결정 (절대경로 우선)
script_dir = Path(__file__).parent
sync_script = script_dir / "notion_beeminder_sync.py"
if not sync_script.exists():
    sync_script = Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/notion_beeminder_sync.py")

result_returncode = 1
slack_message = ""
result_json = {}

try:
    result = subprocess.run(
        [sys.executable, str(sync_script), json_arg],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )

    # stdout 로그 출력
    for line in result.stdout.splitlines():
        log(f"  [sync] {line}")

    if result.stderr:
        log(f"[STEP 3 STDERR] {result.stderr[:2000]}")

    # RESULT_JSON 파싱
    for line in result.stdout.splitlines():
        if line.startswith("RESULT_JSON:"):
            try:
                result_json = json.loads(line[len("RESULT_JSON:"):])
                slack_message = result_json.get("slack_message", "")
            except json.JSONDecodeError:
                pass

    result_returncode = result.returncode

    if result_returncode != 0:
        log(f"[STEP 3 ERROR] notion_beeminder_sync.py 종료코드: {result_returncode}")
        slack_message = slack_message or f"루틴 실행 오류 (종료코드: {result_returncode})"

except subprocess.TimeoutExpired:
    log("[STEP 3 ERROR] 120초 타임아웃 - 프로세스 강제 종료")
    slack_message = "루틴 타임아웃 (120초 초과)"
except Exception as e:
    log(f"[STEP 3 ERROR] subprocess 실행 오류: {e}")
    slack_message = f"루틴 실행 오류: {str(e)[:100]}"


# ── STEP 4: Slack 알림 ────────────────────────────────────────────
log("[STEP 4] Slack 알림 전송...")

if SLACK_BOT_TOKEN:
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

    # SLACK_CHANNEL_ID: 설정값 또는 fallback
    channel = SLACK_CHANNEL_ID or "U0B66D6H12S"

    def _slack():
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": final_msg},
            timeout=10,
        )
        data = resp.json()
        if data.get("ok"):
            return True
        raise RuntimeError(f"slack error: {data.get('error')}")

    try:
        with_retry(_slack, max_retries=3, base_delay=2)
        log("[STEP 4] Slack 전송 성공")
    except Exception as e:
        log(f"[STEP 4] Slack 전송 최종 실패: {e}")
        log(f"[STEP 4] 메시지 내용:\n{final_msg}")
else:
    log("[STEP 4] SLACK_BOT_TOKEN 미설정 - 스킵")


log(f"[완료] company={company_count}, personal={personal_count}, waiting={waiting_count}")
sys.exit(result_returncode)

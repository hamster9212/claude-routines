#!/usr/bin/env python3
"""
Notion → Beeminder 자동화 시스템

역할:
  - Beeminder API 데이터포인트 전송
  - Claude Vision API로 패키지 풀이 이미지 분석
  - 실행 로그 저장

호출 방식 (Scheduled task에서):
  python notion_beeminder_sync.py '<JSON>'

JSON 형식:
  {
    "company_count": 0,
    "personal_count": 0,
    "has_package_keyword": false,
    "packages": [
      {"name": "...", "trigger": "...", "step1": "...", "step2": "...", "step3": "..."}
    ],
    "image_url": "https://... or null"
  }
"""

import os
import sys
import json
import re
import time
import base64
from datetime import datetime
from pathlib import Path
import requests
from logging.handlers import RotatingFileHandler
import logging
from anthropic import Anthropic

# Load environment variables from multiple sources with priority
def load_env_from_multiple_sources():
    """
    환경변수 로드 우선순위:
    1. Windows 시스템 환경변수 (이미 로드됨)
    2. Project .claude/settings.local.json
    3. Project .claude/settings.json
    4. Global ~/.claude/settings.json
    """
    sources = [
        Path.cwd() / ".claude" / "settings.local.json",  # Project local
        Path.cwd() / ".claude" / "settings.json",         # Project global
        Path.home() / ".claude" / "settings.json",        # User global
    ]

    for settings_file in sources:
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    env_config = settings.get("env", {})
                    for key, value in env_config.items():
                        # 기존 환경변수가 없을 때만 로드 (우선순위 유지)
                        if value and not os.environ.get(key):
                            os.environ[key] = value
                            # 로그는 나중에 기록됨
            except Exception as e:
                pass  # Silent failure, continue with next source

load_env_from_multiple_sources()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_RECORD_DB_ID = os.environ.get("NOTION_RECORD_DB_ID", "da3f380eb56d4647ac53d495ba04f6a5")

# ── 설정 ─────────────────────────────────────────────────────────
BEEMINDER_USER     = "wnsdud9212"
BEEMINDER_API_BASE = "https://www.beeminder.com/api/v1"
BEEMINDER_TOKEN    = os.environ.get("BEEMINDER_TOKEN")
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY")

# Slack 지원
SLACK_BOT_TOKEN    = os.environ.get("SLACK_BOT_TOKEN")
SLACK_WEBHOOK_URL  = os.environ.get("SLACK_WEBHOOK_URL")
SLACK_CHANNEL_ID   = os.environ.get("SLACK_CHANNEL_ID")

NOTION_DAILY_GOAL  = "notion-daily"
PACKAGE_DAILY_GOAL = "package-daily"

COMPANY_THRESHOLD  = 1   # 1개 이상이면 벌금
PERSONAL_THRESHOLD = 2   # 2개 이상이면 벌금

# ── 로그 파일 경로 결정 (권한 문제 시 대체 위치) ─────────────────
def setup_log_file():
    """로그 파일 경로 설정 (권한 문제 시 대체 위치 사용)"""
    primary_log = Path.home() / ".claude" / "notion_beeminder.log"
    fallback_log = Path(os.environ.get("TEMP", "C:\\Users\\wnsdu\\AppData\\Local\\Temp")) / "notion_beeminder.log"

    # Primary 시도
    try:
        primary_log.parent.mkdir(parents=True, exist_ok=True)
        # 쓰기 권한 확인
        with open(primary_log, 'a', encoding='utf-8') as f:
            f.write("")
        return primary_log
    except (PermissionError, OSError):
        pass

    # Fallback 시도
    try:
        fallback_log.parent.mkdir(parents=True, exist_ok=True)
        with open(fallback_log, 'a', encoding='utf-8') as f:
            f.write("")
        return fallback_log
    except (PermissionError, OSError):
        pass

    # 모든 위치 실패 - 파일 로깅 비활성화
    return None

LOG_FILE = setup_log_file()

# ── 로깅 설정 (로테이션 지원) ───────────────────────────────────
logger = logging.getLogger("notion_beeminder")
logger.setLevel(logging.DEBUG)

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(console_formatter)

logger.addHandler(console_handler)

# 파일 핸들러 (로테이션: 10MB마다, 5개 백업 유지)
if LOG_FILE:
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        console_handler.emit(logging.LogRecord(
            logger.name, logging.WARNING, __file__, 0,
            f"[WARNING] 로그 파일 핸들러 설정 실패: {e}", (), None
        ))


# ── 유틸 ──────────────────────────────────────────────────────────
def log(msg: str):
    """로그 파일 + stdout 동시 출력 (유니코드 처리)"""
    try:
        logger.info(msg)
    except UnicodeEncodeError:
        logger.info(msg.encode("ascii", errors="replace").decode("ascii"))


def send_slack_message(message: str) -> bool:
    """Slack으로 메시지 전송 (webhook 또는 bot token)"""
    # Webhook 우선 시도
    if SLACK_WEBHOOK_URL:
        try:
            payload = {"text": message}
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                log(f"[Slack] webhook 전송 성공")
                return True
            else:
                log(f"[Slack] webhook 오류: {response.status_code}")
                return False
        except Exception as e:
            log(f"[Slack] webhook 실패: {e}")
            return False

    # Bot token 시도
    if SLACK_BOT_TOKEN and SLACK_CHANNEL_ID:
        try:
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
            payload = {"channel": SLACK_CHANNEL_ID, "text": message}
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                json=payload,
                headers=headers,
                timeout=10
            )
            data = response.json()
            if data.get("ok"):
                log(f"[Slack] bot 전송 성공")
                return True
            else:
                log(f"[Slack] bot 오류: {data.get('error')}")
                return False
        except Exception as e:
            log(f"[Slack] bot 실패: {e}")
            return False

    log("[Slack] 설정되지 않음 (SLACK_WEBHOOK_URL 또는 SLACK_BOT_TOKEN)")
    return False


# ── Beeminder ─────────────────────────────────────────────────────
def send_beeminder(goal_slug: str, value: float = 1.0, comment: str = "") -> bool:
    """Beeminder goal에 데이터포인트 전송 (재시도 3회)"""
    if not BEEMINDER_TOKEN:
        log("[ERROR] BEEMINDER_TOKEN 환경변수가 설정되지 않음")
        return False

    url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USER}/goals/{goal_slug}/datapoints.json"
    payload = {
        "timestamp": int(datetime.now().timestamp()),
        "value": value,
        "auth_token": BEEMINDER_TOKEN,
        "comment": comment,
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            log(f"[BEEMINDER OK] goal={goal_slug}, value={value}, comment={comment}")
            return True
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4초
                log(f"[BEEMINDER RETRY] 시도 {attempt+1}/{max_retries} 실패, {wait_time}초 대기 후 재시도")
                time.sleep(wait_time)
            else:
                log(f"[BEEMINDER ERROR] 최종 실패 - {e}")
                return False


# ── 파일 처리 ────────────────────────────────────────────────────
def file_to_base64(file_content: bytes) -> str | None:
    """파일을 Base64로 인코딩"""
    try:
        b64 = base64.b64encode(file_content).decode('utf-8')
        log(f"[BASE64] 인코딩 완료: {len(b64)} chars")
        return b64
    except Exception as e:
        log(f"[BASE64 ERROR] {e}")
        return None


def download_notion_file(url: str) -> bytes | None:
    """Notion 임시 파일 URL에서 파일 다운로드 (1시간 유효)"""
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        log(f"[NOTION FILE] 다운로드 완료: {len(resp.content)} bytes")
        return resp.content
    except Exception as e:
        log(f"[NOTION FILE ERROR] {e}")
        return None


def get_today_image_base64() -> str | None:
    """
    풀이 기록 DB에서 오늘 날짜 행의 이미지를 가져와
    Base64로 인코딩하여 반환. (클라우드 서비스 불필요)

    반환값: Base64 인코딩된 이미지 데이터 또는 None
    """
    if not NOTION_TOKEN:
        log("[ERROR] NOTION_TOKEN 환경변수가 설정되지 않음")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    # 오늘 날짜 행 검색
    query_url = f"https://api.notion.com/v1/databases/{NOTION_RECORD_DB_ID}/query"
    query_body = {
        "filter": {
            "property": "날짜",
            "date": {"equals": today}
        }
    }

    try:
        resp = requests.post(query_url, headers=headers, json=query_body, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        if not results:
            log(f"[NOTION] 오늘({today}) 풀이 기록 없음")
            return None

        page = results[0]
        page_id = page["id"]

        # 해당 페이지의 blocks 가져오기 (본문 이미지)
        blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        blocks_resp = requests.get(blocks_url, headers=headers, timeout=10)
        blocks_resp.raise_for_status()
        blocks = blocks_resp.json().get("results", [])

        file_url = None

        # 본문에서 이미지/파일 찾기
        for block in blocks:
            btype = block.get("type")
            if btype == "image":
                img = block["image"]
                if img.get("type") == "file":
                    file_url = img["file"].get("url")
                elif img.get("type") == "external":
                    file_url = img["external"].get("url")
            elif btype == "file":
                file_data = block.get("file", {})
                inner = file_data.get("file") or file_data.get("external") or {}
                file_url = inner.get("url")

            if file_url:
                break

        # 본문에 없으면 파일 속성에서 시도
        if not file_url:
            files_prop = page.get("properties", {}).get("풀이사진", {})
            files = files_prop.get("files", [])
            for f in files:
                if f.get("type") == "file":
                    file_url = f["file"].get("url")
                elif f.get("type") == "external":
                    file_url = f["external"].get("url")

                if file_url:
                    break

        if not file_url:
            log("[NOTION] 이미지를 찾을 수 없음")
            return None

        log(f"[NOTION] 파일 URL 획득: {file_url[:60]}...")

        # Notion 파일 다운로드 (1시간 이내 유효)
        file_content = download_notion_file(file_url)
        if not file_content:
            return None

        # Base64 인코딩
        b64_data = file_to_base64(file_content)
        if b64_data:
            log(f"[BASE64] Base64 데이터 준비 완료")
            return b64_data
        else:
            log("[BASE64] 인코딩 실패")
            return None

    except requests.exceptions.RequestException as e:
        log(f"[NOTION ERROR] {e}")
        return None


# ── Claude Vision ──────────────────────────────────────────────────
def parse_vision_response(text: str) -> tuple:
    """
    Vision API 응답을 견고하게 파싱.
    Returns: (passed: bool, reason: str)
    """
    try:
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # RESULT 라인 찾기
        result_line = None
        reason_lines = []
        found_reason = False

        for line in lines:
            if line.upper().startswith('RESULT:'):
                result_line = line
            elif line.upper().startswith('REASON:'):
                found_reason = True
                reason_lines.append(line.replace('REASON:', '').strip())
            elif found_reason:
                reason_lines.append(line)

        # RESULT 파싱
        if not result_line:
            log("[VISION PARSE] RESULT 라인을 찾을 수 없음")
            return False, "응답 형식 오류"

        passed = "PASS" in result_line.upper()

        # REASON 파싱
        reason = " ".join(reason_lines).strip() if reason_lines else "이유 없음"
        if not reason or reason == "REASON:":
            reason = "판단 이유 없음"

        return passed, reason

    except Exception as e:
        log(f"[VISION PARSE ERROR] {e}")
        return False, f"파싱 실패: {str(e)}"


def analyze_package_image(image_data: str, packages: list, is_base64: bool = True) -> tuple:
    """
    Claude Vision API로 풀이 사진이 패키지 3단계 구조를 따랐는지 검증.
    Returns: (passed: bool, reason: str)
    """
    if not ANTHROPIC_API_KEY:
        log("[ERROR] ANTHROPIC_API_KEY 환경변수가 설정되지 않음")
        return False, "API key missing"

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    package_text = "\n\n".join([
        f"[패키지명] {p.get('name', '')}\n"
        f"[발동조건] {p.get('trigger', '')}\n"
        f"[1단계] {p.get('step1', '')}\n"
        f"[2단계] {p.get('step2', '')}\n"
        f"[3단계] {p.get('step3', '')}"
        for p in packages
    ])

    prompt = f"""사진 속 풀이가 아래 3단계 구조를 따랐는지 판단해주세요.

[풀이 패키지 목록 (참고용)]
{package_text}

판단 기준:
- PASS 조건: 사진에 아래 3단계 구조가 모두 보여야 통과. 대충이라도 적혀 있고 실제로 그 단계를 이용한 것처럼 보이면 통과
  1단계: 해석 & 단순화 — 문제를 자기 언어로 다시 정리한 흔적. 짧은 메모라도 있고 이를 바탕으로 풀이를 전개했으면 OK
  2단계: Case 분리 — "한번에 안 보이면 case로 쪼개기"에 해당하는 흔적. 경우를 나눈 표시가 조금이라도 있으면 OK
  3단계: 발상 목록 — "각 case에 쓸 수 있는 도구 나열 후 선택해서 실행"에 해당하는 흔적. 도구/방법을 적고 그걸 사용한 것처럼 보이면 OK
- 탈락 조건: 해당 단계의 흔적 자체가 아예 없는 경우만 FAIL. 부실하거나 대충 적혀도 있으면 인정
- 손글씨 해독 품질은 판단에서 제외. 글씨가 흐리거나 알아보기 어려워도 구조가 보이면 PASS

응답 형식 (반드시 이 형식만 사용):
RESULT: PASS
REASON: 판단 이유 한 문장

또는

RESULT: FAIL
REASON: 어느 단계가 없는지 한 문장"""

    try:
        # 이미지 소스 구성 (Base64 또는 URL)
        if is_base64:
            image_source = {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_data
            }
        else:
            image_source = {
                "type": "url",
                "url": image_data
            }

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # 안정적인 최신 모델
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": image_source
                    },
                    {"type": "text", "text": prompt}
                ]
            }]
        )

        text = response.content[0].text.strip()
        log(f"[VISION] 원본 응답: {text[:100]}...")

        # 견고한 응답 파싱
        passed, reason = parse_vision_response(text)
        log(f"[VISION] 파싱 결과: RESULT={passed}, REASON={reason}")

        return passed, reason

    except Exception as e:
        log(f"[VISION ERROR] {type(e).__name__}: {e}")
        return False, f"API 호출 실패: {str(e)}"


# ── 환경변수 검증 ──────────────────────────────────────────────
def validate_env_vars():
    """
    환경변수 검증:
    - BEEMINDER_TOKEN: 필수 (없으면 에러 후 종료)
    - NOTION_TOKEN: 필수 (없으면 에러 후 종료)
    - ANTHROPIC_API_KEY: 선택 (없으면 경고만, 나머지는 진행)
    """
    # 필수 항목: 없으면 즉시 실패
    critical = {
        "NOTION_TOKEN": NOTION_TOKEN,
        "BEEMINDER_TOKEN": BEEMINDER_TOKEN,
    }

    # 선택 항목: 없으면 경고만
    optional = {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    }

    # 필수 검증
    missing_critical = [k for k, v in critical.items() if not v]
    if missing_critical:
        log(f"[CRITICAL] 필수 환경변수 누락: {', '.join(missing_critical)}")
        log("[ERROR] 스크립트를 종료합니다.")
        return False

    # 선택 검증
    for key, value in optional.items():
        if not value:
            log(f"[WARNING] {key} 환경변수가 설정되지 않음 - Vision API 기능 스킵")

    return True


# ── Notion 업데이트 ───────────────────────────────────────────
def update_notion_record(packages: list, condition1_pass: bool, condition2_result: str):
    """
    Notion 풀이 기록 DB에 검증 결과 자동 기록.
    사용자는 사진만 올리고, 나머지는 스크립트가 입력.
    """
    if not NOTION_TOKEN:
        log("[ERROR] NOTION_TOKEN 환경변수가 설정되지 않음")
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    # 오늘 날짜 행 검색
    query_url = f"https://api.notion.com/v1/databases/{NOTION_RECORD_DB_ID}/query"
    query_body = {
        "filter": {
            "property": "날짜",
            "date": {"equals": today}
        }
    }

    try:
        resp = requests.post(query_url, headers=headers, json=query_body, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        if not results:
            log("[NOTION UPDATE] 오늘 기록 없음 (아직 사진 안 올림)")
            return False

        page_id = results[0]["id"]

        # 검증 결과 결정
        if condition2_result == "pass":
            validation_result = "PASS"
        elif condition2_result == "fail":
            validation_result = "FAIL"
        else:  # skip
            validation_result = "SKIP"

        # 페이지 업데이트
        update_url = f"https://api.notion.com/v1/pages/{page_id}"
        update_body = {
            "properties": {
                "검증결과": {
                    "select": {"name": validation_result}
                }
            }
        }

        update_resp = requests.patch(update_url, headers=headers, json=update_body, timeout=10)
        update_resp.raise_for_status()

        log(f"[NOTION UPDATE] 검증결과 업데이트: {validation_result}")
        return True

    except requests.exceptions.RequestException as e:
        log(f"[NOTION UPDATE ERROR] {e}")
        return False


# ── 메인 ─────────────────────────────────────────────────────────
def main():
    log("=" * 60)
    log(f"START: Notion-Beeminder 자동화 시스템")
    log(f"[LOG] 로그 파일: {LOG_FILE if LOG_FILE else '(파일 로깅 비활성화 - 권한 문제)'}")

    # 환경변수 검증
    if not validate_env_vars():
        log("[ERROR] 환경변수 검증 실패")
        sys.exit(1)

    # JSON 인자 파싱
    if len(sys.argv) < 2:
        log("[ERROR] 인자 없음. 사용법: python script.py '<JSON>'")
        sys.exit(1)

    try:
        # UTF-8 BOM 처리 (Windows PowerShell이 생성할 수 있음)
        json_str = sys.argv[1]
        data = json.loads(json_str.encode().decode('utf-8-sig'))
    except json.JSONDecodeError as e:
        log(f"[ERROR] JSON 파싱 실패: {e}")
        sys.exit(1)

    company_count       = data.get("company_count", 0)
    personal_count      = data.get("personal_count", 0)
    waiting_count       = data.get("waiting_count", 0)
    has_package_keyword = data.get("has_package_keyword", False)
    packages            = data.get("packages", [])

    # ── 조건 0: 대기중 DB 확인 ────────────────────────────────────
    log(f"[조건0] 대기중 할일={waiting_count}개")

    if waiting_count > 0:
        log(f"[조건0 FAIL] 대기중 항목이 {waiting_count}개 있음 - 즉시 실패 처리")
        # 즉시 FAIL 처리
        slack_message = f"대기중 할일 {waiting_count}개 있음 - 먼저 처리해주세요"
        result = {
            "condition0_fail": True,
            "waiting_count": waiting_count,
            "condition1_pass": False,
            "condition2_result": "skip",
            "company_count": company_count,
            "personal_count": personal_count,
            "slack_message": slack_message,
        }
        log("RESULT_JSON: " + json.dumps(result, ensure_ascii=False))
        sys.exit(0)

    # ── 조건 1: 할일 완료 체크 ──────────────────────────────────
    log(f"[조건1] 회사 미완료={company_count}개 / 기타 미완료={personal_count}개")

    condition1_pass = (company_count < COMPANY_THRESHOLD) and (personal_count < PERSONAL_THRESHOLD)

    if condition1_pass:
        send_beeminder(
            NOTION_DAILY_GOAL, 1.0,
            f"할일 완료 - 회사:{company_count} 기타:{personal_count}"
        )
        log("[조건1 PASS] notion-daily value=1 전송")
    else:
        log(f"[조건1 FAIL] 회사={company_count}(기준<{COMPANY_THRESHOLD}), 기타={personal_count}(기준<{PERSONAL_THRESHOLD}) - 전송 안 함")

    # ── 조건 2: 패키지 풀이 검증 ────────────────────────────────
    condition2_result = "skip"  # skip | pass | fail

    if has_package_keyword:
        log(f"[조건2] '패키지' 키워드 발견 - 이미지 분석 시작")
        image_data = get_today_image_base64()
        if image_data:
            passed, reason = analyze_package_image(image_data, packages, is_base64=True)
            if passed:
                send_beeminder(
                    PACKAGE_DAILY_GOAL, 1.0,
                    f"패키지 검증 통과: {reason}"
                )
                condition2_result = "pass"
                log(f"[조건2 PASS] package-daily value=1 전송 - {reason}")
            else:
                condition2_result = "fail"
                log(f"[조건2 FAIL] 전송 안 함 - {reason}")
        else:
            condition2_result = "fail"
            log("[조건2 FAIL] 이미지 없음 - 전송 안 함")
    else:
        log("[조건2 SKIP] 오늘 패키지 키워드 없음")

    # ── Notion 자동 업데이트 ────────────────────────────────────
    # 검증 결과를 Notion에 직접 기록 (사용자가 입력 안 해도 됨)
    update_notion_record(packages, condition1_pass, condition2_result)

    # ── Slack 메시지 구성 ─────────────────────────────────────
    if condition1_pass and condition2_result in ("pass", "skip"):
        slack_message = "오늘 미션 완료! Beeminder 안전"
    else:
        msgs = []
        if not condition1_pass:
            msgs.append(
                f"미완료 할일 있음 - 회사: {company_count}개, 기타: {personal_count}개 / Beeminder 벌금 예정"
            )
        if condition2_result == "fail":
            msgs.append("패키지 풀이 인증 실패 / Beeminder 벌금 예정")
        slack_message = " | ".join(msgs)

    # Scheduled task가 읽을 수 있도록 결과 출력
    result = {
        "condition1_pass": condition1_pass,
        "condition2_result": condition2_result,
        "company_count": company_count,
        "personal_count": personal_count,
        "waiting_count": waiting_count,
        "slack_message": slack_message,
    }
    print(f"RESULT_JSON:{json.dumps(result, ensure_ascii=False)}")

    log(f"[Slack 예정 메시지] {slack_message}")
    log("END: 자동화 완료")
    log("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

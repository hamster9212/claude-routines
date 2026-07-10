#!/usr/bin/env python3
"""
proof-split: 하루 2조각 사진 인증 시스템 (Notion → Beeminder)

기존 notion-beeminder-daily 시스템을 대체한다.
실행 시간대에 따라 두 가지 모드로 동작한다 (GitHub Actions cron):
  - 낮 실행(13:05/13:35/14:05 KST): 오늘의 오전 조각만 즉시 검증
  - 자정 실행(00:05/00:35/01:05 KST): 어제의 오후 조각 정산 + 놓친 오전 보완 + 할일 체크

조각 규칙:
  - 오전 조각: 당일 00:00 ~ 13:00 사이에 인증 기록 행 + 사진 업로드 완료해야 함
  - 오후 조각: 당일 13:00 ~ 24:00 사이에 업로드 완료해야 함
  - 마감 후 행을 수정하면(last_edited_time이 창 밖) FAIL

거짓증명 차단:
  1. 업로드 시간 검증 - Notion 페이지 last_edited_time이 해당 조각 시간창 안이어야 함
  2. AI 엄격 판정 - 조각 목표표의 목표/기준과 사진을 Groq 무료 vision 모델
     (llama-4-scout)이 대조, 애매하면 무조건 FAIL. 크레딧 비용 0원.

시스템 장애 처리:
  - Groq 장애/한도초과 등 판정 자체가 불가능하면 해당 조각은 보류하고
    다음 cron(00:35, 01:05)이 재시도. 01:00 이후 실행에서도 장애면
    사용자 잘못이 아니므로 자동 PASS 처리(벌금 없음).

Beeminder:
  - 오전 PASS → proof-am +1 / 오후 PASS → proof-pm +1 (FAIL이면 미전송 → derail)
  - notion-daily 할일 체크(회사<1, 기타<2, 대기중=0)도 이 실행에 통합

중복 실행 방지 (GitHub Actions cron 3중 등록 대비):
  - 조각: Notion 검증결과가 이미 채워져 있으면 스킵
  - Beeminder: 해당 날짜 datapoint가 이미 있으면 미전송

사용법:
  python proof_split_verify.py                  # 실행 시각에 따라 낮/자정 모드 자동 결정
  python proof_split_verify.py --date 2026-07-03
  python proof_split_verify.py --dry-run        # Beeminder/Notion/Slack 쓰기 없음

필요 환경변수(GitHub Secrets):
  NOTION_TOKEN, BEEMINDER_TOKEN, GROQ_API_KEY, SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
"""

import os
import sys
import json
import time
import base64
import argparse
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone, timedelta, date, time as dtime
from pathlib import Path

import requests

# ── 시간 설정 ─────────────────────────────────────────────────────
KST = timezone(timedelta(hours=9))
AM_DEADLINE = dtime(13, 0)      # 오전 조각 마감
PM_DEADLINE = dtime(23, 59, 59) # 오후 조각 마감 (자정 = 하루 마지막 초)

# ── Notion DB ─────────────────────────────────────────────────────
# 2025-09-03 API부터 "데이터베이스"와 "데이터 소스"가 분리됨.
# 조회는 반드시 data source ID로 해야 함 (database 컨테이너 ID 아님).
PROOF_DB_ID = os.environ.get("PROOF_DB_ID", "1d565f54-273c-45f5-956b-de33f51a5655")   # 인증 기록 (data source)
GOALS_DB_ID = os.environ.get("GOALS_DB_ID", "acf7ba1e-9dc3-4b32-a695-d71feaf0a3d5")   # 조각 목표표 (data source)
TODO_DB_ID  = os.environ.get("TODO_DB_ID", "6e5e0fc8-1e56-82f9-b751-87a3cf6d4f7a")  # 할일 DB (data source, 기존)

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]
PLACEHOLDER_MARKERS = ("여기에 목표 입력", "AI 판정 기준 입력")

# ── Beeminder ─────────────────────────────────────────────────────
BEEMINDER_USER = "wnsdud9212"
BEEMINDER_API  = "https://www.beeminder.com/api/v1"
GOAL_AM     = "proof-am"
GOAL_PM     = "proof-pm"
GOAL_NOTION = "notion-daily"

COMPANY_THRESHOLD  = 1
PERSONAL_THRESHOLD = 2

# ── 환경변수 (secrets는 환경변수/설정 파일에서만 읽는다 - 하드코딩 금지) ──
def load_env():
    """로컬 실행 시 .claude/settings.json 계열에서 환경변수 보충"""
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

load_env()

NOTION_TOKEN      = os.environ.get("NOTION_TOKEN", "")
BEEMINDER_TOKEN   = os.environ.get("BEEMINDER_TOKEN", "")
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY", "")
SLACK_BOT_TOKEN   = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID  = os.environ.get("SLACK_CHANNEL_ID", "U0B66D6H12S")

# Groq 무료 vision 모델 (OpenAI 호환 API). 무료 한도: 1,000요청/일 - 하루 2회 사용
GROQ_API_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL     = "meta-llama/llama-4-scout-17b-16e-instruct"
# 마지막 재시도 판단 기준 시각 (이 시각 이후 실행에서 장애면 자동 PASS)
# 자정 실행(00:05/00:35/01:05 cron): 01:00 이후 / 낮 실행(13:05/13:35/14:05 cron): 14:00 이후
FINAL_ATTEMPT_HOUR_NIGHT = 1
FINAL_ATTEMPT_HOUR_DAY   = 14

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}

# ── 로깅 ─────────────────────────────────────────────────────────
def setup_logging():
    _logger = logging.getLogger("proof_split")
    _logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    _logger.addHandler(ch)

    for log_dir in [Path.home() / ".claude",
                    Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/logs")]:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            fh = RotatingFileHandler(
                log_dir / f"proof_split_{datetime.now(KST).strftime('%Y%m%d')}.log",
                maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8",
            )
            fh.setFormatter(fmt)
            _logger.addHandler(fh)
        except Exception:
            pass
    return _logger

logger = setup_logging()

def log(msg: str):
    try:
        logger.info(msg)
    except UnicodeEncodeError:
        logger.info(msg.encode("ascii", errors="replace").decode("ascii"))


# ── headroom 압축 (선택적) ─────────────────────────────────────────
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import headroom as _headroom

    def hr_compress(text: str, label: str = "") -> str:
        try:
            res = _headroom.compress_text(text, reversible=False)
            if res.saved > 0:
                log(f"[headroom] {label} 압축: {res.before_tokens}→{res.after_tokens} 토큰")
            return res.text
        except Exception:
            return text
except Exception:
    def hr_compress(text: str, label: str = "") -> str:
        return text


def with_retry(func, max_retries=3, base_delay=2):
    last_exc = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exc = e
            if attempt < max_retries - 1:
                wait = base_delay ** attempt
                log(f"[RETRY] {attempt+1}/{max_retries} 실패 ({type(e).__name__}), {wait}초 후 재시도")
                time.sleep(wait)
    raise last_exc


# ── Notion 공통 ───────────────────────────────────────────────────
def query_notion_db(db_id: str, filter_body: dict | None = None) -> list:
    """db_id는 반드시 data source ID (database 컨테이너 ID 아님)."""
    url = f"https://api.notion.com/v1/data_sources/{db_id}/query"
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
        body = dict(body)
        body["start_cursor"] = data["next_cursor"]
    return results


def get_rich_text(props: dict, field: str) -> str:
    items = props.get(field, {})
    rich = items.get("rich_text") or items.get("title") or []
    return "".join(t.get("plain_text", "") for t in rich)


def get_select_name(props: dict, field: str) -> str:
    select = props.get(field, {}).get("select") or {}
    return select.get("name", "")


def parse_notion_time_kst(iso_str: str) -> datetime:
    """Notion의 UTC ISO 시각 → KST datetime"""
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.astimezone(KST)


def update_proof_row(page_id: str, result: str, reason: str, upload_time: str, dry_run: bool):
    if dry_run:
        log(f"[DRY-RUN] Notion 업데이트 생략: {result} / {reason}")
        return
    body = {
        "properties": {
            "검증결과": {"select": {"name": result}},
            "판정이유": {"rich_text": [{"text": {"content": reason[:1900]}}]},
            "업로드시각": {"rich_text": [{"text": {"content": upload_time}}]},
        }
    }
    def _update():
        resp = requests.patch(f"https://api.notion.com/v1/pages/{page_id}",
                              headers=NOTION_HEADERS, json=body, timeout=15)
        resp.raise_for_status()
        return True
    with_retry(_update)
    log(f"[NOTION] 검증결과 기록: {result}")


def create_missing_row(target: date, piece: str, dry_run: bool):
    """미제출 조각의 행을 자동 생성해 기록을 남긴다 (중복 실행 방지 겸용)"""
    if dry_run:
        log(f"[DRY-RUN] 미제출 행 생성 생략: {target} {piece}")
        return
    body = {
        "parent": {"data_source_id": PROOF_DB_ID},
        "properties": {
            "이름": {"title": [{"text": {"content": f"{target.isoformat()} {piece} (미제출)"}}]},
            "날짜": {"date": {"start": target.isoformat()}},
            "조각": {"select": {"name": piece}},
            "검증결과": {"select": {"name": "미제출"}},
            "판정이유": {"rich_text": [{"text": {"content": "마감까지 인증 행/사진 없음"}}]},
        },
    }
    def _create():
        resp = requests.post("https://api.notion.com/v1/pages",
                             headers=NOTION_HEADERS, json=body, timeout=15)
        resp.raise_for_status()
        return True
    with_retry(_create)
    log(f"[NOTION] 미제출 행 생성: {target} {piece}")


# ── Beeminder ─────────────────────────────────────────────────────
def beeminder_has_datapoint(goal: str, daystamp: str) -> bool:
    """해당 날짜(YYYYMMDD) datapoint 존재 여부 - 중복 전송 방지"""
    url = f"{BEEMINDER_API}/users/{BEEMINDER_USER}/goals/{goal}/datapoints.json"
    def _get():
        resp = requests.get(url, params={"auth_token": BEEMINDER_TOKEN, "count": 10}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    try:
        points = with_retry(_get)
        return any(p.get("daystamp") == daystamp for p in points)
    except Exception as e:
        log(f"[BEEMINDER] datapoint 조회 실패({goal}): {e} - 미존재로 간주")
        return False


def send_beeminder(goal: str, target: date, deadline: dtime, comment: str, dry_run: bool) -> bool:
    """timestamp를 해당 날짜의 마감 시각으로 지정해 datapoint 전송"""
    daystamp = target.strftime("%Y%m%d")
    if beeminder_has_datapoint(goal, daystamp):
        log(f"[BEEMINDER] {goal} {daystamp} datapoint 이미 존재 - 전송 스킵")
        return True
    if dry_run:
        log(f"[DRY-RUN] Beeminder 전송 생략: {goal} +1 ({comment})")
        return True
    ts = int(datetime.combine(target, deadline, tzinfo=KST).timestamp())
    payload = {
        "timestamp": ts,
        "value": 1.0,
        "auth_token": BEEMINDER_TOKEN,
        "comment": comment,
    }
    url = f"{BEEMINDER_API}/users/{BEEMINDER_USER}/goals/{goal}/datapoints.json"
    def _send():
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    try:
        with_retry(_send)
        log(f"[BEEMINDER OK] {goal} +1 ({comment})")
        return True
    except Exception as e:
        log(f"[BEEMINDER ERROR] {goal} 전송 실패: {e}")
        return False


# ── 조각 목표표 조회 ──────────────────────────────────────────────
def get_piece_goal(target: date, piece: str) -> dict | None:
    """요일×조각의 목표 반환. 미설정(자리표시자)이면 None."""
    weekday = WEEKDAY_KR[target.weekday()]
    rows = query_notion_db(GOALS_DB_ID, {
        "filter": {
            "and": [
                {"property": "요일", "select": {"equals": weekday}},
                {"property": "조각", "select": {"equals": piece}},
            ]
        }
    })
    if not rows:
        return None
    props = rows[0].get("properties", {})
    goal_text = get_rich_text(props, "목표 내용").strip()
    criteria  = get_rich_text(props, "검증 기준").strip()
    if not goal_text or any(m in goal_text for m in PLACEHOLDER_MARKERS):
        return None
    return {"goal": goal_text, "criteria": criteria, "weekday": weekday}


# ── 사진 수집 ─────────────────────────────────────────────────────
def collect_photos(page: dict) -> list[bytes]:
    """인증 기록 행의 '사진' 속성에서 이미지 다운로드 (최대 3장)"""
    files = page.get("properties", {}).get("사진", {}).get("files", [])
    photos = []
    for f in files[:3]:
        url = None
        if f.get("type") == "file":
            url = f["file"].get("url")
        elif f.get("type") == "external":
            url = f["external"].get("url")
        if not url:
            continue
        try:
            def _dl(u=url):
                resp = requests.get(u, timeout=30)
                resp.raise_for_status()
                return resp.content
            photos.append(with_retry(_dl))
        except Exception as e:
            log(f"[PHOTO] 다운로드 실패: {e}")
    log(f"[PHOTO] {len(photos)}장 확보")
    return photos


def guess_media_type(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"GIF":
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


# ── Groq Vision 엄격 판정 (무료) ───────────────────────────────────
def judge_photos(photos: list[bytes], goal: dict, target: date, piece: str) -> tuple[str, str]:
    """Returns (status, reason). status: 'PASS' | 'FAIL' | 'ERROR'.
    PASS/FAIL = 판정 완료. ERROR = 시스템 장애로 판정 불가(재시도 대상).
    애매하면 FAIL."""
    if not GROQ_API_KEY:
        return "ERROR", "GROQ_API_KEY 미설정"

    goal_text = hr_compress(goal["goal"], "goal")
    criteria  = hr_compress(goal["criteria"], "criteria") if goal["criteria"] else "(별도 기준 없음 - 목표 내용 자체로 판정)"

    prompt = f"""당신은 습관 인증 사진을 검증하는 엄격한 심판이다.
사용자가 아래 목표를 달성했다는 증거로 이 사진을 제출했다.

[날짜/조각] {target.isoformat()} ({goal['weekday']}) {piece} 조각
[목표] {goal_text}
[검증 기준] {criteria}

판정 규칙 (엄격 모드):
1. 사진에서 목표의 결과물이 명확하게 확인되어야만 PASS.
2. 분량·형태가 기준에 미달하면 FAIL. "흔적만 있는" 수준은 FAIL.
3. 목표와 무관한 사진(책상, 풍경, 화면만 켜진 모니터 등)은 FAIL.
4. 조금이라도 애매하거나 확신이 서지 않으면 무조건 FAIL. 입증 책임은 제출자에게 있다.
5. 손글씨가 흐릿해도 내용과 분량이 식별되면 인정하되, 식별 자체가 불가능하면 FAIL.

응답 형식 (이 형식만 사용):
RESULT: PASS 또는 FAIL
REASON: 판정 근거 한두 문장 (무엇이 보였고 무엇이 부족했는지)"""

    # OpenAI 호환 형식: image_url + base64 data URL (Groq에서 실검증 완료)
    content = []
    for p in photos:
        b64 = base64.standard_b64encode(p).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{guess_media_type(p)};base64,{b64}"},
        })
    content.append({"type": "text", "text": prompt})

    def _vision():
        resp = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "User-Agent": "proof-split/1.0",
            },
            json={
                "model": GROQ_MODEL,
                "max_tokens": 300,
                "temperature": 0,
                "messages": [{"role": "user", "content": content}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    try:
        text = with_retry(_vision)
        log(f"[VISION] 원본 응답: {text[:200]}")
    except Exception as e:
        log(f"[VISION ERROR] {type(e).__name__}: {e}")
        return "ERROR", f"Groq API 호출 실패: {str(e)[:100]}"

    passed = None
    reason = "응답에서 판정 근거를 찾지 못함"
    for line in text.splitlines():
        line = line.strip()
        if line.upper().startswith("RESULT:"):
            passed = "PASS" in line.upper()
        elif line.upper().startswith("REASON:"):
            reason = line[len("REASON:"):].strip() or reason
    if passed is None:
        # 형식 미준수 응답 - 판정 불능이 아니라 엄격 원칙에 따라 FAIL
        return "FAIL", f"AI 응답 형식 오류(엄격 원칙에 따라 FAIL): {text[:100]}"
    return ("PASS" if passed else "FAIL"), reason


# ── 조각 검증 ─────────────────────────────────────────────────────
def verify_piece(target: date, piece: str, dry_run: bool, is_final: bool) -> dict:
    """
    한 조각을 검증한다. is_final=True면 시스템 장애 시 자동 PASS(재시도 소진).
    Returns {"result": "PASS"|"FAIL"|"SKIP_DUP"|"DEFER", "reason": str}
    """
    deadline = AM_DEADLINE if piece == "오전" else PM_DEADLINE
    window_start = dtime(0, 0) if piece == "오전" else AM_DEADLINE

    log(f"── [{piece} 조각] 검증 시작 (창: {window_start}~{deadline}) ──")

    rows = query_notion_db(PROOF_DB_ID, {
        "filter": {
            "and": [
                {"property": "날짜", "date": {"equals": target.isoformat()}},
                {"property": "조각", "select": {"equals": piece}},
            ]
        }
    })

    # 1. 행 없음 → 미제출 FAIL
    if not rows:
        log(f"[{piece}] 인증 행 없음 - 미제출 FAIL")
        create_missing_row(target, piece, dry_run)
        return {"result": "FAIL", "reason": "미제출 (인증 행 없음)"}

    page = rows[0]
    page_id = page["id"]
    props = page.get("properties", {})

    # 2. 중복 실행 방지: 이미 판정됨
    existing = get_select_name(props, "검증결과")
    if existing:
        log(f"[{piece}] 이미 판정됨({existing}) - 스킵")
        return {"result": "SKIP_DUP", "reason": f"이미 판정됨: {existing}"}

    last_edited = parse_notion_time_kst(page.get("last_edited_time", ""))
    upload_str = last_edited.strftime("%Y-%m-%d %H:%M KST")

    # 3. 업로드 시간 검증 (거짓증명 차단 1)
    ws = datetime.combine(target, window_start, tzinfo=KST)
    de = datetime.combine(target, deadline, tzinfo=KST)
    if not (ws <= last_edited <= de):
        reason = f"업로드 시간 위반: 마지막 편집 {upload_str} (허용 창 {window_start}~{deadline})"
        log(f"[{piece}] FAIL - {reason}")
        update_proof_row(page_id, "FAIL", reason, upload_str, dry_run)
        return {"result": "FAIL", "reason": reason}

    # 4. 사진 확인
    photos = collect_photos(page)
    if not photos:
        reason = "사진 없음 ('사진' 속성에 업로드 필요)"
        log(f"[{piece}] FAIL - {reason}")
        update_proof_row(page_id, "FAIL", reason, upload_str, dry_run)
        return {"result": "FAIL", "reason": reason}

    # 5. 목표 조회
    goal = get_piece_goal(target, piece)
    if goal is None:
        reason = "조각 목표표 미설정 - Notion에서 목표를 입력하세요"
        log(f"[{piece}] FAIL - {reason}")
        update_proof_row(page_id, "FAIL", reason, upload_str, dry_run)
        return {"result": "FAIL", "reason": reason}

    # 6. AI 엄격 판정 (거짓증명 차단 2)
    status, reason = judge_photos(photos, goal, target, piece)

    # 시스템 장애: 사용자 잘못이 아님. 다음 cron이 재시도하도록 Notion에 기록하지 않음.
    # 마지막 재시도에서도 장애면 자동 PASS 처리(벌금 없음).
    if status == "ERROR":
        if is_final:
            reason = f"시스템 장애로 판정 불가(재시도 소진) - 자동 인정: {reason}"
            log(f"[{piece}] PASS(자동 인정) - {reason}")
            update_proof_row(page_id, "PASS", reason, upload_str, dry_run)
            return {"result": "PASS", "reason": reason}
        log(f"[{piece}] 판정 보류 - {reason} (다음 cron이 재시도)")
        return {"result": "DEFER", "reason": reason}

    log(f"[{piece}] {status} - {reason}")
    update_proof_row(page_id, status, reason, upload_str, dry_run)
    return {"result": status, "reason": reason}


# ── notion-daily 할일 체크 (기존 로직 이식) ─────────────────────────
def check_todos(target: date) -> dict:
    log("── [할일 체크] notion-daily ──")
    company = personal = waiting = 0
    try:
        pages = query_notion_db(TODO_DB_ID, {
            "filter": {"property": "완료", "checkbox": {"equals": False}}
        })
        for page in pages:
            props = page.get("properties", {})
            if get_select_name(props, "할일? 일정?") == "민채 일정":
                continue
            # 기한(end)이 아직 안 된 항목 제외
            date_val = (props.get("진행할 날짜", {}).get("date") or {})
            end_str = date_val.get("end")
            if end_str:
                try:
                    if date.fromisoformat(end_str[:10]) > target:
                        continue
                except ValueError:
                    pass
            category = get_select_name(props, "할일 구분")
            if category == "회사 할 일":
                company += 1
            elif category == "기타 할 일":
                personal += 1
    except Exception as e:
        log(f"[할일 체크 ERROR] {e} - 카운트 0으로 진행")

    try:
        waiting = len(query_notion_db(TODO_DB_ID, {
            "filter": {"and": [
                {"property": "완료", "checkbox": {"equals": False}},
                {"property": "상태", "select": {"equals": "대기중"}},
            ]}
        }))
    except Exception:
        waiting = 0

    passed = (company < COMPANY_THRESHOLD) and (personal < PERSONAL_THRESHOLD) and (waiting == 0)
    log(f"[할일 체크] 회사={company}, 기타={personal}, 대기중={waiting} → {'PASS' if passed else 'FAIL'}")
    return {"passed": passed, "company": company, "personal": personal, "waiting": waiting}


# ── Slack ─────────────────────────────────────────────────────────
def send_slack(message: str, dry_run: bool):
    if dry_run:
        log(f"[DRY-RUN] Slack 생략:\n{message}")
        return
    if not SLACK_BOT_TOKEN:
        log("[Slack] 토큰 미설정 - 스킵")
        return
    def _slack():
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": SLACK_CHANNEL_ID, "text": message},
            timeout=10,
        )
        data = resp.json()
        if data.get("ok"):
            return True
        raise RuntimeError(f"slack error: {data.get('error')}")
    try:
        with_retry(_slack)
        log("[Slack] 전송 성공")
    except Exception as e:
        log(f"[Slack] 전송 최종 실패: {e}\n메시지:\n{message}")


# ── 메인 ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="정산할 날짜 (YYYY-MM-DD). 기본: 방금 끝난 하루")
    parser.add_argument("--dry-run", action="store_true", help="쓰기 작업 없이 검증만")
    args = parser.parse_args()

    now_kst = datetime.now(KST)

    # 실행 시간대로 모드 결정:
    #   낮 실행(06:00~17:59 KST, cron 13:05/13:35/14:05) → 오늘의 오전 조각만 즉시 검증
    #   그 외(자정 cron 00:05/00:35/01:05) → 어제의 오후 조각 + 놓친 오전 보완 + 할일 체크
    day_mode = 6 <= now_kst.hour <= 17
    pieces = ("오전",) if day_mode else ("오전", "오후")
    is_final = now_kst.hour >= (FINAL_ATTEMPT_HOUR_DAY if day_mode
                                else FINAL_ATTEMPT_HOUR_NIGHT)

    if args.date:
        target = date.fromisoformat(args.date)
    elif day_mode:
        target = now_kst.date()
    else:
        # 00:05~05:59 실행 → 어제를 정산
        target = (now_kst - timedelta(hours=6)).date()
        if target == now_kst.date():
            target = target - timedelta(days=1)

    log("=" * 60)
    log(f"START proof-split[{'낮:오전조각' if day_mode else '자정:하루정산'}]: "
        f"대상={target} ({WEEKDAY_KR[target.weekday()]}), "
        f"실행={now_kst.strftime('%Y-%m-%d %H:%M:%S')} KST, dry_run={args.dry_run}")

    missing = [k for k, v in {
        "NOTION_TOKEN": NOTION_TOKEN,
        "BEEMINDER_TOKEN": BEEMINDER_TOKEN,
        "GROQ_API_KEY": GROQ_API_KEY,
    }.items() if not v]
    if missing:
        log(f"[CRITICAL] 필수 환경변수 누락: {', '.join(missing)}")
        return 1

    # 1) 조각 검증 (낮 모드: 오전만 / 자정 모드: 오전 보완 + 오후)
    results = {}
    for piece in pieces:
        try:
            results[piece] = verify_piece(target, piece, args.dry_run, is_final)
        except Exception as e:
            log(f"[{piece} ERROR] {type(e).__name__}: {e}")
            results[piece] = {"result": "ERROR", "reason": str(e)[:200]}

    # 검증 대상 조각이 전부 이미 판정됨 → 중복 실행. 이후 단계 생략하고 종료
    if all(r["result"] == "SKIP_DUP" for r in results.values()):
        log("[중복 실행] 대상 조각 모두 이미 판정됨 - 조기 종료")
        log("=" * 60)
        return 0

    # 2) Beeminder 전송 (PASS 조각만)
    goal_map = {"오전": (GOAL_AM, AM_DEADLINE), "오후": (GOAL_PM, PM_DEADLINE)}
    for piece, res in results.items():
        goal, deadline = goal_map[piece]
        if res["result"] == "PASS":
            send_beeminder(goal, target, deadline,
                           f"{piece} 조각 인증 통과: {res['reason'][:80]}", args.dry_run)
        else:
            log(f"[BEEMINDER] {goal} 미전송 ({res['result']}) → derail 압박")

    # 3) notion-daily 할일 체크 (자정 정산에서만)
    todo = None
    if not day_mode:
        todo = check_todos(target)
        if todo["passed"]:
            send_beeminder(GOAL_NOTION, target, PM_DEADLINE,
                           f"할일 완료 - 회사:{todo['company']} 기타:{todo['personal']}", args.dry_run)

    # 4) Slack 요약
    def badge(r):
        return {"PASS": "✅", "FAIL": "❌", "SKIP_DUP": "↩️",
                "DEFER": "⏳", "ERROR": "⚠️"}.get(r, "❓")

    title = "오전 조각 검증" if day_mode else "하루 정산"
    lines = [f"📸 proof-split {title} — {target} ({WEEKDAY_KR[target.weekday()]})"]
    for piece in pieces:
        r = results[piece]
        label = "판정 보류(재시도 예정)" if r["result"] == "DEFER" else r["result"]
        lines.append(f"{badge(r['result'])} {piece}: {label} — {r['reason'][:200]}")
    if todo is not None:
        lines.append(
            f"{'✅' if todo['passed'] else '❌'} 할일: 회사 {todo['company']} / "
            f"기타 {todo['personal']} / 대기중 {todo['waiting']}"
        )
    fails = [p for p, r in results.items() if r["result"] in ("FAIL", "ERROR")]
    todo_failed = todo is not None and not todo["passed"]
    if fails or todo_failed:
        lines.append("💸 벌금 압박: " + ", ".join(
            ([f"proof-{'am' if p == '오전' else 'pm'}" for p in fails]) +
            ([GOAL_NOTION] if todo_failed else [])
        ))
    else:
        lines.append("🎉 미션 완료! Beeminder 안전")
    send_slack("\n".join(lines), args.dry_run)

    log("END proof-split")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
GitHub Actions / Task Scheduler에서 self-growth-weekly 루틴 실행.

SKILL.md Agent A/B/C 직렬 실행:
  Agent A: 로컬 로그 파일 읽기 + GitHub Actions 실행 기록 조회 (가능한 경우)
  Agent B: Claude API로 패턴 분석 + 건강 점수 산출
  Agent C: Slack 알림 전송 + 분석 결과를 CLAUDE.md에 append

GitHub Actions Secrets / 환경변수 필요:
  ANTHROPIC_API_KEY
선택:
  SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
  NOTION_TOKEN (분석 결과 Notion 저장 시 사용)
  GH_TOKEN (GitHub Actions 실행 기록 조회 시 사용)
"""

import os
import sys
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests

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
        "ANTHROPIC_API_KEY": "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",
        "SLACK_BOT_TOKEN": "xoxb-11192160617749-11210448579094-3SLkUfVn1AEzCXWxDGAKrkEj",
        "SLACK_CHANNEL_ID": "U0B66D6H12S",
        "NOTION_TOKEN": "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",
    }
    for k, v in fallbacks.items():
        if not os.environ.get(k):
            os.environ[k] = v

load_env()

# ── 시간 설정 ─────────────────────────────────────────────────────
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
today_str = now_kst.strftime("%Y-%m-%d")

# ── 로그 설정 ─────────────────────────────────────────────────────
def setup_logging():
    """로그 핸들러 설정: 콘솔 + ~/.claude/ + desktop logs/"""
    _logger = logging.getLogger("selfgrowth_routine")
    _logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # 콘솔
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    _logger.addHandler(ch)

    # ~/.claude/selfgrowth.log
    try:
        p1 = Path.home() / ".claude" / "selfgrowth.log"
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
        dated = log_dir / f"selfgrowth_{now_kst.strftime('%Y%m%d')}.log"
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

log(f"[시작] Self-Growth Weekly 루틴 (KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')})")

# ── 환경변수 ──────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN   = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID  = os.environ.get("SLACK_CHANNEL_ID", "U0B66D6H12S")
NOTION_TOKEN      = os.environ.get("NOTION_TOKEN", "")
GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")

if not ANTHROPIC_API_KEY:
    log("[CRITICAL] ANTHROPIC_API_KEY 누락")
    sys.exit(1)

from anthropic import Anthropic
client = Anthropic(api_key=ANTHROPIC_API_KEY)


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


# ── 로그 파일 경로들 ─────────────────────────────────────────────
LOG_SEARCH_PATHS = [
    Path.home() / ".claude" / "notion_beeminder.log",
    Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/logs"),
    Path(os.environ.get("TEMP", "C:/Users/wnsdu/AppData/Local/Temp")) / "notion_beeminder.log",
]


# ─────────────────────────────────────────────────────────────────
# Agent A: 실행 기록 수집 (로컬 로그 파일 우선, GitHub API 보조)
# ─────────────────────────────────────────────────────────────────
log("\n[Agent A] 최근 7일 실행 기록 수집...")

run_summary = []
total_runs = 0
success_count = 0
fail_count = 0
log_contents = []

# A-1: 로컬 로그 파일에서 읽기
try:
    cutoff_dt = now_kst - timedelta(days=7)

    # 1. 주 로그 파일 (~/.claude/notion_beeminder.log)
    main_log = Path.home() / ".claude" / "notion_beeminder.log"
    if main_log.exists():
        try:
            text = main_log.read_text(encoding="utf-8", errors="replace")
            log_contents.append(f"=== {main_log} ===\n{text[-8000:]}")  # 최근 8KB
        except Exception as e:
            log(f"[Agent A] 메인 로그 읽기 실패: {e}")

    # 2. Desktop logs/ 최근 7일 날짜별 파일
    log_dir = Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/logs")
    if log_dir.exists():
        for i in range(7):
            d = now_kst - timedelta(days=i)
            for pattern in [f"notion_beeminder_{d.strftime('%Y%m%d')}.log",
                            f"notion_routine_{d.strftime('%Y%m%d')}.log"]:
                lf = log_dir / pattern
                if lf.exists():
                    try:
                        text = lf.read_text(encoding="utf-8", errors="replace")
                        log_contents.append(f"=== {lf.name} ===\n{text[-4000:]}")
                    except Exception as e:
                        log(f"[Agent A] {lf.name} 읽기 실패: {e}")

    if log_contents:
        log(f"[Agent A] 로컬 로그 {len(log_contents)}개 파일 로드 완료")

        # 로그에서 SUCCESS/FAIL 패턴 파싱
        import re
        for content in log_contents:
            # "[YYYY-MM-DD HH:MM:SS] [완료]" 라인 찾기
            for line in content.splitlines():
                date_match = re.search(r"\[(\d{4}-\d{2}-\d{2})", line)
                if not date_match:
                    continue
                line_date_str = date_match.group(1)
                try:
                    line_dt = datetime.strptime(line_date_str, "%Y-%m-%d")
                    # cutoff 이전이면 스킵
                    if line_dt < cutoff_dt.replace(tzinfo=None):
                        continue
                except ValueError:
                    continue

                if "[완료]" in line or "END: 자동화 완료" in line:
                    total_runs += 1
                    success_count += 1
                    run_summary.append({"date": line_date_str, "result": "SUCCESS"})
                elif "[CRITICAL]" in line or "[ERROR]" in line:
                    # 심각한 에러만 FAIL로 카운트
                    if any(x in line for x in ["sys.exit", "종료", "CRITICAL"]):
                        fail_count += 1
                        run_summary.append({"date": line_date_str, "result": "FAIL", "detail": line.strip()[:100]})

        log(f"[Agent A] 로그 파싱: 총{total_runs}회, 성공{success_count}, 실패{fail_count}")
    else:
        log("[Agent A] 로컬 로그 파일 없음")

except Exception as e:
    log(f"[Agent A] 로컬 로그 분석 오류: {e}")

# A-2: GitHub Actions API 보조 (GH_TOKEN 있을 때만)
if GH_TOKEN and GITHUB_REPOSITORY:
    try:
        gh_headers = {
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        def _gh_api():
            url = (
                f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/workflows/"
                f"notion-beeminder-daily.yml/runs?per_page=10"
            )
            resp = requests.get(url, headers=gh_headers, timeout=15)
            resp.raise_for_status()
            return resp.json()

        gh_data = with_retry(_gh_api)
        runs = gh_data.get("workflow_runs", [])

        cutoff = now_kst - timedelta(days=7)
        gh_runs = 0
        for run in runs:
            created_at = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            if created_at < cutoff:
                continue
            status = run.get("conclusion", "unknown")
            run_date = created_at.astimezone(KST).strftime("%Y-%m-%d")
            gh_runs += 1
            if status == "success":
                run_summary.append({"date": run_date, "result": "GH_SUCCESS"})
            elif status in ("failure", "timed_out"):
                run_summary.append({"date": run_date, "result": "GH_FAIL"})
            else:
                run_summary.append({"date": run_date, "result": f"GH_{status.upper()}"})

        log(f"[Agent A] GitHub Actions 기록 {gh_runs}개 추가")

    except Exception as e:
        log(f"[Agent A] GitHub API 조회 실패 (선택사항): {e}")

# 실행 기록이 전혀 없으면 더미
if not run_summary:
    run_summary = [{"date": today_str, "result": "UNKNOWN", "note": "로그 없음 - 첫 실행 주"}]
    log("[Agent A] 실행 기록 없음 - 더미 데이터 사용")

agent_a_result = {
    "period": f"{(now_kst - timedelta(days=7)).strftime('%Y-%m-%d')} ~ {today_str}",
    "total_runs": total_runs,
    "success_count": success_count,
    "fail_count": fail_count,
    "daily_results": run_summary[:20],  # 최대 20개
    "log_files_found": len(log_contents),
    "log_sample": "\n".join(log_contents)[:3000] if log_contents else "(로그 없음)",
}


# ─────────────────────────────────────────────────────────────────
# Agent B: Claude API로 패턴 분석
# ─────────────────────────────────────────────────────────────────
log("\n[Agent B] Claude API 패턴 분석...")

analysis_prompt = f"""
오늘 날짜: {today_str}
아래는 최근 7일간 Notion-Beeminder 루틴의 실행 기록 및 로그 샘플입니다.

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

agent_b_result = {}

try:
    def _claude():
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            messages=[{"role": "user", "content": analysis_prompt}]
        )
        return response.content[0].text.strip()

    raw = with_retry(_claude, max_retries=3, base_delay=3)
    log(f"[Agent B] 응답: {raw[:200]}...")

    # 코드블록 제거
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            if part.strip().startswith("json"):
                raw = part.strip()[4:].strip()
                break
            elif part.strip().startswith("{"):
                raw = part.strip()
                break

    raw = raw.strip()
    try:
        agent_b_result = json.loads(raw)
    except json.JSONDecodeError:
        import ast
        agent_b_result = ast.literal_eval(raw)

except (json.JSONDecodeError, ValueError) as e:
    log(f"[Agent B] JSON 파싱 실패: {e}")
    agent_b_result = {
        "analysis_date": today_str,
        "health_score": 50,
        "weaknesses": ["분석 데이터 부족"],
        "strengths": ["로컬 실행 환경 안정"],
        "repeated_errors": [],
        "recommended_rules": ["실행 기록 쌓인 후 재분석 권장"],
        "summary": "초기 주 - 데이터 누적 중",
    }
except Exception as e:
    log(f"[Agent B] Claude API 오류: {e}")
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
log(f"[Agent B] 건강점수={health_score}, 요약={summary}")


# ─────────────────────────────────────────────────────────────────
# Agent C-1: CLAUDE.md에 분석 결과 append
# ─────────────────────────────────────────────────────────────────
log("\n[Agent C-1] CLAUDE.md에 분석 결과 append...")

CLAUDE_MD_PATHS = [
    Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/CLAUDE.md.txt"),
    Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/CLAUDE.md"),
    Path.home() / ".claude" / "CLAUDE.md",
]

append_entry = f"""
## Self-Growth 분석 ({today_str})

- 건강점수: {health_score}/100
- 요약: {summary}
- 약점: {', '.join(agent_b_result.get('weaknesses', [])[:3])}
- 강점: {', '.join(agent_b_result.get('strengths', [])[:3])}
- 반복에러: {', '.join(agent_b_result.get('repeated_errors', [])[:3]) or '없음'}
- 추천: {', '.join(agent_b_result.get('recommended_rules', [])[:3])}
- 분석기간: {agent_a_result.get('period', '')} (총{total_runs}회, 성공{success_count}, 실패{fail_count})
"""

claude_md_updated = False
for claude_md_path in CLAUDE_MD_PATHS:
    try:
        if claude_md_path.exists():
            # 기존 파일에 append
            with open(claude_md_path, "a", encoding="utf-8") as f:
                f.write(append_entry)
            log(f"[Agent C-1] CLAUDE.md append 성공: {claude_md_path}")
            claude_md_updated = True
            break
    except Exception as e:
        log(f"[Agent C-1] {claude_md_path} append 실패: {e}")

if not claude_md_updated:
    # 파일이 없으면 새로 생성 (첫 번째 경로)
    try:
        new_path = CLAUDE_MD_PATHS[0]
        new_path.parent.mkdir(parents=True, exist_ok=True)
        with open(new_path, "w", encoding="utf-8") as f:
            f.write(f"# CLAUDE.md - Self-Growth 분석 기록\n{append_entry}")
        log(f"[Agent C-1] CLAUDE.md 신규 생성: {new_path}")
    except Exception as e:
        log(f"[Agent C-1] CLAUDE.md 생성 실패: {e}")

# 분석 결과를 로그에도 기록
analysis_log = Path("C:/Users/wnsdu/OneDrive/Desktop/claude code/logs")
try:
    analysis_log.mkdir(parents=True, exist_ok=True)
    analysis_file = analysis_log / f"selfgrowth_analysis_{today_str}.json"
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump({
            "agent_a": agent_a_result,
            "agent_b": agent_b_result,
        }, f, ensure_ascii=False, indent=2)
    log(f"[Agent C-1] 분석 결과 JSON 저장: {analysis_file}")
except Exception as e:
    log(f"[Agent C-1] 분석 결과 저장 실패: {e}")


# ─────────────────────────────────────────────────────────────────
# Agent C-2: Slack 알림 전송
# ─────────────────────────────────────────────────────────────────
log("\n[Agent C-2] Slack 알림 전송...")

weaknesses = agent_b_result.get("weaknesses", [])
recommended = agent_b_result.get("recommended_rules", [])

weakness_text = "\n".join(f"  - {w}" for w in weaknesses[:3]) if weaknesses else "  - 없음"
recommend_text = "\n".join(f"  - {r}" for r in recommended[:3]) if recommended else "  - 없음"

slack_msg = (
    f"🧠 자기 성장 루틴 분석 완료 ({today_str})\n"
    f"건강점수: {health_score}/100\n"
    f"요약: {summary}\n"
    f"약점:\n{weakness_text}\n"
    f"추천:\n{recommend_text}\n"
    f"(로그파일 {len(log_contents)}개 분석, 실행기록 {total_runs}회)"
)

if SLACK_BOT_TOKEN:
    channel = SLACK_CHANNEL_ID or "U0B66D6H12S"

    def _slack():
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": slack_msg},
            timeout=10,
        )
        data = resp.json()
        if data.get("ok"):
            return True
        raise RuntimeError(f"slack error: {data.get('error')}")

    try:
        with_retry(_slack, max_retries=3, base_delay=2)
        log("[Agent C-2] Slack 전송 성공")
    except Exception as e:
        log(f"[Agent C-2] Slack 전송 최종 실패: {e}")
        log(f"[Agent C-2] 메시지 내용:\n{slack_msg}")
else:
    log("[Agent C-2] SLACK_BOT_TOKEN 미설정 - Slack 스킵")
    log(f"[Agent C-2] 메시지 미리보기:\n{slack_msg}")


# ─────────────────────────────────────────────────────────────────
# 최종 결과 출력
# ─────────────────────────────────────────────────────────────────
log(f"\n[완료] 건강점수={health_score}, 요약={summary}")
print(f"RESULT_JSON:{json.dumps(agent_b_result, ensure_ascii=False)}")

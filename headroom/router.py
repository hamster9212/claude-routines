"""ContentRouter — 입력 콘텐츠 타입 자동 판별.

Headroom 파이프라인의 라우터를 모방한다. 입력을 보고 가장 알맞은
전문 압축기로 보낸다: json / code / log / prose.
"""
from __future__ import annotations

import json
import re

# 로그 라인 휴리스틱: 타임스탬프 / 레벨 토큰 / 대괄호 prefix
_LOG_LINE = re.compile(
    r"(^\s*\[?\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})"      # 2026-06-28 07:00
    r"|(\b(?:DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|TRACE)\b)"  # 레벨
    r"|(^\s*\[(?:완료|에러|시작|END|START)\])",          # 한국어/영문 상태 prefix
    re.MULTILINE,
)

# 코드 휴리스틱: 흔한 키워드/구문
_CODE_HINT = re.compile(
    r"(^\s*(?:def |class |import |from |function |const |let |var |public |private |fn |func ))"
    r"|(=>|::|\bself\b|\bconsole\.log\b|;\s*$)",
    re.MULTILINE,
)


def _looks_json(text: str) -> bool:
    s = text.strip()
    if not s or s[0] not in "{[":
        return False
    try:
        json.loads(s)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def detect(text: str) -> str:
    """콘텐츠 타입을 반환: 'json' | 'code' | 'log' | 'prose'."""
    if not text or not text.strip():
        return "prose"

    if _looks_json(text):
        return "json"

    lines = text.splitlines() or [text]
    sample = "\n".join(lines[:200])

    log_hits = len(_LOG_LINE.findall(sample))
    # 라인 수 대비 로그 패턴 비율이 높으면 로그로 판정
    if log_hits >= max(3, len(lines) * 0.25):
        return "log"

    code_hits = len(_CODE_HINT.findall(sample))
    if code_hits >= max(3, len(lines) * 0.3):
        return "code"

    return "prose"

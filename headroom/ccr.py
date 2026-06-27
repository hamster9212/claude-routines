"""CCR — Contextual Compression Retrieval (가역 압축 캐시).

Headroom의 핵심 차별점: 압축은 비가역이 아니다. 원본을 로컬에 캐시하고,
압축 결과에 짧은 참조 토큰 `⟦HR:abcd1234⟧` 을 남긴다. LLM(또는 사람)이
`headroom_retrieve(token)` 으로 원본을 TTL 내에 100% 복원할 수 있다.

로컬 우선(local-first): 데이터는 머신을 떠나지 않는다. 기본 캐시 경로는
`~/.headroom/ccr/` 이며, 환경변수 `HEADROOM_CCR_DIR` 로 변경 가능.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

# 참조 토큰 형식: 사람이 봐도 압축 placeholder임이 명확하고, 모델이
# 우발적으로 생성하기 어려운 유니코드 괄호를 사용한다.
REF_PREFIX = "⟦HR:"
REF_SUFFIX = "⟧"

DEFAULT_TTL_SECONDS = 24 * 3600  # 24시간


def _cache_dir() -> Path:
    raw = os.environ.get("HEADROOM_CCR_DIR")
    base = Path(raw) if raw else (Path.home() / ".headroom" / "ccr")
    base.mkdir(parents=True, exist_ok=True)
    return base


def make_ref(original: str) -> str:
    """원본 문자열을 캐시에 저장하고 참조 토큰을 반환한다.

    동일 내용은 동일 토큰으로 매핑된다(자동 중복 제거).
    """
    digest = hashlib.sha256(original.encode("utf-8")).hexdigest()[:12]
    token = f"{REF_PREFIX}{digest}{REF_SUFFIX}"
    path = _cache_dir() / f"{digest}.json"
    if not path.exists():
        payload = {
            "token": token,
            "created": time.time(),
            "len": len(original),
            "content": original,
        }
        # 원자적 쓰기: 임시파일 후 교체 (무인 동시 실행 안전)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, path)
    return token


def retrieve(token: str) -> str | None:
    """참조 토큰으로 원본을 복원한다. 없거나 만료 시 None."""
    digest = token.strip()
    if digest.startswith(REF_PREFIX) and digest.endswith(REF_SUFFIX):
        digest = digest[len(REF_PREFIX):-len(REF_SUFFIX)]
    path = _cache_dir() / f"{digest}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data.get("content")


def expand(text: str) -> str:
    """텍스트 안의 모든 CCR 참조 토큰을 원본으로 치환한다(완전 복원)."""
    if REF_PREFIX not in text:
        return text
    out = []
    i = 0
    while i < len(text):
        start = text.find(REF_PREFIX, i)
        if start == -1:
            out.append(text[i:])
            break
        out.append(text[i:start])
        end = text.find(REF_SUFFIX, start)
        if end == -1:
            out.append(text[start:])
            break
        token = text[start:end + len(REF_SUFFIX)]
        original = retrieve(token)
        out.append(original if original is not None else token)
        i = end + len(REF_SUFFIX)
    return "".join(out)


def gc(ttl_seconds: int = DEFAULT_TTL_SECONDS) -> int:
    """TTL이 지난 캐시 항목을 삭제한다. 삭제 개수 반환."""
    removed = 0
    now = time.time()
    for path in _cache_dir().glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if now - data.get("created", 0) > ttl_seconds:
                path.unlink()
                removed += 1
        except (json.JSONDecodeError, OSError):
            continue
    return removed

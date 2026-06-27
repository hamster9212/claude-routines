"""CacheAligner — prefix 안정화로 KV 캐시 적중률 향상.

Anthropic/OpenAI의 prompt 캐시는 prefix가 바이트 단위로 동일할 때만 적중한다.
타임스탬프·UUID·실행ID 같은 휘발성 토큰이 prefix에 섞이면 캐시가 매번 깨진다.
CacheAligner는 그런 휘발성 패턴을 안정적인 placeholder로 정규화하여, 동일한
시스템 프롬프트/문맥이 반복될 때 캐시가 실제로 적중하도록 만든다.

주의: 정규화는 압축 대상 본문이 아니라 "캐시 prefix 안정성"이 목적이다.
출력 의미를 바꾸지 않는 범위에서만 적용한다.
"""
from __future__ import annotations

import re

_VOLATILE = [
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?\b"), "⟦TS⟧"),
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"), "⟦UUID⟧"),
    (re.compile(r"\b0x[0-9a-fA-F]{6,}\b"), "⟦ADDR⟧"),
    (re.compile(r"\b(?:run|job|trace|session)[-_]?id[=:]\s*\S+", re.IGNORECASE), "⟦RUNID⟧"),
]


def align(text: str) -> str:
    """휘발성 prefix 토큰을 안정 placeholder로 정규화한다."""
    for pattern, repl in _VOLATILE:
        text = pattern.sub(repl, text)
    return text

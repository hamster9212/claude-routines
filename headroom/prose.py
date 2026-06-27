"""ProseCompressor — 로그/산문 압축기.

Headroom의 Kompress-base(HF 모델) 대신, 무인 환경에서 동작하는 결정론적
휴리스틱 압축을 사용한다. 로그·반복 텍스트에서 특히 강력하다.

기법:
  1. 연속 중복 라인 접기:  "...(×N)" 표기
  2. 빈도 높은 동일 라인 dedup (전체 범위, 첫 등장만 유지 + 횟수)
  3. 과도한 공백/빈 줄 축소
  4. head + tail 보존, 중간부는 CCR 참조로 치환 (가역) — 매우 긴 로그용
"""
from __future__ import annotations

import re
from collections import Counter

from . import ccr

# 복원용 마커 파서: "{line}  ⟦×N⟧" / "{line}  ⟦반복×N⟧"
_COUNT_MARK = re.compile(r"^(.*?)\s+⟦(?:반복)?×(\d+)⟧$")
# CCR 참조 토큰: ⟦HR:<12 hex>⟧
_HR_REF = re.compile(r"⟦HR:[0-9a-fA-F]+⟧")

# 이 줄 수를 넘는 산문은 head/tail만 남기고 중간을 CCR로 접는다.
HEAD_TAIL_THRESHOLD = 400
HEAD_LINES = 120
TAIL_LINES = 80

_WS = re.compile(r"[ \t]+")
_BLANKS = re.compile(r"\n{3,}")


def _collapse_consecutive(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        j = i
        while j + 1 < n and lines[j + 1] == lines[i]:
            j += 1
        count = j - i + 1
        if count >= 3:
            out.append(f"{lines[i]}  ⟦×{count}⟧")
        else:
            out.extend([lines[i]] * count)
        i = j + 1
    return out


def _dedup_frequent(lines: list[str]) -> list[str]:
    """전체에서 4회 이상 반복되는 동일 라인은 첫 등장만 유지하고 횟수 주석."""
    freq = Counter(l for l in lines if l.strip())
    repeated = {l for l, c in freq.items() if c >= 4}
    seen: set[str] = set()
    out: list[str] = []
    for l in lines:
        if l in repeated:
            if l in seen:
                continue
            seen.add(l)
            out.append(f"{l}  ⟦반복×{freq[l]}⟧")
        else:
            out.append(l)
    return out


def compress(text: str, reversible: bool = True) -> str:
    if not text:
        return text

    # 1. 공백 정규화
    text = _WS.sub(" ", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = _BLANKS.sub("\n\n", text)

    lines = text.split("\n")
    lines = _collapse_consecutive(lines)
    lines = _dedup_frequent(lines)

    # 2. 초장문: head + tail 보존, 중간은 CCR 참조
    if reversible and len(lines) > HEAD_TAIL_THRESHOLD:
        middle = "\n".join(lines[HEAD_LINES:-TAIL_LINES])
        ref = ccr.make_ref(middle)
        omitted = len(lines) - HEAD_LINES - TAIL_LINES
        lines = (
            lines[:HEAD_LINES]
            + [f"⟦중략 {omitted}줄 → {ref}⟧"]
            + lines[-TAIL_LINES:]
        )

    return "\n".join(lines)


def restore(text: str) -> str:
    """압축된 로그/산문을 복원한다.

    - 반복 카운트 마커(⟦×N⟧, ⟦반복×N⟧) → N개 라인으로 재전개
    - 중략 CCR 참조(⟦중략 … → ⟦HR:…⟧⟧) 및 일반 CCR 참조 → 원본으로 복원
    반복 dedup은 등장 위치를 근사 복원하므로 라인 수/내용은 보존되나
    비연속 반복의 정확한 순서까지 보장하지는 않는다(의미 보존 우선).
    """
    out: list[str] = []
    for line in text.split("\n"):
        # 중략 블록: 마커를 떼고 CCR 참조만 추출해 원본 중간부로 복원
        if line.startswith("⟦중략"):
            ref_match = _HR_REF.search(line)
            if ref_match:
                out.append(ccr.expand(ref_match.group(0)))
                continue
        m = _COUNT_MARK.match(line)
        if m:
            base, count = m.group(1), int(m.group(2))
            out.extend([base] * count)
        else:
            out.append(line)
    return ccr.expand("\n".join(out))

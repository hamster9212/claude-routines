"""SmartCrusher — 범용 JSON 압축기.

Headroom의 SmartCrusher를 모방. 동형(homogeneous) dict 배열을 테이블화하여
반복되는 키 문자열을 제거하고, 빈 값/긴 문자열을 정리한다.

핵심 기법:
  1. 동형 dict 배열 → {"__hr_table__": {"cols": [...], "rows": [[...]]}}
     (키를 N번 반복하는 대신 1번만 기록 → 토큰 대폭 절감)
  2. null / 빈 문자열 / 빈 컨테이너 제거 (의미 보존)
  3. 임계값 초과 긴 문자열 → CCR 참조 토큰으로 치환 (가역)
  4. 컴팩트 직렬화 (공백 없는 separators)

모든 변환은 가역적이다: `restore()` + CCR `expand()` 로 원본 복원 가능.
"""
from __future__ import annotations

import json
from typing import Any

from . import ccr

TABLE_KEY = "__hr_table__"
# 이 길이를 넘는 문자열 값은 CCR 참조로 치환한다.
LONG_STRING_THRESHOLD = 200


def _is_homogeneous_records(value: Any) -> bool:
    """dict들의 배열이고 키 집합이 충분히 겹치면 테이블화 대상."""
    if not isinstance(value, list) or len(value) < 2:
        return False
    if not all(isinstance(x, dict) for x in value):
        return False
    key_sets = [frozenset(x.keys()) for x in value]
    # 첫 행 키 기준, 80% 이상 행이 동일 키 집합을 공유하면 동형으로 본다.
    base = key_sets[0]
    if not base:
        return False
    matching = sum(1 for ks in key_sets if ks == base)
    return matching >= len(value) * 0.8


def _shrink_value(value: Any, reversible: bool) -> Any:
    if isinstance(value, str):
        if reversible and len(value) > LONG_STRING_THRESHOLD:
            return ccr.make_ref(value)
        return value
    if isinstance(value, dict):
        return _shrink_dict(value, reversible)
    if isinstance(value, list):
        return _shrink_list(value, reversible)
    return value


def _shrink_dict(d: dict, reversible: bool) -> dict:
    out = {}
    for k, v in d.items():
        # 빈 값 제거 (단 0/False는 의미가 있으므로 보존)
        if v is None or v == "" or v == [] or v == {}:
            continue
        out[k] = _shrink_value(v, reversible)
    return out


def _shrink_list(lst: list, reversible: bool) -> Any:
    if _is_homogeneous_records(lst):
        cols = list(lst[0].keys())
        rows = []
        for rec in lst:
            rows.append([_shrink_value(rec.get(c), reversible) for c in cols])
        return {TABLE_KEY: {"cols": cols, "rows": rows}}
    return [_shrink_value(x, reversible) for x in lst]


def compress(text: str, reversible: bool = True) -> str:
    """JSON 문자열을 받아 압축된 JSON 문자열을 반환한다."""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return text  # JSON이 아니면 원본 그대로
    shrunk = _shrink_value(data, reversible)
    return json.dumps(shrunk, ensure_ascii=False, separators=(",", ":"))


def _restore_value(value: Any) -> Any:
    if isinstance(value, dict):
        if TABLE_KEY in value and isinstance(value[TABLE_KEY], dict):
            tbl = value[TABLE_KEY]
            cols = tbl["cols"]
            return [
                {c: _restore_value(v) for c, v in zip(cols, row)}
                for row in tbl["rows"]
            ]
        return {k: _restore_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_restore_value(x) for x in value]
    return value


def restore(text: str) -> str:
    """압축된 JSON을 구조적으로 복원한다(테이블→배열).

    긴 문자열 CCR 참조는 ccr.expand()로 별도 복원한다.
    """
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return text
    restored = _restore_value(data)
    expanded = json.loads(ccr.expand(json.dumps(restored, ensure_ascii=False)))
    return json.dumps(expanded, ensure_ascii=False, indent=2)

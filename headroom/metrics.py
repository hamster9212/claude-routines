"""metrics — 압축 절감 통계 기록/조회 (`headroom perf`).

각 compress() 호출의 before/after 토큰을 JSONL로 누적 기록하고, 누적
절감률·달러 추정치를 집계한다. 로컬 우선: `~/.headroom/metrics.jsonl`.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

# claude-opus 입력 토큰 대략 단가(USD/1K) — 절감 달러 추정용(표시 목적)
PRICE_PER_1K_INPUT = 0.015


def _metrics_path() -> Path:
    raw = os.environ.get("HEADROOM_METRICS_DIR")
    base = Path(raw) if raw else (Path.home() / ".headroom")
    base.mkdir(parents=True, exist_ok=True)
    return base / "metrics.jsonl"


def record(before_tokens: int, after_tokens: int, content_type: str) -> None:
    """단일 압축 이벤트 기록. 절대 예외를 던지지 않는다(베스트 에포트)."""
    try:
        entry = {
            "ts": time.time(),
            "before": before_tokens,
            "after": after_tokens,
            "saved": before_tokens - after_tokens,
            "type": content_type,
        }
        with _metrics_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def summary() -> dict:
    """누적 통계 집계."""
    path = _metrics_path()
    total_before = total_after = events = 0
    by_type: dict[str, int] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            total_before += e.get("before", 0)
            total_after += e.get("after", 0)
            events += 1
            by_type[e.get("type", "?")] = by_type.get(e.get("type", "?"), 0) + e.get("saved", 0)
    saved = total_before - total_after
    ratio = (saved / total_before) if total_before else 0.0
    return {
        "events": events,
        "total_before": total_before,
        "total_after": total_after,
        "saved": saved,
        "ratio": ratio,
        "dollars_saved": round(saved / 1000 * PRICE_PER_1K_INPUT, 4),
        "by_type": by_type,
    }


def format_perf() -> str:
    s = summary()
    if s["events"] == 0:
        return "headroom perf: 기록된 압축 이벤트가 없습니다."
    lines = [
        "📊 headroom perf",
        f"  이벤트:      {s['events']}회",
        f"  압축 전:     {s['total_before']:,} 토큰",
        f"  압축 후:     {s['total_after']:,} 토큰",
        f"  절감:        {s['saved']:,} 토큰 ({s['ratio']*100:.1f}%)",
        f"  추정 절감액: ${s['dollars_saved']}",
    ]
    if s["by_type"]:
        lines.append("  타입별 절감:")
        for t, v in sorted(s["by_type"].items(), key=lambda x: -x[1]):
            lines.append(f"    - {t:8s}: {v:,} 토큰")
    return "\n".join(lines)

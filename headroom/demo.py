"""headroom 실측 데모 — 대표 워크로드에서 토큰 절감을 측정/출력한다.

실행: python -m headroom.demo
"""
from __future__ import annotations

import json

from . import compress_text
from .tokens import estimate_tokens


def _bar(ratio: float, width: int = 30) -> str:
    filled = int(ratio * width)
    return "█" * filled + "░" * (width - filled)


def scenario_log() -> str:
    # 반복이 많은 전형적 무인 루틴 로그
    lines = []
    for i in range(300):
        lines.append(f"[2026-06-{(i%28)+1:02d} 07:00:0{i%10}] [INFO] 환경변수 로드 시도")
        lines.append("[INFO] ANTHROPIC_API_KEY 확인됨")
        lines.append("[INFO] Notion DB 연결 OK")
        if i % 50 == 0:
            lines.append("[ERROR] ANTHROPIC_API_KEY 환경변수 누락 — 재시도")
    return "\n".join(lines)


def scenario_json() -> str:
    records = [
        {
            "date": f"2026-06-{(i%28)+1:02d}",
            "result": "SUCCESS" if i % 7 else "FAIL",
            "duration_ms": 1200 + i,
            "retries": i % 3,
            "note": "",
            "extra": None,
        }
        for i in range(120)
    ]
    return json.dumps({"period": "7d", "daily_results": records}, ensure_ascii=False, indent=2)


def scenario_code() -> str:
    return '''
# 이 함수는 환경변수를 로드한다 (긴 설명 주석)
def load_env():
    # 여러 소스에서 우선순위대로 로드
    sources = ["a.json", "b.json"]   # 후보 경로들
    for path in sources:
        # 존재하면 읽는다
        data = read(path)  # 파일 읽기
    return data  // 최종 반환
'''.strip()


def run() -> None:
    scenarios = {
        "로그 (무인 루틴, 반복 많음)": scenario_log(),
        "JSON (동형 레코드 120개)": scenario_json(),
        "코드 (주석 많은 Python)": scenario_code(),
    }
    print("=" * 64)
    print(" headroom 압축 실측 데모")
    print("=" * 64)
    total_before = total_after = 0
    for name, text in scenarios.items():
        res = compress_text(text, record_metrics=False)
        total_before += res.before_tokens
        total_after += res.after_tokens
        print(f"\n▶ {name}  [{res.content_type}]")
        print(f"   {res.before_tokens:>7,} → {res.after_tokens:>7,} 토큰")
        print(f"   {_bar(res.ratio)}  {res.ratio*100:.1f}% 절감")
        # 가역성 즉시 검증
        restored = res.expand()
        ok = estimate_tokens(restored) >= res.before_tokens * 0.9
        print(f"   가역성 복원: {'OK' if ok else 'WARN'} ({estimate_tokens(restored):,} 토큰 복원)")

    ratio = (total_before - total_after) / total_before if total_before else 0
    print("\n" + "=" * 64)
    print(f" 합계: {total_before:,} → {total_after:,} 토큰  ({ratio*100:.1f}% 절감)")
    print("=" * 64)


if __name__ == "__main__":
    run()

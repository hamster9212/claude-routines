"""headroom CLI — `python -m headroom <command>`.

명령:
  compress <file>     파일을 압축해 stdout으로 출력 (+ 절감률을 stderr로)
  perf                누적 절감 통계 출력
  retrieve <token>    CCR 참조 토큰으로 원본 복원
  gc                  TTL 지난 CCR 캐시 정리
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import compress_text, ccr, metrics


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 0

    cmd, *rest = argv

    if cmd == "compress":
        if not rest:
            print("usage: headroom compress <file>", file=sys.stderr)
            return 2
        text = Path(rest[0]).read_text(encoding="utf-8", errors="replace")
        res = compress_text(text)
        sys.stdout.write(res.text)
        print(
            f"\n[headroom] {res.content_type}: {res.before_tokens}→{res.after_tokens} "
            f"토큰 ({res.ratio*100:.1f}% 절감)",
            file=sys.stderr,
        )
        return 0

    if cmd == "perf":
        print(metrics.format_perf())
        return 0

    if cmd == "retrieve":
        if not rest:
            print("usage: headroom retrieve <token>", file=sys.stderr)
            return 2
        original = ccr.retrieve(rest[0])
        if original is None:
            print("(not found or expired)", file=sys.stderr)
            return 1
        sys.stdout.write(original)
        return 0

    if cmd == "gc":
        removed = ccr.gc()
        print(f"[headroom] CCR 캐시 {removed}개 정리")
        return 0

    print(f"unknown command: {cmd}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""headroom 패키지 단위 테스트 (CLAUDE.md §4 강제 검증).

검증 항목:
  - 콘텐츠 라우팅 정확성
  - 압축률 (대표 워크로드 ≥40%)
  - 가역성 (CCR round-trip 100% 복원)
  - 정확성 불변 (JSON 의미 보존)
  - 통합 안전성 (짧은 입력/엣지케이스에서 무손실 패스)

실행: python -m pytest tests/test_headroom.py -v
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

import pytest

# 워크트리 루트를 import 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 테스트 격리: CCR/metrics 캐시를 임시 디렉터리로
_TMP = tempfile.mkdtemp(prefix="headroom_test_")
os.environ["HEADROOM_CCR_DIR"] = os.path.join(_TMP, "ccr")
os.environ["HEADROOM_METRICS_DIR"] = os.path.join(_TMP, "metrics")

import headroom  # noqa: E402
from headroom import ccr, router, smartcrusher, prose  # noqa: E402
from headroom.tokens import estimate_tokens  # noqa: E402


# ── 토큰 추정기 ──────────────────────────────────────────────
def test_token_estimator_cjk_vs_ascii():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello world") > 0
    # 한글은 글자당 ~1토큰, ASCII는 ~4글자당 1토큰
    assert estimate_tokens("가나다라마") >= estimate_tokens("abcde")


# ── 라우터 ──────────────────────────────────────────────────
def test_router_detects_json():
    assert router.detect('{"a": 1, "b": [1,2,3]}') == "json"
    assert router.detect('[{"x":1},{"x":2}]') == "json"


def test_router_detects_log():
    log = "\n".join(
        f"[2026-06-28 07:00:0{i%10}] [INFO] something happened" for i in range(20)
    )
    assert router.detect(log) == "log"


def test_router_detects_code():
    code = "\n".join([
        "def foo(x):",
        "    import os",
        "    return os.path.join(x, 'y')",
        "class Bar:",
        "    def baz(self):",
        "        return self.x",
    ] * 3)
    assert router.detect(code) == "code"


def test_router_defaults_to_prose():
    assert router.detect("그냥 평범한 한국어 문장입니다. 특별한 패턴이 없습니다.") == "prose"


# ── CCR 가역성 ───────────────────────────────────────────────
def test_ccr_roundtrip():
    original = "민감하고 긴 원본 내용 " * 50
    token = ccr.make_ref(original)
    assert token.startswith("⟦HR:")
    assert ccr.retrieve(token) == original


def test_ccr_dedup_same_content_same_token():
    a = ccr.make_ref("동일 내용입니다 " * 30)
    b = ccr.make_ref("동일 내용입니다 " * 30)
    assert a == b


def test_ccr_expand_inline():
    secret = "이것은 매우 긴 비밀 문자열입니다 " * 20
    token = ccr.make_ref(secret)
    embedded = f"앞부분 {token} 뒷부분"
    assert ccr.expand(embedded) == f"앞부분 {secret} 뒷부분"


def test_ccr_retrieve_missing_returns_none():
    assert ccr.retrieve("⟦HR:deadbeefdead⟧") is None


# ── SmartCrusher (JSON) ──────────────────────────────────────
def test_smartcrusher_tabularizes_homogeneous_records():
    data = {"rows": [{"a": i, "b": "x", "c": None, "d": ""} for i in range(50)]}
    text = json.dumps(data, ensure_ascii=False, indent=2)
    res = headroom.compress_text(text, record_metrics=False)
    assert res.content_type == "json"
    assert res.ratio > 0.4  # 키 반복 제거로 큰 절감
    # 구조 복원 후 의미가 보존되는지 (null/빈값 정리는 허용)
    restored = json.loads(res.expand())
    assert len(restored["rows"]) == 50
    assert restored["rows"][10]["a"] == 10


def test_smartcrusher_long_string_is_reversible():
    big = "긴 설명 문자열 " * 60
    data = {"note": big, "id": 1}
    res = headroom.compress_text(json.dumps(data, ensure_ascii=False), record_metrics=False)
    restored = json.loads(res.expand())
    assert restored["note"] == big


# ── Prose / 로그 ─────────────────────────────────────────────
def test_prose_collapses_repeats():
    text = "\n".join(["동일한 로그 라인"] * 100)
    res = headroom.compress_text(text, record_metrics=False)
    assert res.ratio > 0.5
    assert res.after_tokens < res.before_tokens


def test_prose_repeat_collapse_restores_line_count():
    # 연속 반복 100줄 → 복원 시 라인 수 보존
    text = "\n".join(["동일한 로그 라인"] * 100)
    res = headroom.compress_text(text, record_metrics=False)
    restored = res.expand()
    assert restored.count("동일한 로그 라인") == 100


def test_prose_headtail_reversible():
    lines = [f"라인 {i} 내용입니다 ----" for i in range(1000)]
    text = "\n".join(lines)
    res = headroom.compress_text(text, record_metrics=False)
    # 중략된 중간부가 CCR로 복원되어 모든 라인 포함
    restored = res.expand()
    assert "라인 500" in restored


# ── compress() 메시지 API (Headroom 호환) ────────────────────
def test_compress_messages_api():
    big = json.dumps([{"k": i, "v": "x"} for i in range(60)])
    msgs = headroom.compress(messages=[
        {"role": "user", "content": big},
        {"role": "assistant", "content": "short"},
    ])
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert len(msgs[0]["content"]) <= len(big)


def test_compress_text_kwarg():
    res = headroom.compress(text="단순 텍스트")
    assert isinstance(res, headroom.CompressResult)


def test_compress_requires_input():
    with pytest.raises(ValueError):
        headroom.compress()


# ── 안전장치 ─────────────────────────────────────────────────
def test_small_input_passthrough():
    res = headroom.compress_text("짧음", record_metrics=False)
    assert res.text == "짧음"
    assert res.saved == 0


def test_never_grows():
    # 어떤 입력이든 압축 결과가 원본보다 토큰이 크면 안 된다
    for sample in ["abc", "x" * 5, json.dumps({"a": 1}), "한 줄 짜리 로그"]:
        res = headroom.compress_text(sample, record_metrics=False)
        assert res.after_tokens <= res.before_tokens


def test_invalid_json_falls_back_to_prose_or_passthrough():
    broken = '{"a": 1, "b":'  # 깨진 JSON
    res = headroom.compress_text(broken, record_metrics=False)
    # 예외 없이 처리되어야 한다
    assert isinstance(res.text, str)


def test_metrics_record_and_summary():
    headroom.compress_text("\n".join(["반복 로그"] * 200))  # record_metrics=True 기본
    s = headroom.metrics.summary()
    assert s["events"] >= 1
    assert s["total_before"] >= s["total_after"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

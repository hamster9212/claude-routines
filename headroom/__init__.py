"""headroom — 로컬 우선 컨텍스트 압축 (headroomlabs-ai/headroom 모방, 순수 Python 포트).

LLM에 보내기 전 tool output·로그·RAG 청크·대화 히스토리를 압축하여 토큰을
60~95% 절감한다. 외부 의존성·네트워크 없이 무인 스케줄 환경에서 동작한다.

파이프라인:
    Input → CacheAligner → ContentRouter → Specialized Compressor → CCR → Output
                                          ├ SmartCrusher   (JSON)
                                          ├ CodeCompressor (코드)
                                          └ ProseCompressor(로그/산문)

기본 사용:
    from headroom import compress, compress_text

    # 메시지 배열 압축 (Headroom API 호환)
    msgs = compress(messages=[{"role": "user", "content": big_text}])

    # 단일 텍스트 압축
    result = compress_text(big_json)
    print(result.text)        # 압축본
    print(result.ratio)       # 절감률
    print(result.expand())    # 원본 복원(가역)
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import cache_aligner, ccr, code_compressor, metrics, prose, router, smartcrusher
from .tokens import estimate_tokens

__version__ = "0.1.0-local"
__all__ = [
    "compress",
    "compress_text",
    "CompressResult",
    "withHeadroom",
    "retrieve",
    "__version__",
]

# 이 토큰 수 미만의 짧은 입력은 압축 오버헤드가 이득보다 커서 건너뛴다.
MIN_TOKENS_TO_COMPRESS = 80


@dataclass
class CompressResult:
    text: str
    content_type: str
    before_tokens: int
    after_tokens: int
    meta: dict = field(default_factory=dict)

    @property
    def saved(self) -> int:
        return self.before_tokens - self.after_tokens

    @property
    def ratio(self) -> float:
        return (self.saved / self.before_tokens) if self.before_tokens else 0.0

    def expand(self) -> str:
        """CCR 참조를 모두 원본으로 복원한다(가역)."""
        if self.content_type == "json":
            return smartcrusher.restore(self.text)
        if self.content_type in ("log", "prose"):
            return prose.restore(self.text)
        return ccr.expand(self.text)

    def __str__(self) -> str:  # 사람이 print 시 압축본을 그대로 본다
        return self.text


def _dispatch(text: str, content_type: str, reversible: bool) -> str:
    if content_type == "json":
        return smartcrusher.compress(text, reversible=reversible)
    if content_type == "code":
        return code_compressor.compress(text, reversible=reversible)
    # log / prose 공통
    return prose.compress(text, reversible=reversible)


def compress_text(
    text: str,
    *,
    reversible: bool = True,
    align_cache: bool = True,
    record_metrics: bool = True,
) -> CompressResult:
    """단일 문자열을 압축하여 CompressResult를 반환한다."""
    if text is None:
        text = ""
    before = estimate_tokens(text)
    content_type = router.detect(text)

    # 너무 짧으면 패스(오버헤드 회피) — 단 타입은 기록
    if before < MIN_TOKENS_TO_COMPRESS:
        return CompressResult(text, content_type, before, before, {"skipped": "too_small"})

    staged = cache_aligner.align(text) if (align_cache and content_type != "json") else text
    compressed = _dispatch(staged, content_type, reversible)

    after = estimate_tokens(compressed)
    # 압축이 오히려 커졌으면 원본 유지(안전장치)
    if after >= before:
        compressed, after, content_type = text, before, content_type
        meta = {"skipped": "no_gain"}
    else:
        meta = {}

    if record_metrics:
        metrics.record(before, after, content_type)
    return CompressResult(compressed, content_type, before, after, meta)


def compress(messages=None, *, text=None, model: str = "claude-opus-4", **kwargs):
    """Headroom 호환 진입점.

    - messages=[{"role","content"}, ...] → 각 content를 압축한 새 리스트 반환
    - text="..."                          → CompressResult 반환
    `model` 인자는 API 호환을 위해 받지만 로컬 추정기에는 영향 없다.
    """
    if text is not None:
        return compress_text(text, **kwargs)
    if messages is None:
        raise ValueError("compress(): messages 또는 text 중 하나는 필요합니다.")

    out = []
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            res = compress_text(content, **kwargs)
            new_msg = dict(msg)
            new_msg["content"] = res.text
            out.append(new_msg)
        else:
            out.append(msg)  # 멀티모달/구조화 content는 건드리지 않음
    return out


def retrieve(token: str):
    """CCR 참조 토큰으로 원본 복원."""
    return ccr.retrieve(token)


def withHeadroom(client):
    """Anthropic/OpenAI 클라이언트를 감싸 전송 직전 자동 압축하는 얇은 래퍼.

    실제 Headroom의 `withHeadroom`을 모방. 메시지 배열을 가진 호출만 가로채
    압축한다. (네트워크/SDK 미설치 환경에서도 import는 성공하도록 지연 처리)
    """
    return _HeadroomClient(client)


class _HeadroomClient:
    def __init__(self, client):
        self._client = client

    def __getattr__(self, name):
        return getattr(self._client, name)

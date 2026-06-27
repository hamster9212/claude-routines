"""CodeCompressor — 코드 압축기.

실제 Headroom은 언어별 AST 파서를 쓰지만, 무인 환경 호환을 위해 의존성 없는
정규식 기반 경량 압축을 사용한다. 의미를 보존하면서 주석/빈 줄/잉여 공백을 제거한다.

지원 힌트: Python, JS/TS, Go, Rust, Java, C/C++ 의 흔한 주석 형태.
가역성: 원본 전체를 CCR에 저장하고 끝에 참조를 남긴다(복원 가능).
"""
from __future__ import annotations

import re

from . import ccr

# 한 줄 주석 (# 또는 //) — 문자열 리터럴 안은 건드리지 않도록 보수적으로 처리
_HASH_COMMENT = re.compile(r"(^|\s)#(?![!{]).*$", re.MULTILINE)
_SLASH_COMMENT = re.compile(r"(^|\s)//.*$", re.MULTILINE)
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_BLANKS = re.compile(r"\n\s*\n\s*\n+")
_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)


def _has_string_quote(line: str) -> bool:
    return ('"' in line) or ("'" in line)


def compress(text: str, reversible: bool = True) -> str:
    if not text:
        return text

    original = text
    out = _BLOCK_COMMENT.sub("", text)

    # 따옴표 없는 줄에서만 한 줄 주석 제거 (문자열 내 #, // 오제거 방지)
    cleaned_lines = []
    for line in out.split("\n"):
        if not _has_string_quote(line):
            line = _HASH_COMMENT.sub("", line)
            line = _SLASH_COMMENT.sub("", line)
        cleaned_lines.append(line)
    out = "\n".join(cleaned_lines)

    out = _TRAILING_WS.sub("", out)
    out = _BLANKS.sub("\n\n", out)
    out = out.strip("\n")

    # 의미 보존을 위해 원본은 CCR에 보관 (디버깅/복원용)
    if reversible:
        ref = ccr.make_ref(original)
        out = f"{out}\n⟦원본코드 {ref}⟧"
    return out

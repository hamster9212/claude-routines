# plan.md — Headroom 컨텍스트 압축 시스템 적용

## 목표
[headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)의 핵심(로컬 우선 컨텍스트 압축, 60~95% 토큰 절감)을 이 프로젝트에 **철저히 적용**한다.
실제 Headroom은 Rust+HuggingFace 모델 의존성이 크므로, 무인 스케줄 환경(Task Scheduler/GitHub Actions)에서도 추가 설치·네트워크 없이 동작하도록 **순수 Python 로컬 구현**으로 핵심 아키텍처를 충실히 모방한다.

## 접근 방식
Headroom 아키텍처 파이프라인을 그대로 모방:
```
Input → CacheAligner → ContentRouter → Specialized Compressor → CCR → Output
                                       ├ SmartCrusher (JSON)
                                       ├ CodeCompressor (코드)
                                       └ ProseCompressor (로그/산문)
```

1. `headroom/` 순수 Python 패키지 신설 (외부 의존성 0)
   - `__init__.py` — `compress()`, `compress_text()`, `withHeadroom()`, `__version__`
   - `tokens.py` — 토큰 추정기(ASCII≈/4 + CJK 1자=1토큰)
   - `router.py` — ContentRouter: JSON / code / log / prose 자동 판별
   - `smartcrusher.py` — JSON 압축(동형 dict 배열→테이블화, 빈값 제거, 긴 문자열 CCR 치환)
   - `code_compressor.py` — 주석/공백 제거, 구조 보존
   - `prose.py` — 로그/산문(중복행 dedup, head+tail 보존, 타임스탬프 축약)
   - `ccr.py` — Contextual Compression Retrieval: 원본 로컬 캐시 + 토큰으로 복원(가역)
   - `cache_aligner.py` — prefix 안정화(KV 캐시 적중률↑)
   - `metrics.py` — 절감 통계 기록/조회(`perf`)
   - `cli.py` — `compress` / `perf` / `retrieve`
2. 토큰 과다 소비 루틴에 통합:
   - `run_selfgrowth_routine.py` Agent B Claude 호출 직전 `agent_a_result` 압축
   - `run_notion_routine.py` 동일 패턴 적용
3. 테스트(`tests/test_headroom.py`) — 압축률, 가역성(round-trip), 라우팅, 정확성 불변
4. README(`headroom/README.md`) + 데모 스크립트로 절감 수치 실측

## 예상 파일 변경 목록
- 신규: `headroom/*.py` (9개 모듈), `tests/test_headroom.py`, `headroom/README.md`, `headroom/demo.py`, `plan.md`
- 수정: `run_selfgrowth_routine.py`, `run_notion_routine.py` (압축 통합, 실패 시 원본 fallback)

## 검증 기준 (CLAUDE.md §4 강제 검증)
1. 단위 테스트: `python -m pytest tests/test_headroom.py` 전부 통과
2. 가역성: 모든 압축 결과는 CCR 토큰으로 원본 100% 복원
3. 압축률: 실제 로그/JSON 샘플에서 ≥40% 토큰 절감
4. 통합 안전성: 압축 모듈 import 실패 시 루틴은 원본으로 정상 동작(graceful degradation)
5. 기존 테스트 회귀 없음: `python -m pytest` 전체 통과

## 원칙 준수 (CLAUDE.md)
- §1 플랜 우선: 본 문서 = 플랜
- §2 가시성: 각 단계 로그 출력
- §5 워크트리: 현재 워크트리에서 작업
- §7 금지: .env 미수정, `git add -A` 미사용, 테스트 없는 머지 금지

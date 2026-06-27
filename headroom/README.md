# headroom (로컬 포트)

[headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)의 핵심 아이디어
— **로컬 우선 컨텍스트 압축으로 LLM 토큰 60~95% 절감** — 을 이 저장소에 맞게
**순수 Python(외부 의존성 0)** 으로 이식한 것입니다. 무인 스케줄 환경(Windows Task
Scheduler / GitHub Actions)에서 추가 설치·네트워크 없이 그대로 동작합니다.

> 원본 Headroom은 Rust + HuggingFace 모델 기반이라 무인 환경 설치가 무겁습니다.
> 이 포트는 **동일한 아키텍처와 API**를 결정론적 휴리스틱으로 재현해, 설치 실패로
> 루틴이 멈추는 일이 없도록 했습니다(import 실패 시에도 루틴은 원본으로 정상 동작).

## 아키텍처 (원본 파이프라인 그대로 모방)

```
Input → CacheAligner → ContentRouter → Specialized Compressor → CCR → Output
                                       ├ SmartCrusher   (JSON)
                                       ├ CodeCompressor (코드)
                                       └ ProseCompressor(로그/산문)
```

| 모듈 | 역할 |
|------|------|
| `router.py` | 콘텐츠 타입 자동 판별 (json/code/log/prose) |
| `smartcrusher.py` | 동형 dict 배열 테이블화 + 빈값 제거 + 긴 문자열 CCR 치환 |
| `code_compressor.py` | 주석/공백 제거, 의미 보존 |
| `prose.py` | 반복 로그 dedup, head/tail 보존, 중략부 CCR |
| `ccr.py` | 원본 로컬 캐시 + 참조 토큰으로 100% 가역 복원 |
| `cache_aligner.py` | 휘발성 prefix(타임스탬프/UUID) 정규화 → KV 캐시 적중률↑ |
| `metrics.py` | 압축 절감 통계 누적/집계 (`headroom perf`) |
| `tokens.py` | CJK 인지 토큰 추정기 |

## 사용법

```python
from headroom import compress, compress_text

# 1) 메시지 배열 압축 (원본 Headroom API 호환)
msgs = compress(messages=[{"role": "user", "content": big_text}])

# 2) 단일 텍스트 압축
res = compress_text(big_log)
print(res.text)        # 압축본 (LLM에 전송)
print(res.ratio)       # 절감률 (0.0~1.0)
print(res.expand())    # 원본 복원 (가역)
```

### CLI

```bash
python -m headroom compress <file>    # 파일 압축 → stdout
python -m headroom perf               # 누적 절감 통계
python -m headroom retrieve <token>   # CCR 참조 복원
python -m headroom gc                 # TTL 지난 캐시 정리
python -m headroom.demo               # 실측 데모 (아래 수치 재현)
```

## 실측 절감 (`python -m headroom.demo`)

| 시나리오 | 압축 전 | 압축 후 | 절감 |
|----------|--------:|--------:|-----:|
| 로그 (반복 많은 무인 루틴) | 9,927 | 65 | **99.3%** |
| JSON (동형 레코드 120개) | 4,588 | 1,217 | **73.5%** |
| 코드 (주석 많은 Python) | 94 | 86 | 8.5% |
| **합계** | **14,609** | **1,368** | **90.6%** |

## 가역성(CCR)

- **JSON**: 테이블화/긴 문자열 치환은 `expand()`로 구조까지 완전 복원
- **로그/산문**: 반복 dedup은 카운트를 보존해 라인 수까지 복원, 중략부는 CCR로 복원
- **원본은 로컬(`~/.headroom/ccr/`)에만 저장** — 데이터가 머신을 떠나지 않음

## 이 저장소 통합 지점

- `run_selfgrowth_routine.py` — Agent B Claude 분석 호출 전 `log_sample` 압축
- `notion_beeminder_sync.py` — Vision 프롬프트의 `package_text` 압축

두 곳 모두 **import 실패/압축 오류 시 원본을 그대로 사용**하여 루틴 안정성을 해치지
않습니다(graceful degradation). 모델에 전달되는 압축은 `reversible=False`(의미 보존
dedup)로, CCR 참조로 내용이 가려지지 않습니다.

## 테스트

```bash
python -m pytest tests/test_headroom.py -v   # 21개 테스트
```

라이선스: 원본 Headroom과 동일하게 Apache 2.0 정신을 따릅니다(로컬 학습용 포트).

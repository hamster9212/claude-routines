# Notion-Beeminder 자동화 시스템 설치 가이드

## 📦 설치

### 1단계: 의존성 설치
```bash
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정

필수 환경변수만 설정 (클라우드 서비스 불필요):

```bash
# Notion API (필수)
NOTION_TOKEN=ntn_...
NOTION_RECORD_DB_ID=da3f380eb56d4647ac53d495ba04f6a5

# Beeminder API (필수)
BEEMINDER_TOKEN=your_beeminder_token

# Claude/Anthropic API (필수)
ANTHROPIC_API_KEY=sk-ant-...
```

Windows에서 환경변수 설정:
1. Win+R → `systempropertiesadvanced` 실행
2. "환경 변수" 클릭
3. "사용자 변수" → "새로 만들기"
4. 변수명: `NOTION_TOKEN`, 변수값: `ntn_...` 입력 (반복)

## 🚀 사용 방법

### 명령어
```bash
python notion_beeminder_sync.py '{"company_count": 0, "personal_count": 1, "has_package_keyword": true, "packages": [{"name": "패키지명", "trigger": "발동조건", "step1": "1단계", "step2": "2단계", "step3": "3단계"}]}'
```

**주의**: `image_url` 파라미터는 더 이상 필요 없습니다. 이미지는 Notion에서 자동으로 가져옵니다.

### Scheduled Task 등록
Windows Task Scheduler 또는 CLI에서:
```bash
python C:\Users\wnsdu\OneDrive\Desktop\claude code\notion_beeminder_sync.py '<JSON>'
```

## 📋 기능

- ✅ Notion 할일 완료 상태 → Beeminder 데이터포인트 전송
- ✅ 패키지 풀이 이미지 → Claude Vision API로 자동 검증 (Base64 방식)
- ✅ Notion 파일 자동 다운로드 → Base64 인코딩 → Vision API 분석
- ✅ 클라우드 서비스 불필요 (Google Cloud, Google Drive 설정 없음)
- ✅ 실행 로그 자동 로테이션 (10MB 단위, 최대 5개 유지)
- ✅ API 재시도 로직 (exponential backoff: 1초, 2초, 4초)

## 📊 로그 파일

로그: `~/.claude/notion_beeminder.log*`
- `notion_beeminder.log` (현재)
- `notion_beeminder.log.1` (이전)
- 최대 5개 파일 자동 유지

## ⚠️ 주의사항

- **Vision API 비용**: 매일 이미지 분석 시 약 $0.003/회 (월 ~$100)
- **Notion 임시 URL**: 파일은 1시간 내에 분석되어야 함 (Scheduled Task에서 자동 처리)
- **Notion DB 구조 변경**: 속성명 변경 시 `get_today_image_base64()` 함수 수정 필요
- **인터넷 연결 필수**: Notion API, Beeminder API, Claude API 호출 필요

## 🚀 빠른 테스트

1. 환경변수 설정 확인:
```bash
echo %NOTION_TOKEN%
echo %BEEMINDER_TOKEN%
echo %ANTHROPIC_API_KEY%
```

2. 스크립트 실행 테스트:
```bash
python notion_beeminder_sync.py '{"company_count": 0, "personal_count": 0, "has_package_keyword": false, "packages": []}'
```

3. 로그 확인:
```bash
cat ~/.claude/notion_beeminder.log
```

# Google Drive에서 Base64로 마이그레이션

## 변경사항

**기존 (Google Drive 방식)**
```
Notion 파일 → 임시 URL → Google Drive 업로드 → 공개 URL → Vision API
```

**신규 (Base64 방식)**
```
Notion 파일 → 임시 URL → 다운로드 → Base64 인코딩 → Vision API
```

## 장점

✅ 클라우드 서비스 불필요 (Google Cloud, Google Drive 설정 없음)  
✅ 환경 변수 3개만 필요 (NOTION_TOKEN, BEEMINDER_TOKEN, ANTHROPIC_API_KEY)  
✅ pip install 간단 (requests + anthropic만 필요)  
✅ 보안성 증가 (API 키 파일 관리 불필요)  

## 설정

환경변수만 필수 (더 이상 Google Drive 설정 불필요):

```bash
NOTION_TOKEN=ntn_...
BEEMINDER_TOKEN=...
ANTHROPIC_API_KEY=sk-ant-...
```

완료! 🎉

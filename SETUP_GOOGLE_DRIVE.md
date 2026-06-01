# Google Drive 자동 전환 설정 가이드

## 1단계: Google Cloud 프로젝트 생성
1. https://console.cloud.google.com/ 접속
2. "프로젝트 만들기" → 프로젝트명: `notion-beeminder`
3. 생성 완료 대기 (1-2분)

## 2단계: Google Drive API 활성화
1. 좌측 메뉴 → "API 및 서비스" → "라이브러리"
2. "Google Drive API" 검색
3. "사용" 클릭

## 3단계: 서비스 계정 생성
1. 좌측 메뉴 → "API 및 서비스" → "사용자 인증 정보"
2. "만들기" → "서비스 계정"
3. 서비스 계정 이름: `notion-beeminder-bot`
4. "만들고 계속하기"
5. 역할: `Editor` (Google Drive 수정 권한)
6. "계속" → "완료"

## 4단계: 키 다운로드
1. 생성된 서비스 계정 클릭
2. "키" 탭
3. "키 추가" → "새 키" → "JSON" 
4. 다운로드된 파일을 아래 위치로 이동:
   ```
   C:\Users\wnsdu\.claude\google_drive_key.json
   ```

## 5단계: Google Drive 폴더 생성
1. Google Drive (https://drive.google.com) 접속
2. "+ 새로만들기" → "폴더"
3. 폴더명: `Beeminder 풀이 기록`
4. 폴더 우클릭 → "공유"
5. 아래 이메일로 공유 (읽기/쓰기):
   - **google_drive_key.json의 "client_email" 값 복사해서 입력**
   - 예: `notion-beeminder-bot@...iam.gserviceaccount.com`

## 6단계: 폴더 ID 확인
1. Google Drive에서 생성한 폴더 열기
2. URL에서 폴더 ID 추출:
   ```
   https://drive.google.com/drive/folders/1abc_DEF123_xyz456
                                          ^^^^^^^^^^^^^^^^^ <- 이 부분
   ```
3. 아래 환경변수 설정:
   ```
   GOOGLE_DRIVE_FOLDER_ID=1abc_DEF123_xyz456
   GOOGLE_DRIVE_KEY_PATH=C:\Users\wnsdu\.claude\google_drive_key.json
   ```

완료!

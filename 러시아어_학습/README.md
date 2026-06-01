# 기초러시아어 학습 - GitHub Pages 배포

이 저장소는 기초 러시아어 학습 웹사이트를 GitHub Pages에 배포하기 위한 것입니다.

## 빠른 시작 (5분)

### 1단계: 사전 준비
- GitHub 계정 필요 (없으면 https://github.com/signup 에서 무료로 생성)
- Git 설치 필요 (Windows: https://git-scm.com/download/win)

### 2단계: 저장소 생성 및 설정

이 저장소를 GitHub에 푸시하기 위해 다음 명령어를 실행하세요:

```bash
# 저장소 초기화
git init

# 원격 저장소 설정 (YOUR_USERNAME을 자신의 GitHub username으로 바꾸기)
git remote add origin https://github.com/YOUR_USERNAME/russian-learning.git

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Russian language learning website"

# 메인 브랜치로 푸시
git branch -M main
git push -u origin main
```

### 3단계: GitHub Pages 활성화

1. GitHub에서 저장소 열기
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Pages** 클릭
4. **Source** 섹션에서 **Branch: main** 선택
5. 저장 후 몇 초 대기

### 4단계: 공개 URL 확인

웹사이트는 다음 주소에서 접근 가능합니다:
```
https://YOUR_USERNAME.github.io/russian-learning/
```

## 파일 구조

```
russian-learning/
├── index.html              # 메인 학습 웹페이지
├── README.md              # 이 파일
├── deploy.sh              # 배포 스크립트
└── deployment_guide.txt   # 상세 배포 가이드
```

## 파일 설명

- **index.html**: 기초러시아어 학습 앱 (완전한 웹 기반 애플리케이션)
  - 교양수업 대비 완벽한 학습 자료
  - 오프라인에서도 작동

- **deploy.sh**: 자동 배포 스크립트
  - Git 저장소 자동 초기화
  - GitHub Pages 폴더 구조 생성
  - 배포 명령어 출력

## 배포 후 확인사항

- [ ] GitHub 저장소 생성됨
- [ ] `git push` 성공적으로 완료
- [ ] Settings > Pages에서 GitHub Pages 활성화됨
- [ ] 공개 URL에서 웹사이트 접근 가능
- [ ] 학습 앱이 정상 작동함

## 추가 지원

더 자세한 단계별 가이드는 `deployment_guide.txt` 파일을 참조하세요.

## 라이선스

이 프로젝트는 자유로운 사용을 목적으로 제공됩니다.

---
**배포 준비 완료**: 위의 명령어를 복사해서 터미널에 붙여넣기만 하면 됩니다!

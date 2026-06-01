#!/bin/bash
# Life System 자동 개선 루프
# 실행: bash improve_loop.sh

SITE_DIR="/c/Users/wnsdu/OneDrive/Desktop/claude code/life-system"
DEPLOY_SCRIPT="$SITE_DIR/deploy.py"
LOG="$SITE_DIR/improve_log.txt"
MAX=50       # 총 반복 횟수
PAUSE_AT=5   # N번마다 멈추고 확인

echo "🚀 Life System 자동 개선 루프 시작" | tee -a "$LOG"
echo "총 ${MAX}회 / ${PAUSE_AT}회마다 확인" | tee -a "$LOG"
echo "======================================" | tee -a "$LOG"

for i in $(seq 1 $MAX); do
  echo "" | tee -a "$LOG"
  echo "━━━ [${i}/${MAX}] 개선 실행 중... ━━━" | tee -a "$LOG"

  # Claude로 개선안 생성 + 적용
  claude --headless "
당신은 improver 에이전트입니다.
파일 경로: $SITE_DIR/index.html

현재 Life Command System HTML 파일을 읽고,
다음 중 아직 구현 안 된 기능 하나를 골라 실제로 코드에 반영하세요:

1. 태스크 우선순위 (🔴긴급 / 🟡중요 / ⚪일반) 태그
2. 마감일 설정 + D-day 표시
3. 브라우저 알림 (Notification API)
4. PWA manifest.json 추가
5. 전체 태스크 검색바
6. 주간 완료율 미니 통계 (7일 바 차트)
7. 자기소개서 재료 카테고리에 서술형 메모 에디터
8. 반복 태스크 (매일/매주) 설정
9. 태스크 완료 시 confetti 애니메이션
10. 다크/라이트 모드 토글

규칙:
- 반드시 실제 파일을 Edit 도구로 수정
- 한 번에 기능 하나만 추가 (작게, 확실하게)
- 기존 기능 절대 망가뜨리지 말 것
- 수정 완료 후 '✅ [기능명] 추가 완료'라고 출력
" 2>&1 | tee -a "$LOG"

  echo "[${i}] 완료: $(date '+%H:%M:%S')" | tee -a "$LOG"

  # N번마다 Netlify 재배포 + 확인
  if (( i % PAUSE_AT == 0 )); then
    echo "" | tee -a "$LOG"
    echo "======================================"
    echo "✋ ${i}번 완료 — Netlify 재배포 중..."
    python "$DEPLOY_SCRIPT" 2>&1 | tail -3
    echo ""
    echo "🌐 확인: https://junyeong-life-system.netlify.app"
    echo "계속하려면 Enter, 중단하려면 Ctrl+C"
    echo "======================================"
    read -r
  fi

done

echo "" | tee -a "$LOG"
echo "🎉 전체 ${MAX}회 개선 완료!" | tee -a "$LOG"
echo "최종 배포 중..." | tee -a "$LOG"
python "$DEPLOY_SCRIPT" 2>&1 | tail -3
echo "🌐 https://junyeong-life-system.netlify.app" | tee -a "$LOG"

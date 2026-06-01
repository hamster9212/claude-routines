#!/bin/bash

# 기초러시아어 학습 - GitHub Pages 배포 스크립트
# 이 스크립트는 GitHub Pages 배포를 위한 자동 설정을 수행합니다

echo "=========================================="
echo "GitHub Pages 배포 스크립트"
echo "=========================================="
echo ""

# Step 1: Git 저장소 초기화 확인
if [ ! -d ".git" ]; then
    echo "[1/4] Git 저장소 초기화 중..."
    git init
    echo "✓ Git 저장소 초기화 완료"
else
    echo "[1/4] ✓ Git 저장소 이미 존재"
fi

echo ""

# Step 2: GitHub Pages 폴더 구조 확인
echo "[2/4] GitHub Pages 폴더 구조 확인 중..."
if [ ! -f "index.html" ]; then
    echo "⚠ 경고: index.html 파일을 찾을 수 없습니다"
else
    echo "✓ index.html 파일 확인됨"
fi

echo ""

# Step 3: 필수 파일 확인
echo "[3/4] 배포 필수 파일 확인 중..."
files=("index.html" "README.md" ".gitignore")
missing=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        if [ "$file" != ".gitignore" ]; then
            echo "⚠ $file (필수 파일 없음)"
            ((missing++))
        fi
    fi
done

echo ""

# Step 4: 배포 명령어 안내
echo "[4/4] 배포 명령어 안내"
echo ""
echo "다음 명령어를 터미널에 붙여넣기하여 배포하세요:"
echo "=========================================="
echo ""
echo "# Step 1: 원격 저장소 설정 (YOUR_USERNAME을 자신의 GitHub username으로 바꾸기)"
echo "git remote add origin https://github.com/YOUR_USERNAME/russian-learning.git"
echo ""
echo "# Step 2: 모든 파일 추가"
echo "git add ."
echo ""
echo "# Step 3: 커밋"
echo "git commit -m \"Initial commit: Russian language learning website\""
echo ""
echo "# Step 4: 메인 브랜치로 푸시"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "=========================================="
echo ""

# Step 5: 최종 안내
echo "배포 후 설정:"
echo "1. GitHub에서 저장소 열기"
echo "2. Settings > Pages 클릭"
echo "3. Source: Branch main 선택"
echo "4. Save 클릭"
echo ""
echo "완료 후 접근 URL:"
echo "https://YOUR_USERNAME.github.io/russian-learning/"
echo ""
echo "=========================================="
echo "배포 스크립트 완료!"
echo "=========================================="

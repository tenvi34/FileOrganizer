#!/bin/bash
# 파일 정리 프로그램 자동 빌드 스크립트

echo "🚀 파일 정리 프로그램 빌드 스크립트"
echo "=================================="

# 운영체제 감지
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS 감지됨"
    PYTHON_CMD="python3"
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux 감지됨"
    PYTHON_CMD="python3"
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "🪟 Windows 감지됨"
    PYTHON_CMD="python"
    PLATFORM="Windows"
else
    echo "❓ 알 수 없는 운영체제: $OSTYPE"
    PYTHON_CMD="python3"
    PLATFORM="Unknown"
fi

# Python 확인
echo -e "\n📍 Python 확인 중..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python이 설치되지 않았습니다!"
    echo "   https://www.python.org 에서 설치하세요."
    exit 1
fi

$PYTHON_CMD --version

# 필수 패키지 설치
echo -e "\n📦 필수 패키지 설치 중..."
$PYTHON_CMD -m pip install -r requirements.txt
$PYTHON_CMD -m pip install pyinstaller

# macOS에서 tkinter 확인
if [[ "$PLATFORM" == "macOS" ]]; then
    echo -e "\n🔍 tkinter 확인 중..."
    if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
        echo "⚠️  tkinter가 설치되지 않았습니다!"
        echo "   실행: brew install python-tk"
        read -p "지금 설치하시겠습니까? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            brew install python-tk
        fi
    fi
fi

# 빌드 실행
echo -e "\n🔨 빌드 시작..."
$PYTHON_CMD build.py

# 결과 확인
if [ $? -eq 0 ]; then
    echo -e "\n✅ 빌드 성공!"
    
    # 실행 파일 위치 안내
    if [[ "$PLATFORM" == "Windows" ]]; then
        echo "📁 실행 파일: dist/FileOrganizer.exe"
    else
        echo "📁 실행 파일: dist/FileOrganizer"
        
        # 실행 권한 부여
        chmod +x dist/FileOrganizer
        echo "✓ 실행 권한 부여됨"
    fi
    
    # 실행 여부 확인
    read -p "지금 실행하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$PLATFORM" == "macOS" ]]; then
            open dist/FileOrganizer
        elif [[ "$PLATFORM" == "Linux" ]]; then
            ./dist/FileOrganizer
        fi
    fi
else
    echo -e "\n❌ 빌드 실패!"
    exit 1
fi
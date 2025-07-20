@echo off
chcp 65001 > nul
title 파일 정리 프로그램 빌드

echo 🚀 파일 정리 프로그램 빌드 스크립트
echo ==================================
echo.

rem Python 확인
echo 📍 Python 확인 중...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다!
    echo    https://www.python.org 에서 설치하세요.
    pause
    exit /b 1
)

python --version
echo.

rem 필수 패키지 설치
echo 📦 필수 패키지 설치 중...
python -m pip install -r requirements.txt
python -m pip install pyinstaller
echo.

rem 빌드 실행
echo 🔨 빌드 시작...
python build.py

if errorlevel 1 (
    echo.
    echo ❌ 빌드 실패!
    pause
    exit /b 1
)

echo.
echo ✅ 빌드 성공!
echo 📁 실행 파일: dist\FileOrganizer.exe
echo.

rem 실행 여부 확인
set /p RUN="지금 실행하시겠습니까? (y/n): "
if /i "%RUN%"=="y" (
    start "" "dist\FileOrganizer.exe"
)

pause
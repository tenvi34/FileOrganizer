#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 정리 프로그램 빌드 스크립트
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """빌드 디렉토리 정리"""
    print("🧹 빌드 디렉토리 정리 중...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.spec', '*.pyc']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✓ {dir_name} 디렉토리 삭제")
    
    # .pyc 파일과 __pycache__ 디렉토리 재귀적으로 삭제
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def check_requirements():
    """필수 패키지 확인"""
    print("📦 필수 패키지 확인 중...")
    
    required_packages = ['pyinstaller', 'send2trash']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} 설치됨")
        except ImportError:
            missing_packages.append(package)
            print(f"  ✗ {package} 미설치")
    
    if missing_packages:
        print("\n❌ 누락된 패키지를 설치하세요:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def build_executable():
    """실행 파일 빌드"""
    print("\n🔨 실행 파일 빌드 중...")
    
    # 플랫폼별 설정
    if sys.platform == "win32":
        icon_file = "icon.ico"
        exe_name = "FileOrganizer.exe"
    elif sys.platform == "darwin":
        icon_file = "icon.icns"
        exe_name = "FileOrganizer"
    else:
        icon_file = None
        exe_name = "FileOrganizer"
    
    # PyInstaller 명령어 구성
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--noupx",
        "--name", "FileOrganizer",
        "--add-data", f"src{os.pathsep}src",
    ]
    
    # 아이콘 파일이 있으면 추가
    if icon_file and os.path.exists(icon_file):
        cmd.extend(["--icon", icon_file])
    
    # hidden imports 추가
    cmd.extend([
        "--hidden-import", "tkinter",
        "--hidden-import", "send2trash",
    ])
    
    # main.py 추가
    cmd.append("main.py")
    
    print(f"  명령어: {' '.join(cmd)}")
    
    # 빌드 실행
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✓ 빌드 성공!")
        
        # 빌드된 파일 확인
        exe_path = os.path.join("dist", exe_name)
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print(f"\n📁 빌드 결과:")
            print(f"  - 파일: {exe_path}")
            print(f"  - 크기: {size_mb:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 빌드 실패!")
        print(f"에러 출력:\n{e.stderr}")
        return False

def create_installer():
    """설치 프로그램 생성 (선택사항)"""
    if sys.platform == "win32":
        print("\n📦 Windows 설치 프로그램 생성...")
        # NSIS나 Inno Setup 사용
        print("  ℹ️  NSIS 또는 Inno Setup을 사용하여 설치 프로그램을 만들 수 있습니다.")
    elif sys.platform == "darwin":
        print("\n📦 macOS DMG 생성...")
        # DMG 생성 스크립트
        print("  ℹ️  create-dmg를 사용하여 DMG 파일을 만들 수 있습니다.")

def main():
    """메인 함수"""
    print("🚀 파일 정리 프로그램 빌드 시작")
    print("=" * 50)
    
    # 1. 이전 빌드 정리
    if "--clean" in sys.argv:
        clean_build()
        print("\n✅ 정리 완료!")
        return
    
    # 2. 필수 패키지 확인
    if not check_requirements():
        sys.exit(1)
    
    # 3. 빌드 디렉토리 정리
    clean_build()
    
    # 4. 실행 파일 빌드
    if build_executable():
        print("\n✅ 빌드 완료!")
        
        # 5. 설치 프로그램 생성 (선택)
        if "--installer" in sys.argv:
            create_installer()
    else:
        print("\n❌ 빌드 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
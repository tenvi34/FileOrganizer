#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
"""
파일 자동 분류 프로그램
메인 진입점
"""

from src.app import FileOrganizerApp

def main():
    """메인 함수"""
    app = FileOrganizerApp()
    app.run()
    
if __name__ == "__main__":
    main()
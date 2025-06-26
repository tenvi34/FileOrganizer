#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 자동 분류 프로그램
메인 진입점
"""

from src.app import FileOrgaizerApp

def main():
    """메인 함수"""
    app = FileOrgaizerApp()
    app.run()
    
if __name__ == "__main__":
    main()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 자동 분류 프로그램
메인 애플리케이션 클래스
"""

import tkinter as tk
from src.ui.main_window import MainWindow

class FileOrgnizeApp:
    """메인 애플리케이션 클래스"""

    def __init__(self):
        """애플리케이션 초기화"""
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root)

    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()

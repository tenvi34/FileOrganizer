#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 자동 분류 프로그램
메인 애플리케이션 클래스
"""

import tkinter as tk
from src.ui.main_window import MainWindow

# tkinterdnd2 임포트 및 초기화
try:
    from tkinterdnd2 import TkinterDnD

    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("tkinterdnd2가 설치되지 않았습니다. 드래그 앤 드롭 기능이 비활성화됩니다.")


class FileOrganizerApp:
    """메인 애플리케이션 클래스"""

    def __init__(self):
        """애플리케이션 초기화"""
        # tkinterdnd2가 있으면 TkinterDnD.Tk() 사용, 없으면 일반 Tk() 사용
        if HAS_DND:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.main_window = MainWindow(self.root)

    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()

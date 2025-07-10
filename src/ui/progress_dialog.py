#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
진행률 표시 다이얼로그
"""

import tkinter as tk
from tkinter import ttk
import threading


class ProgressDialog(tk.Toplevel):
    """진행률 표시 다이얼로그"""
    
    def __init__(self, parent, title="작업 진행 중", can_cancel=True):
        """초기화
        
        Args:
            parent: 부모 윈도우
            title: 다이얼로그 제목
            can_cancel: 취소 버튼 표시 여부
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("450x200")
        self.resizable(False, False)
        
        # 모달 다이얼로그로 설정
        self.transient(parent)
        self.grab_set()
        
        # 중앙 배치
        self.update_idletasks()
        x = (self.winfo_screenwidth // 2) - (450 // 2)
        y = (self.winfo_screenheight // 2) - (200 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.cancelled = False
        self.can_cancel = can_cancel
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
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f"+{x}+{y}")

        self.cancelled = False
        self.can_cancel = can_cancel

        self.create_widgets()

        # 닫기 버튼 비활성화
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 메인 메시지
        self.message_label = ttk.Label(
            main_frame, text="작업을 시작하는 중...", font=("", 10, "bold")
        )
        self.message_label.pack(pady=(0, 10))

        # 진행률 바
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, length=400, mode="determinate", variable=self.progress_var
        )
        self.progress_bar.pack(pady=5)

        # 진행률 텍스트
        self.progress_label = ttk.Label(main_frame, text="0%")
        self.progress_label.pack(pady=5)

        # 상세 메시지
        self.detail_label = ttk.Label(main_frame, text="", foreground="gray")
        self.detail_label.pack(pady=5)

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))

        if self.can_cancel:
            self.cancel_button = ttk.Button(
                button_frame, text="취소", command=self.cancel
            )
            self.cancel_button.pack()

    def update_progress(self, current, total, message="", detail=""):
        """진행률 업데이트

        Args:
            current: 현재 값
            total: 전체 값
            message: 메인 메시지
            detail: 상세 메시지
        """
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{int(progress)}%")

        if message:
            self.message_label.config(text=message)

        if detail:
            self.detail_label.config(text=detail)

        self.update_idletasks()

    def set_indeterminate(self, message="처리 중..."):
        """불확정 모드 설정"""
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)
        self.message_label.config(text=message)
        self.progress_label.config(text="")

    def cancel(self):
        """작업 취소"""
        self.cancelled = True
        if self.can_cancel:
            self.cancel_button.config(state="disabled", text="취소 중...")

    def on_close(self):
        """닫기 버튼 처리"""
        if self.can_cancel:
            self.cancel()

    def close(self):
        """다이얼로그 닫기"""
        self.grab_release()
        self.destroy()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
대화상자 클래스들
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable


class LogWindow:
    """별도 로그 창"""

    def __init__(self, parent, content: str, refresh_callback: Callable):
        """초기화

        Args:
            parent: 부모 윈도우
            content: 로그 내용
            refresh_callback: 새로고침 콜백
        """
        self.window = tk.Toplevel(parent)
        self.window.title("로그 뷰어")
        self.window.geometry("800x600")

        self.refresh_callback = refresh_callback
        self._alive = True

        # 창 닫기 이벤트
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # UI 생성
        self.setup_ui()

        # 초기 내용 설정
        self.update_content(content)

    def setup_ui(self):
        """UI 구성"""
        # 프레임
        frame = ttk.Frame(self.window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 버튼
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(button_frame, text="새로고침", command=self.refresh).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="모두 복사", command=self.copy_all).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="닫기", command=self.on_close).pack(
            side=tk.LEFT, padx=2
        )

        # 텍스트 위젯
        self.text_widget = tk.Text(frame, wrap=tk.WORD, height=30)
        scrollbar = ttk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self.text_widget.yview
        )
        self.text_widget.configure(yscrollcommand=scrollbar.set)

        self.text_widget.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # 그리드 가중치
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

    def update_content(self, content: str):
        """내용 업데이트"""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, content)
        self.text_widget.see(tk.END)

    def refresh(self):
        """새로고침"""
        if self.refresh_callback:
            self.refresh_callback()

    def copy_all(self):
        """전체 내용 복사"""
        self.window.clipboard_clear()
        self.window.clipboard_append(self.text_widget.get(1.0, tk.END))
        messagebox.showinfo("복사 완료", "로그가 클립보드에 복사되었습니다.")

    def lift(self):
        """창을 최상위로"""
        self.window.lift()
        self.window.focus_force()

    def on_close(self):
        """창 닫기"""
        self._alive = False
        self.window.destroy()

    def is_alive(self) -> bool:
        """창이 남아있는지 화인"""
        return self._alive and self.window.winfo_exists()

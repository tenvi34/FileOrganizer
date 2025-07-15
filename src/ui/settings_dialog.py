#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
고급 설정 다이얼로그
"""

import tkinter as tk
from tkinter import ttk


class AdvancedSettingsDialog(tk.Toplevel):
    """고급 설정 다이얼로그"""

    def __init__(self, parent, current_settings):
        """초기화"""
        super().__init__(parent)
        self.title("고급 설정")
        self.geometry("500x400")
        self.resizable(False, False)

        # 모달 다이얼로그
        self.transient(parent)
        self.grab_set()

        self.current_settings = current_settings
        self.result = None

        self.create_widgets()
        self.load_settings()

        # 중앙 배치
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (250)
        y = (self.winfo_screenheight() // 2) - (200)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """위젯 생성"""
        # 노트북 (탭)
        notebook = ttk.Notebook(self, padding="10")
        notebook.pack(fill=tk.BOTH, expand=True)

        # 성능 탭
        self.create_performance_tab(notebook)

        # 검증 탭
        self.create_verification_tab(notebook)

        # 네트워크 탭
        self.create_network_tab(notebook)

        # 버튼 프레임
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="확인", command=self.ok_clicked).pack(
            side=tk.RIGHT, padx=5
        )

        ttk.Button(button_frame, text="취소", command=self.cancel_clicked).pack(
            side=tk.RIGHT, padx=5
        )

    def create_performance_tab(self, parent):
        """성능 설정 탭"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="성능")

        # 멀티스레드 복사
        self.multithread_var = tk.BooleanVar()
        ttk.Checkbutton(
            frame,
            text="대용량 파일(1GB+) 멀티스레드 복사 사용",
            variable=self.multithread_var,
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        # 스레드 수
        ttk.Label(frame, text="동시 작업 스레드 수:").grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.thread_count_var = tk.IntVar()
        thread_spinbox = ttk.Spinbox(
            frame, from_=1, to=8, textvariable=self.thread_count_var, width=10
        )
        thread_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)

        # 캐시 크기
        ttk.Label(frame, text="파일 정보 캐시 크기:").grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.cache_size_var = tk.IntVar()
        cache_spinbox = ttk.Spinbox(
            frame,
            from_=1000,
            to=50000,
            increment=1000,
            textvariable=self.cache_size_var,
            width=10,
        )
        cache_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)

        # 배치 크기
        ttk.Label(frame, text="파일 스캔 배치 크기:").grid(
            row=3, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.batch_size_var = tk.IntVar()
        batch_spinbox = ttk.Spinbox(
            frame,
            from_=50,
            to=1000,
            increment=50,
            textvariable=self.batch_size_var,
            width=10,
        )
        batch_spinbox.grid(row=3, column=1, sticky=tk.W, pady=5)

    def create_verification_tab(self, parent):
        """검증 설정 탭"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="검증")

        # 복사 후 검증
        self.verify_copy_var = tk.BooleanVar()
        ttk.Checkbutton(
            frame,
            text="대용량 파일(100MB+) 복사 후 검증",
            variable=self.verify_copy_var,
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        # 검증 방법
        ttk.Label(frame, text="검증 방법:").grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.verify_method_var = tk.StringVar()
        ttk.Radiobutton(
            frame,
            text="빠른 검증 (크기만)",
            variable=self.verify_method_var,
            value="quick",
        ).grid(row=2, column=0, sticky=tk.W, padx=30, pady=2)

        ttk.Radiobutton(
            frame,
            text="완전 검증 (MD5 해시)",
            variable=self.verify_method_var,
            value="full",
        ).grid(row=3, column=0, sticky=tk.W, padx=30, pady=2)

        # 검증 실패 시 동작
        ttk.Label(frame, text="검증 실패 시:").grid(
            row=4, column=0, sticky=tk.W, padx=10, pady=(20, 5)
        )

        self.verify_fail_var = tk.StringVar()
        ttk.Radiobutton(
            frame, text="재시도", variable=self.verify_fail_var, value="retry"
        ).grid(row=5, column=0, sticky=tk.W, padx=30, pady=2)

        ttk.Radiobutton(
            frame, text="건너뛰기", variable=self.verify_fail_var, value="skip"
        ).grid(row=6, column=0, sticky=tk.W, padx=30, pady=2)

        ttk.Radiobutton(
            frame, text="중단", variable=self.verify_fail_var, value="abort"
        ).grid(row=7, column=0, sticky=tk.W, padx=30, pady=2)

    def create_network_tab(self, parent):
        """네트워크 설정 탭"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="네트워크")

        # 네트워크 드라이브 최적화
        self.network_optimize_var = tk.BooleanVar()
        ttk.Checkbutton(
            frame,
            text="네트워크 드라이브 자동 감지 및 최적화",
            variable=self.network_optimize_var,
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        # 네트워크 청크 크기
        ttk.Label(frame, text="네트워크 전송 청크 크기:").grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.network_chunk_var = tk.StringVar()
        chunk_combo = ttk.Combobox(
            frame,
            textvariable=self.network_chunk_var,
            values=["10MB", "50MB", "100MB", "200MB"],
            state="readonly",
            width=15,
        )
        chunk_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # 네트워크 타임아웃
        ttk.Label(frame, text="네트워크 타임아웃 (초):").grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=5
        )

        self.timeout_var = tk.IntVar()
        timeout_spinbox = ttk.Spinbox(
            frame,
            from_=30,
            to=600,
            increment=30,
            textvariable=self.timeout_var,
            width=10,
        )
        timeout_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)

    def load_settings(self):
        """현재 설정 로드"""
        # 성능
        self.multithread_var.set(self.current_settings.get("multithread_copy", True))
        self.thread_count_var.set(self.current_settings.get("thread_count", 4))
        self.cache_size_var.set(self.current_settings.get("cache_size", 5000))
        self.batch_size_var.set(self.current_settings.get("batch_size", 100))

        # 검증
        self.verify_copy_var.set(self.current_settings.get("verify_copy", True))
        self.verify_method_var.set(self.current_settings.get("verify_method", "quick"))
        self.verify_fail_var.set(
            self.current_settings.get("verify_fail_action", "retry")
        )

        # 네트워크
        self.network_optimize_var.set(
            self.current_settings.get("network_optimize", True)
        )
        self.network_chunk_var.set(
            self.current_settings.get("network_chunk_size", "50MB")
        )
        self.timeout_var.set(self.current_settings.get("network_timeout", 120))

    def ok_clicked(self):
        """확인 버튼 클릭"""
        self.result = {
            # 성능
            "multithread_copy": self.multithread_var.get(),
            "thread_count": self.thread_count_var.get(),
            "cache_size": self.cache_size_var.get(),
            "batch_size": self.batch_size_var.get(),
            # 검증
            "verify_copy": self.verify_copy_var.get(),
            "verify_method": self.verify_method_var.get(),
            "verify_fail_action": self.verify_fail_var.get(),
            # 네트워크
            "network_optimize": self.network_optimize_var.get(),
            "network_chunk_size": self.network_chunk_var.get(),
            "network_timeout": self.timeout_var.get(),
        }
        self.destroy()

    def cancel_clicked(self):
        """취소 버튼 클릭"""
        self.result = None
        self.destroy()

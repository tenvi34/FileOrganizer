#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
상태 패널 UI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class StatusPanel:
    """상태 패널 클래스"""

    def __init__(self, parent, logger, callbacks):
        """초기화

        Args:
            parent: 부모 위젯
            logger: 로거
            callbacks: 콜백 함수 딕셔너리
        """
        self.parent = parent
        self.logger = logger
        self.callbacks = callbacks

        # 진행률 변수
        self.progress_var = tk.DoubleVar()

        # 통계 라벨 딕셔너리
        self.stats_labels = {}

        # 프레임 생성
        self.create_panel()

    def create_panel(self):
        """패널 생성"""
        # 상태 프레임
        self.frame = ttk.Frame(self.parent, style="Panel.TFrame", width=400)
        self.frame.pack_propagate(False)

        # 헤더
        ttk.Label(self.frame, text="📊 상태", style="Header.TLabel").pack(pady=5)

        # 통계 정보
        self.create_stats_frame()

        # 진행률
        self.create_progress_frame()

        # 로그
        self.create_log_frame()

    def create_stats_frame(self):
        """통계 프레임 생성"""
        stats_frame = ttk.LabelFrame(self.frame, text="통계", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        stats = [
            ("total_files", "전체 파일:"),
            ("selected_files", "선택된 파일:"),
            ("processed_files", "처리된 파일:"),
            ("success_count", "성공:"),
            ("error_count", "실패:"),
        ]

        for i, (key, label) in enumerate(stats):
            ttk.Label(stats_frame, text=label).grid(
                row=i, column=0, sticky=tk.W, pady=2
            )
            self.stats_labels[key] = ttk.Label(stats_frame, text="0")
            self.stats_labels[key].grid(
                row=i, column=1, sticky=tk.E, pady=2, padx=(20, 0)
            )

        stats_frame.columnconfigure(0, weight=1)

    def create_progress_frame(self):
        """진행률 프레임 생성"""
        progress_frame = ttk.LabelFrame(self.frame, text="진행률", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.progress_label = ttk.Label(progress_frame, text="대기 중...")
        self.progress_label.pack()

    def create_log_frame(self):
        """로그 프레임 생성"""
        log_frame = ttk.LabelFrame(self.frame, text="로그", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 로그 버튼
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            log_button_frame, text="지우기", command=self.clear_log, width=8
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_button_frame, text="저장", command=self.save_log, width=8).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            log_button_frame,
            text="별도창",
            command=self.callbacks.get("open_log_window"),
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        # 로그 텍스트
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15)
        log_scrollbar = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_stats(self, stats_dict):
        """통계 정보 업데이트

        Args:
            stats_dict: 통계 정보 딕셔너리
        """
        for key, value in stats_dict.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=str(value))

    def update_stat(self, key, value):
        """개별 통계 업데이트

        Args:
            key: 통계 키
            value: 값
        """
        if key in self.stats_labels:
            self.stats_labels[key].config(text=str(value))

    def update_progress(self, current, total, message=""):
        """진행률 업데이트

        Args:
            current: 현재 값
            total: 전체 값
            message: 메시지
        """
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=message)
        else:
            self.progress_var.set(0)
            self.progress_label.config(text=message)

    def log(self, message):
        """로그 메시지 출력

        Args:
            message: 로그 메시지
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
        self.log("로그를 지웠습니다.")

    def save_log(self):
        """로그 저장"""
        log_content = self.log_text.get(1.0, tk.END)
        saved_path = self.logger.save_log_with_dialog(log_content)
        if saved_path:
            messagebox.showinfo("저장 완료", f"로그가 저장되었습니다:\n{saved_path}")

    def get_log_content(self):
        """로그 내용 반환"""
        return self.log_text.get(1.0, tk.END)

    def reset_progress(self):
        """진행률 초기화"""
        self.progress_var.set(0)
        self.progress_label.config(text="대기 중...")

    def reset_stats(self):
        """통계 초기화"""
        for label in self.stats_labels.values():
            label.config(text="0")

    def get_widget(self):
        """위젯 반환"""
        return self.frame

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
메인 윈도우 UI - 3단 레이아웃 버전
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import sys
from datetime import datetime

from src.constants import *
from src.core import FileMatcher, FileProcessor, RuleManager
from src.ui.dialogs import LogWindow
from src.utils.logger import Logger
from src.utils.validators import Validator


class MainWindow:
    """메인 윈도우 클래스 - 3단 레이아웃"""

    def __init__(self, root):
        """초기화"""
        self.root = root
        # 플랫폼 감지
        self.is_macos = sys.platform == 'darwin'
        self.is_windows = sys.platform == 'win32'
        
        # 플랫폼별 설정
        if self.is_macos:
            self.root.title(f"{APP_TITLE} v{APP_VERSION}")
            self.root.geometry(f"{MAC_SIZE}")
        else:
            self.root.title(f"{APP_TITLE} v{APP_VERSION}")
            self.root.geometry(f"{WINDOW_SIZE}")

        # 스타일 설정
        self.setup_styles()

        # 컴포넌트 초기화
        self.rule_manager = RuleManager(CONFIG_FILE)
        self.file_matcher = FileMatcher()
        self.file_processor = FileProcessor(log_callback=self.log)
        self.logger = Logger(LOG_DIR)
        self.validator = Validator()

        # UI 변수
        self.source_var = tk.StringVar()
        self.keyword_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.match_mode_var = tk.StringVar(value=DEFAULT_MATCH_MODE)
        self.subfolder_var = tk.BooleanVar(value=True)
        self.copy_var = tk.BooleanVar(value=False)
        self.delete_var = tk.BooleanVar(value=False)
        self.permanent_delete_var = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar()

        # 파일 목록 관련 변수
        self.file_list_data = []  # 매칭된 파일 정보
        self.file_vars = {}  # 체크박스 변수들

        # 로그 창 변수
        self.log_window = None

        # UI 설정
        self.setup_ui()

        # 규칙 목록 업데이트
        self.update_rule_list()

    def setup_styles(self):
        """스타일 설정 - 흰색/파랑 테마"""
        style = ttk.Style()

        # 테마 설정
        # macOS 호환 수정
        if sys.platform == 'darwin':
            style.theme_use('aqua')  # macOS 네이티브 테마
        else:
            style.theme_use('clam')

        # 색상 팔레트 정의 (흰색-파랑 조합)
        main_bg = "#FAFBFC"  # 매우 밝은 회색 (거의 흰색)
        panel_bg = "#FFFFFF"  # 순수 흰색
        primary_blue = "#0066CC"  # 메인 파란색
        light_blue = "#E6F2FF"  # 매우 연한 파란색
        hover_blue = "#0052A3"  # 호버 시 진한 파란색
        border_color = "#E1E4E8"  # 연한 테두리
        text_primary = "#24292E"  # 진한 텍스트
        text_secondary = "#586069"  # 연한 텍스트

        # 메인 배경색 설정
        self.root.configure(bg=main_bg)

        # 프레임 스타일
        style.configure(
            "Panel.TFrame", background=panel_bg, relief=tk.FLAT, borderwidth=1
        )

        style.configure("TFrame", background=main_bg)

        # 헤더 라벨 스타일
        style.configure(
            "Header.TLabel",
            font=('Helvetica' if sys.platform == 'darwin' else 'Segoe UI', 12, 'bold'),
            background=panel_bg,
            foreground=primary_blue,
        )

        # 일반 라벨 스타일
        style.configure("TLabel", background=panel_bg, foreground=text_primary)

        # 버튼 스타일 - macOS 특별 처리
        if self.is_macos:
            # macOS aqua 테마에서 버튼 글자색만 검은색으로
            style.configure('TButton',
                            foreground='black',
                            font=('Helvetica', 9))
            
            # 액센트 버튼도 글자색 설정
            style.configure('Accent.TButton',
                            foreground='black',
                            font=('Helvetica', 10, 'bold'))
        else:
            # Windows/Linux
            style.configure('TButton',
                            background=primary_blue,
                            foreground='white',
                            borderwidth=0,
                            focuscolor='none',
                            font=('Segoe UI', 9),
                            padding=(10, 5))
            
            style.map('TButton',
                        background=[('active', hover_blue), ('pressed', hover_blue)],
                        foreground=[('active', 'white')])
            
            # 액센트 버튼 (실행 버튼용)
            style.configure('Accent.TButton',
                            background='#28A745',
                            foreground='white',
                            font=('Segoe UI', 10, 'bold'),
                            padding=(15, 8))
            
            style.map('Accent.TButton',
                    background=[('active', '#218838')])

        # LabelFrame 스타일
        style.configure(
            "TLabelframe",
            background=panel_bg,
            borderwidth=1,
            relief=tk.SOLID,
            bordercolor=border_color,
        )

        style.configure(
            "TLabelframe.Label",
            background=panel_bg,
            foreground=primary_blue,
            font=("Segoe UI", 10, "bold"),
        )

        # Entry 스타일
        style.configure(
            "TEntry",
            fieldbackground="white",
            borderwidth=1,
            relief=tk.SOLID,
            bordercolor=border_color,
            insertcolor=primary_blue,
        )

        style.map("TEntry", bordercolor=[("focus", primary_blue)])

        # Combobox 스타일
        style.configure(
            "TCombobox",
            fieldbackground="white",
            borderwidth=1,
            relief=tk.SOLID,
            bordercolor=border_color,
            arrowcolor=primary_blue,
        )

        # Treeview 스타일
        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            borderwidth=1,
            relief=tk.SOLID,
            bordercolor=border_color,
            foreground=text_primary,
        )

        style.configure(
            "Treeview.Heading",
            background=light_blue,
            foreground=text_primary,
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
        )

        style.map("Treeview.Heading", background=[("active", "#CCE5FF")])

        # 선택된 아이템 스타일
        style.map(
            "Treeview",
            background=[("selected", primary_blue)],
            foreground=[("selected", "white")],
        )

        # Notebook (탭) 스타일
        style.configure(
            "TNotebook", background=panel_bg, borderwidth=0, tabmargins=[0, 0, 0, 0]
        )

        style.configure(
            "TNotebook.Tab",
            background="#F6F8FA",
            foreground=text_secondary,
            padding=[20, 10],
            font=("Segoe UI", 9),
            borderwidth=0,
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", panel_bg)],
            foreground=[("selected", primary_blue)],
        )

        # Checkbutton 스타일
        style.configure(
            "TCheckbutton",
            background=panel_bg,
            foreground=text_primary,
            focuscolor="none",
        )

        # Radiobutton 스타일
        style.configure(
            "TRadiobutton",
            background=panel_bg,
            foreground=text_primary,
            focuscolor="none",
        )

        # Progressbar 스타일
        style.configure(
            "TProgressbar",
            background=primary_blue,
            troughcolor=light_blue,
            borderwidth=0,
            lightcolor=primary_blue,
            darkcolor=primary_blue,
        )

        # Scrollbar 스타일
        style.configure(
            "TScrollbar",
            background="#F0F0F0",
            bordercolor="#F0F0F0",
            arrowcolor=text_secondary,
            troughcolor="white",
        )

        style.map("TScrollbar", background=[("active", "#D0D0D0")])

    def setup_ui(self):
        """UI 구성 - 3단 레이아웃"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # PanedWindow로 3개 영역 분할
        self.paned_window = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 1. 설정 패널 (왼쪽)
        self.setup_settings_panel()

        # 2. 파일 목록 패널 (중앙)
        self.setup_file_list_panel()

        # 3. 상태 패널 (오른쪽)
        self.setup_status_panel()

    def setup_settings_panel(self):
        """설정 패널 구성"""
        # 설정 패널 프레임
        settings_frame = ttk.Frame(self.paned_window, style="Panel.TFrame", width=400)
        settings_frame.pack_propagate(False)
        self.paned_window.add(settings_frame, weight=1)

        # 헤더
        header = ttk.Label(settings_frame, text="⚙️ 설정", style="Header.TLabel")
        header.pack(pady=5)

        # 노트북 (탭) 위젯
        self.settings_notebook = ttk.Notebook(settings_frame)
        self.settings_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 탭 1: 기본 설정
        self.setup_basic_settings_tab()

        # 탭 2: 규칙 관리
        self.setup_rules_tab()

        # 탭 3: 작업 옵션
        self.setup_options_tab()

    def setup_basic_settings_tab(self):
        """기본 설정 탭"""
        basic_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(basic_frame, text="기본 설정")

        # 작업 폴더 설정
        folder_frame = ttk.LabelFrame(basic_frame, text="작업 폴더", padding=10)
        folder_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(folder_frame, text="대상 폴더:").pack(anchor=tk.W)

        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(folder_select_frame, textvariable=self.source_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(
            folder_select_frame, text="선택", command=self.select_source_folder, width=8
        ).pack(side=tk.LEFT, padx=(5, 0))

        ttk.Checkbutton(
            folder_frame, text="하위 폴더 포함", variable=self.subfolder_var
        ).pack(anchor=tk.W, pady=5)

        # 최근 폴더 목록
        recent_frame = ttk.LabelFrame(basic_frame, text="최근 사용 폴더", padding=10)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.recent_listbox = tk.Listbox(recent_frame, height=8)
        self.recent_listbox.pack(fill=tk.BOTH, expand=True)
        self.recent_listbox.bind("<Double-Button-1>", self.on_recent_folder_select)

    def setup_rules_tab(self):
        """규칙 관리 탭"""
        rules_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(rules_frame, text="규칙 관리")

        # 규칙 추가 프레임
        add_rule_frame = ttk.LabelFrame(rules_frame, text="새 규칙 추가", padding=10)
        add_rule_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(add_rule_frame, text="키워드:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        ttk.Entry(add_rule_frame, textvariable=self.keyword_var).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=2
        )

        ttk.Label(add_rule_frame, text="매칭 방식:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Combobox(
            add_rule_frame,
            textvariable=self.match_mode_var,
            values=MATCH_MODES,
            state="readonly",
            width=18,
        ).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(add_rule_frame, text="대상 폴더:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        dest_frame = ttk.Frame(add_rule_frame)
        dest_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Entry(dest_frame, textvariable=self.dest_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(
            dest_frame, text="...", command=self.select_dest_folder, width=3
        ).pack(side=tk.LEFT, padx=(2, 0))

        ttk.Button(add_rule_frame, text="규칙 추가", command=self.add_rule).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        add_rule_frame.columnconfigure(1, weight=1)

        # 규칙 목록
        list_frame = ttk.LabelFrame(rules_frame, text="현재 규칙", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 규칙 트리뷰
        self.rule_tree = ttk.Treeview(
            list_frame,
            columns=("enabled", "keyword", "match", "dest"),
            show="tree headings",
            height=10,
        )
        self.rule_tree.heading("enabled", text="✓")
        self.rule_tree.heading("keyword", text="키워드")
        self.rule_tree.heading("match", text="매칭")
        self.rule_tree.heading("dest", text="대상 폴더")

        self.rule_tree.column("#0", width=0, stretch=False)
        self.rule_tree.column("enabled", width=30, anchor="center")
        self.rule_tree.column("keyword", width=80)
        self.rule_tree.column("match", width=60)
        self.rule_tree.column("dest", width=150)

        rule_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.rule_tree.yview
        )
        self.rule_tree.configure(yscrollcommand=rule_scrollbar.set)

        self.rule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rule_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.rule_tree.bind("<Button-1>", self.on_rule_click)

        # 규칙 관리 버튼
        rule_button_frame = ttk.Frame(rules_frame)
        rule_button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(rule_button_frame, text="선택 삭제", command=self.delete_rule).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            rule_button_frame, text="전체 선택", command=self.select_all_rules
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            rule_button_frame, text="전체 해제", command=self.deselect_all_rules
        ).pack(side=tk.LEFT, padx=2)

    def setup_options_tab(self):
        """작업 옵션 탭"""
        options_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(options_frame, text="작업 옵션")

        # 작업 유형 선택
        operation_frame = ttk.LabelFrame(options_frame, text="작업 유형", padding=10)
        operation_frame.pack(fill=tk.X, padx=10, pady=10)

        self.operation_var = tk.StringVar(value="move")
        ttk.Radiobutton(
            operation_frame,
            text="파일 이동",
            variable=self.operation_var,
            value="move",
            command=self.on_operation_change,
        ).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            operation_frame,
            text="파일 복사",
            variable=self.operation_var,
            value="copy",
            command=self.on_operation_change,
        ).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            operation_frame,
            text="파일 삭제",
            variable=self.operation_var,
            value="delete",
            command=self.on_operation_change,
        ).pack(anchor=tk.W, pady=2)

        # 삭제 옵션
        self.delete_options_frame = ttk.LabelFrame(
            options_frame, text="삭제 옵션", padding=10
        )
        self.delete_options_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Checkbutton(
            self.delete_options_frame,
            text="영구 삭제 (복구 불가)",
            variable=self.permanent_delete_var,
        ).pack(anchor=tk.W)

        # 초기 상태 설정
        self.delete_options_frame.pack_forget()

        # 작업 버튼
        action_frame = ttk.Frame(options_frame)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.preview_button = ttk.Button(
            action_frame, text="미리보기", command=self.preview_files
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.execute_button = ttk.Button(
            action_frame,
            text="작업 실행",
            command=self.organize_files,
            style="Accent.TButton",
        )
        self.execute_button.pack(side=tk.LEFT, padx=5)

    def setup_file_list_panel(self):
        """파일 목록 패널 구성"""
        # 파일 목록 프레임
        file_frame = ttk.Frame(self.paned_window, style="Panel.TFrame", width=600)
        file_frame.pack_propagate(False)
        self.paned_window.add(file_frame, weight=2)

        # 헤더
        header_frame = ttk.Frame(file_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(header_frame, text="📁 파일 목록", style="Header.TLabel").pack(
            side=tk.LEFT
        )

        self.file_count_label = ttk.Label(header_frame, text="(0개 파일)")
        self.file_count_label.pack(side=tk.LEFT, padx=10)

        # 도구 모음
        toolbar_frame = ttk.Frame(file_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(
            toolbar_frame, text="전체 선택", command=self.select_all_files, width=10
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            toolbar_frame, text="전체 해제", command=self.deselect_all_files, width=10
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            toolbar_frame, text="새로고침", command=self.refresh_file_list, width=10
        ).pack(side=tk.LEFT, padx=2)

        # 파일 트리뷰
        tree_frame = ttk.Frame(file_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_tree = ttk.Treeview(
            tree_frame,
            columns=("check", "filename", "size", "modified", "rule", "destination"),
            show="tree headings",
        )

        self.file_tree.heading("check", text="✓")
        self.file_tree.heading("filename", text="파일명")
        self.file_tree.heading("size", text="크기")
        self.file_tree.heading("modified", text="수정일")
        self.file_tree.heading("rule", text="매칭 규칙")
        self.file_tree.heading("destination", text="대상")

        self.file_tree.column("#0", width=0, stretch=False)
        self.file_tree.column("check", width=30, anchor="center")
        self.file_tree.column("filename", width=200)
        self.file_tree.column("size", width=80)
        self.file_tree.column("modified", width=120)
        self.file_tree.column("rule", width=100)
        self.file_tree.column("destination", width=150)

        file_scrollbar_y = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.file_tree.yview
        )
        file_scrollbar_x = ttk.Scrollbar(
            tree_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview
        )
        self.file_tree.configure(
            yscrollcommand=file_scrollbar_y.set, xscrollcommand=file_scrollbar_x.set
        )

        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        file_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        file_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.file_tree.bind("<Button-1>", self.on_file_click)

    def setup_status_panel(self):
        """상태 패널 구성"""
        # 상태 프레임
        status_frame = ttk.Frame(self.paned_window, style="Panel.TFrame", width=400)
        status_frame.pack_propagate(False)
        self.paned_window.add(status_frame, weight=1)

        # 헤더
        ttk.Label(status_frame, text="📊 상태", style="Header.TLabel").pack(pady=5)

        # 통계 정보
        stats_frame = ttk.LabelFrame(status_frame, text="통계", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        self.stats_labels = {}
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

        # 진행률
        progress_frame = ttk.LabelFrame(status_frame, text="진행률", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.progress_label = ttk.Label(progress_frame, text="대기 중...")
        self.progress_label.pack()

        # 로그
        log_frame = ttk.LabelFrame(status_frame, text="로그", padding=5)
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
            log_button_frame, text="별도창", command=self.open_log_window, width=8
        ).pack(side=tk.LEFT, padx=2)

        # 로그 텍스트
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15)
        log_scrollbar = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 이벤트 핸들러들
    def select_source_folder(self):
        """소스 폴더 선택"""
        folder = filedialog.askdirectory(title="대상 폴더 선택")
        if folder:
            self.source_var.set(folder)
            self.add_to_recent_folders(folder)
            self.refresh_file_list()

    def select_dest_folder(self):
        """대상 폴더 선택"""
        folder = filedialog.askdirectory(title="이동할 폴더 선택")
        if folder:
            self.dest_var.set(folder)

    def add_to_recent_folders(self, folder):
        """최근 폴더에 추가"""
        # TODO: 최근 폴더 목록 관리 구현
        if hasattr(self, "recent_listbox"):
            items = list(self.recent_listbox.get(0, tk.END))
            if folder not in items:
                self.recent_listbox.insert(0, folder)
                if self.recent_listbox.size() > 10:
                    self.recent_listbox.delete(10)

    def on_recent_folder_select(self, event):
        """최근 폴더 선택"""
        selection = self.recent_listbox.curselection()
        if selection:
            folder = self.recent_listbox.get(selection[0])
            self.source_var.set(folder)
            self.refresh_file_list()

    def on_operation_change(self):
        """작업 유형 변경"""
        operation = self.operation_var.get()

        if operation == "delete":
            self.delete_options_frame.pack(fill=tk.X, padx=10, pady=10)
            self.delete_var.set(True)
            self.copy_var.set(False)
        else:
            self.delete_options_frame.pack_forget()
            self.delete_var.set(False)
            self.copy_var.set(operation == "copy")
            self.permanent_delete_var.set(False)

    def add_rule(self):
        """규칙 추가"""
        keyword = self.keyword_var.get().strip()
        dest = self.dest_var.get().strip()
        match_mode = self.match_mode_var.get()

        if not keyword:
            messagebox.showwarning("경고", "키워드를 입력하세요.")
            return

        if not self.delete_var.get() and not dest:
            messagebox.showwarning("경고", "대상 폴더를 선택하세요.")
            return

        if self.rule_manager.add_rule(keyword, dest, match_mode):
            self.update_rule_list()
            # 입력 필드 초기화
            self.keyword_var.set("")
            self.dest_var.set("")
            self.match_mode_var.set(DEFAULT_MATCH_MODE)
            self.log(f"규칙 추가: '{keyword}' → '{dest}' (매칭: {match_mode})")
            self.refresh_file_list()

    def delete_rule(self):
        """선택한 규칙 삭제"""
        selected = self.rule_tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 규칙을 선택하세요.")
            return

        item = self.rule_tree.item(selected[0])
        keyword = item["values"][1]

        if messagebox.askyesno("확인", f"'{keyword}' 규칙을 삭제하시겠습니까?"):
            if self.rule_manager.delete_rule(keyword):
                self.update_rule_list()
                self.log(f"규칙 삭제: '{keyword}'")
                self.refresh_file_list()

    def select_all_rules(self):
        """모든 규칙 선택"""
        self.rule_manager.set_all_rules_enabled(True)
        self.update_rule_list()
        self.refresh_file_list()

    def deselect_all_rules(self):
        """모든 규칙 해제"""
        self.rule_manager.set_all_rules_enabled(False)
        self.update_rule_list()
        self.refresh_file_list()

    def on_rule_click(self, event):
        """규칙 트리뷰 클릭 이벤트"""
        region = self.rule_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.rule_tree.identify_column(event.x)
            if column == "#1":  # 활성화 열
                item = self.rule_tree.identify_row(event.y)
                if item:
                    keyword = self.rule_tree.item(item)["values"][1]
                    self.rule_manager.toggle_rule(keyword)
                    self.update_rule_list()
                    self.refresh_file_list()

    def update_rule_list(self):
        """규칙 목록 업데이트"""
        # 기존 항목 삭제
        for item in self.rule_tree.get_children():
            self.rule_tree.delete(item)

        # 규칙 추가
        for keyword, rule_data in self.rule_manager.get_rules_list():
            if isinstance(rule_data, dict):
                dest = rule_data.get("dest", "")
                match_mode = rule_data.get("match_mode", "포함")
                enabled = rule_data.get("enabled", True)
            else:
                dest = rule_data
                match_mode = "포함"
                enabled = True

            check_mark = "✓" if enabled else ""

            if self.delete_var.get():
                dest_display = "(삭제)"
            else:
                dest_display = os.path.basename(dest) if dest else ""

            self.rule_tree.insert(
                "", "end", values=(check_mark, keyword, match_mode, dest_display)
            )

    def refresh_file_list(self):
        """파일 목록 새로고침"""
        # 기존 목록 초기화
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        self.file_list_data.clear()
        self.file_vars.clear()

        source = self.source_var.get()
        if not source or not os.path.exists(source):
            self.file_count_label.config(text="(0개 파일)")
            self.update_stats()
            return

        active_rules = self.rule_manager.get_active_rules()
        if not active_rules:
            self.file_count_label.config(text="(0개 파일)")
            self.update_stats()
            return

        # 매칭되는 파일 찾기
        count = 0
        for (
            file_path,
            dest_folder,
            keyword,
            match_mode,
        ) in self.file_matcher.find_matching_files_generator(
            source, active_rules, self.subfolder_var.get()
        ):
            file_info = self.get_file_info(file_path, dest_folder, keyword, match_mode)
            self.file_list_data.append(file_info)

            # 트리에 추가
            item_id = self.file_tree.insert(
                "",
                "end",
                values=(
                    "✓",  # 기본적으로 체크
                    file_info["filename"],
                    file_info["size"],
                    file_info["modified"],
                    file_info["rule"],
                    file_info["destination"],
                ),
            )

            # 체크박스 상태 저장
            self.file_vars[item_id] = tk.BooleanVar(value=True)
            count += 1

        self.file_count_label.config(text=f"({count}개 파일)")
        self.update_stats()

    def get_file_info(self, file_path, dest_folder, keyword, match_mode):
        """파일 정보 가져오기"""
        file_stat = os.stat(file_path)
        size = self.format_file_size(file_stat.st_size)
        modified = datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M")

        if self.delete_var.get():
            destination = "삭제" if not self.permanent_delete_var.get() else "영구삭제"
        else:
            destination = os.path.basename(dest_folder) if dest_folder else ""

        return {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": size,
            "modified": modified,
            "rule": f"{keyword} ({match_mode})",
            "keyword": keyword,
            "match_mode": match_mode,
            "destination": destination,
            "dest_folder": dest_folder,
        }

    def format_file_size(self, size):
        """파일 크기 포맷팅"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def on_file_click(self, event):
        """파일 트리뷰 클릭 이벤트"""
        region = self.file_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.file_tree.identify_column(event.x)
            if column == "#1":  # 체크박스 열
                item = self.file_tree.identify_row(event.y)
                if item:
                    # 체크 상태 토글
                    current = self.file_vars[item].get()
                    self.file_vars[item].set(not current)
                    check_mark = "✓" if not current else ""
                    values = list(self.file_tree.item(item)["values"])
                    values[0] = check_mark
                    self.file_tree.item(item, values=values)
                    self.update_stats()

    def select_all_files(self):
        """모든 파일 선택"""
        for item in self.file_tree.get_children():
            self.file_vars[item].set(True)
            values = list(self.file_tree.item(item)["values"])
            values[0] = "✓"
            self.file_tree.item(item, values=values)
        self.update_stats()

    def deselect_all_files(self):
        """모든 파일 선택 해제"""
        for item in self.file_tree.get_children():
            self.file_vars[item].set(False)
            values = list(self.file_tree.item(item)["values"])
            values[0] = ""
            self.file_tree.item(item, values=values)
        self.update_stats()

    def update_stats(self):
        """통계 정보 업데이트"""
        total = len(self.file_list_data)
        selected = sum(1 for var in self.file_vars.values() if var.get())

        self.stats_labels["total_files"].config(text=str(total))
        self.stats_labels["selected_files"].config(text=str(selected))

    def preview_files(self):
        """파일 미리보기"""
        self.log_text.delete(1.0, tk.END)
        self.log("=== 미리보기 시작 ===")

        selected_count = sum(1 for var in self.file_vars.values() if var.get())
        if selected_count == 0:
            messagebox.showinfo("정보", "선택된 파일이 없습니다.")
            return

        operation = self.operation_var.get()
        if operation == "delete":
            delete_type = "영구 삭제" if self.permanent_delete_var.get() else "휴지통"
            self.log(f"⚠️ {selected_count}개 파일이 {delete_type}될 예정입니다.")
        else:
            action = "복사" if operation == "copy" else "이동"
            self.log(f"{selected_count}개 파일이 {action}될 예정입니다.")

        # 선택된 파일 목록 표시 (최대 20개)
        shown = 0
        for item_id, var in self.file_vars.items():
            if var.get():
                values = self.file_tree.item(item_id)["values"]
                self.log(f"• {values[1]} → {values[5]}")
                shown += 1
                if shown >= 20:
                    remaining = selected_count - shown
                    if remaining > 0:
                        self.log(f"... 그리고 {remaining}개 더")
                    break

        self.log("=== 미리보기 종료 ===")

    def organize_files(self):
        """파일 정리 시작"""
        # 선택된 파일 확인
        selected_files = []
        for i, (item_id, var) in enumerate(self.file_vars.items()):
            if var.get():
                file_info = self.file_list_data[i]
                selected_files.append(file_info)

        if not selected_files:
            messagebox.showinfo("정보", "선택된 파일이 없습니다.")
            return

        # 확인 대화상자
        operation = self.operation_var.get()
        if operation == "delete":
            if self.permanent_delete_var.get():
                message = f"⚠️ 경고 ⚠️\n\n{len(selected_files)}개 파일을 영구 삭제합니다.\n이 작업은 되돌릴 수 없습니다!\n\n정말 계속하시겠습니까?"
                if not messagebox.askyesno("영구 삭제 확인", message, icon="warning"):
                    return
            else:
                message = f"{len(selected_files)}개 파일을 휴지통으로 이동합니다.\n\n계속하시겠습니까?"
                if not messagebox.askyesno("삭제 확인", message):
                    return
        else:
            action = "복사" if operation == "copy" else "이동"
            message = (
                f"{len(selected_files)}개 파일을 {action}합니다.\n\n계속하시겠습니까?"
            )
            if not messagebox.askyesno("확인", message):
                return

        # 별도 스레드에서 실행
        thread = threading.Thread(
            target=self._organize_files_thread, args=(selected_files,)
        )
        thread.start()

    def _organize_files_thread(self, selected_files):
        """파일 정리 스레드"""
        self.log_text.delete(1.0, tk.END)
        self.log("=== 파일 정리 시작 ===")

        # UI 비활성화
        self.root.after(0, self.disable_ui)

        # 진행률 초기화
        self.update_progress(0, len(selected_files), "준비 중...")

        operation = self.operation_var.get()
        is_delete = operation == "delete"
        is_copy = operation == "copy"
        is_permanent = self.permanent_delete_var.get()

        success_count = 0
        error_count = 0

        # 파일 처리
        for i, file_info in enumerate(selected_files):
            file_path = file_info["path"]
            dest_folder = file_info["dest_folder"]
            keyword = file_info["keyword"]
            match_mode = file_info["match_mode"]

            batch = [(file_path, dest_folder, keyword, match_mode)]

            success, error = self.file_processor.process_batch(
                batch,
                is_delete,
                is_permanent,
                is_copy,
                "삭제" if is_delete else ("복사" if is_copy else "이동"),
            )

            success_count += success
            error_count += error

            # 진행률 업데이트
            self.update_progress(
                i + 1,
                len(selected_files),
                f"처리 중... ({i + 1}/{len(selected_files)})",
            )

            # 통계 업데이트
            self.root.after(
                0, lambda: self.stats_labels["processed_files"].config(text=str(i + 1))
            )
            self.root.after(
                0,
                lambda s=success_count: self.stats_labels["success_count"].config(
                    text=str(s)
                ),
            )
            self.root.after(
                0,
                lambda e=error_count: self.stats_labels["error_count"].config(
                    text=str(e)
                ),
            )

        self.log(f"\n=== 작업 완료 ===")
        self.log(f"성공: {success_count}개 파일")
        self.log(f"실패: {error_count}개 파일")

        # 진행률 완료
        self.update_progress(len(selected_files), len(selected_files), "작업 완료!")

        # UI 활성화
        self.root.after(0, self.enable_ui)

        # 파일 목록 새로고침
        self.root.after(0, self.refresh_file_list)

        # 완료 메시지
        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "완료",
                f"파일 정리가 완료되었습니다.\n\n성공: {success_count}개\n실패: {error_count}개",
            ),
        )

    def disable_ui(self):
        """UI 비활성화"""
        self.preview_button.config(state="disabled")
        self.execute_button.config(state="disabled")
        self.settings_notebook.tab(0, state="disabled")
        self.settings_notebook.tab(1, state="disabled")
        self.settings_notebook.tab(2, state="disabled")

    def enable_ui(self):
        """UI 활성화"""
        self.preview_button.config(state="normal")
        self.execute_button.config(state="normal")
        self.settings_notebook.tab(0, state="normal")
        self.settings_notebook.tab(1, state="normal")
        self.settings_notebook.tab(2, state="normal")

    def log(self, message):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, current, total, message=""):
        """진행률 업데이트"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=message)
        else:
            self.progress_var.set(0)
            self.progress_label.config(text=message)

        self.root.update_idletasks()

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

    def open_log_window(self):
        """별도 창에서 로그 보기"""
        if hasattr(self, "log_window") and self.log_window is not None:
            try:
                if self.log_window.is_alive():
                    self.log_window.lift()
                    return
            except:
                pass

        log_content = self.log_text.get(1.0, tk.END)
        self.log_window = LogWindow(self.root, log_content, self.refresh_log_window)

    def refresh_log_window(self):
        """로그 창 내용 새로고침"""
        if hasattr(self, "log_window") and self.log_window is not None:
            try:
                if self.log_window.is_alive():
                    self.log_window.update_content(self.log_text.get(1.0, tk.END))
            except:
                pass

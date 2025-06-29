#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
메인 윈도우 UI
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
from datetime import datetime

from src.constants import *
from src.core import FileMatcher, FileProcessor, RuleManager
from src.ui.dialogs import LogWindow
from src.utils.logger import Logger
from src.utils.validators import Validator

class MainWindow:
    """메인 윈도우 클래스"""
    
    def __init__(self, root):
        """초기화"""
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # 컴포넌트 초기화
        self.rule_manager = RuleManager(CONFIG_FILE)
        self.file_matcher = FileMatcher()
        self.file_processor = FileProcessor(log_callback=self.log)
        self.logger = Logger(LOG_DIR)
        self.validatory = Validator()
        
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
        
        # 로그 창 변수
        self.log_window = None
        
        # UI 설정
        self.setup_ui()
        
        # 규칙 목록 업데이트
        self.update_rule_list()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 소스 폴더 선택
        self._create_source_folder_selection(main_frame)
        
        # 규칙 추가 영역
        self._create_rule_section(main_frame)
        
        # 규칙 목록 영역
        self._create_rule_list_section(main_frame)
        
        # 옵션 영역
        self._create_options_section(main_frame)
        
        # 실행 버튼
        self._create_action_buttons(main_frame)
        
        # 진행률 표시 영역
        self._create_progress_section(main_frame)
        
        # 로그 영역
        self._create_log_section(main_frame)
        
        # 그리드 가중치 설정
        self._configure_grid_weights(main_frame)
        
    def _create_source_folder_selection(self, parent):
        """소스 폴더 선택 영역 생성"""
        ttk.Label(parent, text="대상 폴더:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(parent, textvariable=self.source_var, width=50).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(
            parent, text="폴더 선택", command=self.select_source_folder
        ).grid(row=0, column=2)
        
    def _create_rule_section(self, parent):
        """규칙 추가 영역 생성"""
        rule_frame = ttk.LabelFrame(parent, text="분류 규칙", padding="10")
        rule_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 첫번째 줄: 키워드랑 매칭 옵션
        ttk.Label(rule_frame, text="키워드:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(rule_frame, textvariable=self.keyword_var, width=20).grid(
            row=0, column=1, padx=5
        )
        
        ttk.Label(rule_frame, text="매칭 옵션:").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 0)
        )
        self.match_mode_combo = ttk.Combobox(
            rule_frame,
            textvariable=self.match_mode_var,
            values=MATCH_MODES,
            width=10,
            state="readonly"
        )
        self.match_mode_combo.grid(row=0, column=3, padx=5)
        
        # 두번째 줄: 대상 폴더
        ttk.Label(rule_frame, text="이동할 폴더:").grid(
            row=1, column=0, sticky=tk.W, pady=(5, 0)
        )
        ttk.Entry(rule_frame, textvariable=self.dest_var, width=40).grid(
            row=1, column=1, columnspan=2, padx=5, pady=(5, 0)
        )
        ttk.Button(rule_frame, text="폴더 선택", command=self.select_dest_folder).grid(
            row=1, column=3, pady=(5, 0)
        )
        
        ttk.Button(rule_frame, text="규칙 추가", command=self.add_rule).grid(
            row=1, column=4, padx=10, pady=(5, 0)
        )
        
    def _create_rule_list_section(self, parent):
        """규칙 목록 영역 생성"""
        list_frame = ttk.Frame(parent)
        list_frame.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10
        )
        
        # 전체 선택/해제 버튼
        
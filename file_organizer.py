#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import json
from datetime import datetime
import threading


class FileOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("파일 자동 분류 프로그램")
        self.root.geometry("800x600")

        # 설정 파일 경로
        self.config_file = "file_organizer_config.json"
        self.rules = self.load_config()

        # UI 설정
        self.setup_ui()

    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 소스 폴더 선택
        ttk.Label(main_frame, text="대상 폴더:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.source_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="폴더 선택", command=self.select_source_folder).grid(row=0, column=2)
        
        # 규칙 추가 섹션
        rule_frame = ttk.LabelFrame(main_frame, text="분류 규칙", padding="10")
        rule_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(rule_frame, text="키워드:").grid(row=0, column=0, sticky=tk.W)
        self.keyword_var = tk.StringVar()
        ttk.Entry(rule_frame, textvariable=self.keyword_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(rule_frame, text="이동할 폴더:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.dest_var = tk.StringVar()
        ttk.Entry(rule_frame, textvariable=self.dest_var, width=30).grid(row=0, column=3, padx=5)
        ttk.Button(rule_frame, text="폴더 선택", command=self.select_dest_folder).grid(row=0, column=4)
        
        ttk.Button(rule_frame, text="규칙 추가", command=self.add_rule).grid(row=0, column=5, padx=10)
        
        # 규칙 목록
        
        

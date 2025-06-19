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
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # 트리뷰(TreeView)로 규칙 표시
        self.tree = ttk.Treeview(list_frame, columns=("키워드", "대상 폴더"), show="tree headings", height=10)
        self.tree = ttk.Treeview(list_frame, columns=('키워드', '대상 폴더'), show='tree headings', height=10)
        
        self.tree.heading('#0', text='번호')
        self.tree.heading('키워드', text='키워드')
        self.tree.heading('대상 폴더', text='대상 폴더')
        
        self.tree.column('#0', width=50)
        self.tree.column('키워드', width=150)
        self.tree.column('대상 폴더', width=400)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 규칙 삭제 버튼
        ttk.Button(main_frame, text="선택한 규칙 삭제", command=self.delete_rule).grid(row=3, column=0, columnspan=3, pady=5)
        
        # 옵션
        option_frame = ttk.LabelFrame(main_frame, text="옵션", padding="10")
        option_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.subfolder_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="하위 폴더 포함", variable=self.subfolder_var).grid(row=0, column=0, sticky=tk.W)
        
        self.copy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(option_frame, text="복사 (체크 안하면 이동)", variable=self.copy_var).grid(row=0, column=1, sticky=tk.W, padx=20)
        
        # 실행 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="파일 정리 시작", command=self.organize_files, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="미리보기", command=self.preview_files).pack(side=tk.LEFT, padx=5)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=70)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # 저장된 규칙 로드
        self.update_rule_list()
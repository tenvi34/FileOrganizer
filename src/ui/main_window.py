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
        ttk.Label(parent, text="대상 폴더:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.source_var, width=50).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(parent, text="폴더 선택", command=self.select_source_folder).grid(
            row=0, column=2
        )

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
            state="readonly",
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
        button_bar = ttk.Frame(list_frame)
        button_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(button_bar, text="전체 선택", command=self.select_all_rules).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_bar, text="전체 해제", command=self.deselect_all_rules).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_bar, text="선택 반전", command=self.toggle_all_rules).pack(
            side=tk.LEFT, padx=2
        )

        # 트리뷰로 규칙 표시
        tree_frame = ttk.Frame(list_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("활성화", "키워드", "매칭", "대상 폴더"),
            show="tree headings",
            height=10,
        )
        self.tree.heading("#0", text="번호")
        self.tree.heading("활성화", text="✓")
        self.tree.heading("키워드", text="키워드")
        self.tree.heading("매칭", text="매칭 옵션")
        self.tree.heading("대상 폴더", text="대상 폴더")

        self.tree.column("#0", width=50)
        self.tree.column("활성화", width=40, anchor="center")
        self.tree.column("키워드", width=150)
        self.tree.column("매칭", width=80)
        self.tree.column("대상 폴더", width=400)

        # 스크롤바
        scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 트리뷰 클릭 이벤트
        self.tree.bind("<Button-1>", self.on_tree_click)

        # 그리드 가중치
        list_frame.rowconfigure(1, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

    def _create_options_section(self, parent):
        """옵션 영역 생성"""
        # 규칙 삭제 버튼
        ttk.Button(parent, text="선택한 규칙 삭제", command=self.delete_rule).grid(
            row=3, column=0, columnspan=3, pady=5
        )

        # 옵션 프레임
        option_frame = ttk.LabelFrame(parent, text="옵션", padding="10")
        option_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Checkbutton(
            option_frame, text="하위 폴더 포함", variable=self.subfolder_var
        ).grid(row=0, column=0, sticky=tk.W)

        # 복사(이동) 옵션
        self.copy_check = ttk.Checkbutton(
            option_frame, text="복사 (체크 안하면 이동)", variable=self.copy_var
        )
        self.copy_check.grid(row=0, column=1, sticky=tk.W, padx=20)

        # 삭제 옵션
        self.delete_check = ttk.Checkbutton(
            option_frame,
            text="삭제 모드",
            variable=self.delete_var,
            command=self.on_delete_mode_change,
        )
        self.delete_check.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        self.permanent_check = ttk.Checkbutton(
            option_frame,
            text="영구 삭제 (복구 불가)",
            variable=self.permanent_delete_var,
        )
        self.permanent_check.grid(row=1, column=1, sticky=tk.W, padx=20, pady=(5, 0))

        # 초기에는 영구 삭제 모드 비활성화
        self.permanent_check.config(state="disabled")

    def _create_action_buttons(self, parent):
        """실행 버튼 생성"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(
            button_frame,
            text="파일 정리 시작",
            command=self.organize_files,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="미리보기", command=self.preview_files).pack(
            side=tk.LEFT, padx=5
        )

    def _create_progress_section(self, parent):
        """진행률 영역 생성"""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)

        self.progress_label = ttk.Label(progress_frame, text="준비 중...")
        self.progress_label.grid(row=0, column=1, padx=5)

        progress_frame.columnconfigure(0, weight=1)

    def _create_log_section(self, parent):
        """로그 영역 생성"""
        log_frame = ttk.LabelFrame(parent, text="로그", padding="5")
        log_frame.grid(
            row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10
        )

        # 로그 버튼 프레임
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5)
        )

        ttk.Button(log_button_frame, text="로그 지우기", command=self.clear_log).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(log_button_frame, text="로그 저장", command=self.save_log).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            log_button_frame, text="별도 창에서 보기", command=self.open_log_window
        ).pack(side=tk.LEFT, padx=2)

        # 로그 텍스트 영역
        self.log_text = tk.Text(log_frame, height=12, width=70, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # 로그 프레임 그리드 가중치
        log_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)

    def _configure_grid_weights(self, parent):
        """그리드 가중치 설정"""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)
        parent.rowconfigure(7, weight=1)

    # 이벤트 핸들러
    def select_source_folder(self):
        """소스 폴더 선택"""
        folder = filedialog.askdirectory(title="대상 폴더 선택")
        if folder:
            self.source_var.set(folder)

    def select_dest_folder(self):
        """대상 폴더 선택"""
        folder = filedialog.askdirectory(title="이동할 폴더 선택")
        if folder:
            self.dest_var.set(folder)

    def add_rule(self):
        """규칙 추가"""
        keyword = self.keyword_var.get().strip()
        dest = self.dest_var.get().strip()
        match_mode = self.match_mode_var.get()

        if not keyword or not dest:
            messagebox.showwarning("경고", "키워드와 대상 폴더를 모두 입력하세요.")
            return

        if self.rule_manager.add_rule(keyword, dest, match_mode):
            self.update_rule_list()
            # 입력 필드 초기화
            self.keyword_var.set("")
            self.dest_var.set("")
            self.match_mode_var.set(DEFAULT_MATCH_MODE)
            self.log(f"규칙 추가: '{keyword}' → '{dest}' (매칭: {match_mode})")

    def delete_rule(self):
        """선택한 규칙 삭제"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 규칙을 선택하세요.")
            return

        item = self.tree.item(selected[0])
        keyword = item["values"][1]

        if messagebox.askyesno("확인", f"'{keyword}' 규칙을 삭제하시겠습니까?"):
            if self.rule_manager.delete_rule(keyword):
                self.update_rule_list()
                self.log(f"규칙 삭제: '{keyword}'")

    def select_all_rules(self):
        """모든 규칙 선택"""
        self.rule_manager.set_all_rules_enabled(True)
        self.update_rule_list()

    def deselect_all_rules(self):
        """모든 규칙 해제"""
        self.rule_manager.set_all_rules_enabled(False)
        self.update_rule_list()

    def toggle_all_rules(self):
        """모든 규칙 선택 반전"""
        self.rule_manager.toggle_all_rules()
        self.update_rule_list()

    def on_tree_click(self, event):
        """트리뷰 클릭 이벤트 처리"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # 활성화 열
                item = self.tree.identify_row(event.y)
                if item:
                    # 체크 상태 토글
                    keyword = self.tree.item(item)["values"][1]
                    self.rule_manager.toggle_rule(keyword)
                    self.update_rule_list()

    def on_delete_mode_change(self):
        """삭제 모드 변경 시 UI 업데이트"""
        if self.delete_var.get():
            # 삭제 모드일 때는 복사 옵션 비활성화
            self.copy_var.set(False)
            self.copy_check.config(state="disabled")
            # 영구 삭제 옵션 활성화
            self.permanent_check.config(state="normal")
        else:
            # 삭제 모드가 아닐 때는 영구 삭제 옵션 비활성화
            self.permanent_delete_var.set(False)
            self.permanent_check.config(state="disabled")
            # 복사 옵션 활성화
            self.copy_check.config(state="normal")

        # TreeView 업데이트하여 대상 폴더 표시 변경
        self.update_rule_list()

    def update_rule_list(self):
        """규칙 목록 업데이트"""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 규칙 추가
        for i, (keyword, rule_data) in enumerate(self.rule_manager.get_rules_list(), 1):
            # 이전 버전 호환성 처리
            if isinstance(rule_data, str):
                # 기존 형식: {"keyword": "dest_path"}
                dest = rule_data
                match_mode = "포함"
                enabled = True
            else:
                # 새로운 형식
                dest = rule_data.get("dest", "")
                match_mode = rule_data.get("match_mode", "포함")
                enabled = rule_data.get("enabled", True)

            check_mark = "✓" if enabled else ""

            # 삭제 모드일 때 대상 폴더 표시 변경
            if self.delete_var.get():
                dest_display = "(삭제 모드 - 폴더 불필요)"
            else:
                dest_display = dest

            self.tree.insert(
                "",
                "end",
                text=str(1),
                values=(check_mark, keyword, match_mode, dest_display),
            )

    def preview_files(self):
        """파일 미리보기"""
        self.log_text.delete(1.0, tk.END)
        self.log("=== 미리보기 시작 ===")

        # 활성화된 규칙 수 확인
        active_rules = self.rule_manager.get_active_rules()
        active_count = len(active_rules)
        total_count = len(self.rule_manager.rules)

        self.log(f"활성 규칙: {active_count}/{total_count}개")

        # 소스 폴더 확인
        source = self.source_var.get()
        if not source or not os.path.exists(source):
            messagebox.showerror("오류", "유효한 대상 폴더를 선택하세요.")
            return

        if not active_rules:
            messagebox.showwarning("경고", "활성화된 분류 규칙이 없습니다.")
            return

        # 진행률 초기화
        self.update_progress(0, 0, "파일 검색 중...")

        # 제너레이터로 파일 수만 빠르게 카운트
        match_count = 0

        for i, (file_path, dest, keyword, match_mode) in enumerate(
            self.file_matcher.find_matching_files_generator(
                source, active_rules, self.subfolder_var.get()
            )
        ):
            match_count += 1

            # 처음 PREVIEW_LIMIT개만 로그에 표시
            if i < PREVIEW_LIMIT:
                file_name = os.path.basename(file_path)
                if self.delete_var.get():
                    delete_type = (
                        "영구 삭제" if self.permanent_delete_var.get() else "휴지통"
                    )
                    self.log(
                        f"매칭: {file_name} → {delete_type} (키워드: {keyword}, 모드: {match_mode})"
                    )
                else:
                    self.log(
                        f"매칭: {file_name} → {dest} (키워드: {keyword}, 모드: {match_mode})"
                    )
            elif i == PREVIEW_LIMIT:
                self.log(
                    f"\n... 그리고 {match_count - PREVIEW_LIMIT}개 더 있습니다 ..."
                )

        if match_count > 0:
            if self.delete_var.get():
                delete_type = (
                    "영구 삭제"
                    if self.permanent_delete_var.get()
                    else "휴지통으로 이동"
                )
                self.log(f"\n⚠️ 총 {match_count}개 파일이 {delete_type}될 예정입니다.")
            else:
                action = "복사" if self.copy_var.get() else "이동"
                self.log(f"\n총 {match_count}개 파일이 {action}될 예정입니다.")

            # 많은 파일이 있을 경우 별도 창 열기 제안
            if match_count > 50:
                if messagebox.askyesno(
                    "많은 파일",
                    f"{match_count}개의 파일이 발견되었습니다.\n별도 창에서 로그를 보시겠습니까?",
                ):
                    self.open_log_window()
        else:
            self.log("\n매칭되는 파일이 없습니다.")

        self.log("=== 미리보기 종료 ===\n")
        self.update_progress(0, 0, "미리보기 완료")

    def organize_files(self):
        """파일 정리 시작"""
        # 환경 검증
        source = self.source_var.get()
        active_rules = self.rule_manager.get_active_rules()

        is_valid, warnings = self.validator.validate_before_operation(
            source, active_rules, self.copy_var.get(), self.delete_var.get()
        )

        if warnings:
            warning_msg = "\n".join(warnings)
            if not is_valid:
                messagebox.showerror("오류", warning_msg)
                return
            else:
                if not messagebox.askyesno(
                    "경고", f"{warning_msg}\n\n계속하시겠습니까?"
                ):
                    return

        # 매칭되는 파일 수 미리 확인
        match_count = sum(
            1
            for _ in self.file_matcher.find_matching_files_generator(
                source, active_rules, self.subfolder_var.get()
            )
        )

        if match_count == 0:
            messagebox.showinfo("정보", "매칭되는 파일이 없습니다.")
            return

        # 확인 대화상자
        if self.delete_var.get():
            if self.permanent_delete_var.get():
                message = f"⚠️ 경고 ⚠️\n\n{match_count}개 파일을 영구 삭제합니다.\n이 작업은 되돌릴 수 없습니다!\n\n정말 계속하시겠습니까?"
                if not messagebox.askyesno("영구 삭제 확인", message, icon="warning"):
                    return
                # 이중 확인
                if not messagebox.askyesno(
                    "최종 확인",
                    f"정말로 {match_count}개 파일을 영구 삭제하시겠습니까?\n\n마지막 확인입니다!",
                    icon="warning",
                ):
                    return
            else:
                message = f"{match_count}개 파일을 휴지통으로 이동합니다.\n\n계속하시겠습니까?"
                if not messagebox.askyesno("삭제 확인", message):
                    return
        else:
            operation = "복사" if self.copy_var.get() else "이동"
            message = f"{match_count}개 파일을 {operation}합니다.\n\n계속하시겠습니까?"
            if not messagebox.askyesno("확인", message):
                return

        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._organize_files_thread)
        thread.start()

    def _organize_files_thread(self):
        """파일 정리 스레드"""
        self.log_text.delete(1.0, tk.END)
        self.log("=== 파일 정리 시작 ===")

        # 진행률 초기화
        self.update_progress(0, 0, "파일 검색 중...")

        source = self.source_var.get()
        active_rules = self.rule_manager.get_active_rules()
        is_copy = self.copy_var.get()
        is_delete = self.delete_var.get()
        is_permanent = self.permanent_delete_var.get()

        if is_delete:
            operation = "영구 삭제" if is_permanent else "삭제"
        else:
            operation = "복사" if is_copy else "이동"

        success_count = 0
        error_count = 0
        processed_count = 0

        # 배치 처리 설정
        batch = []

        # UI 업데이트 주기 설정
        last_update_time = time.time()

        # 제너레이터로 파일 처리
        file_generator = self.file_matcher.find_matching_files_generator(
            source, active_rules, self.subfolder_var.get()
        )

        # 전체 파일 수를 미리 계산 (프로그레스바용)
        total_files = sum(
            1
            for _ in self.file_matcher.find_matching_files_generator(
                source, active_rules, self.subfolder_var.get()
            )
        )

        if total_files == 0:
            self.log("매칭되는 파일이 없습니다.")
            self.update_progress(0, 0, "완료 - 매칭 파일 없음")
            return

        self.log(f"총 {total_files}개 파일을 처리합니다.")

        # 다시 제너레이터 생성
        file_generator = self.file_matcher.find_matching_files_generator(
            source, active_rules, self.subfolder_var.get()
        )

        for file_path, dest_folder, keyword, match_mode in file_generator:
            batch.append((file_path, dest_folder, keyword, match_mode))

            # 배치가 가득 차거나 마지막 파일인 경우 처리
            if len(batch) >= BATCH_SIZE:
                success, error = self.file_processor.process_batch(
                    batch, is_delete, is_permanent, is_copy, operation
                )
                success_count += success
                error_count += error
                processed_count += len(batch)

                # UI 업데이트 (주기적으로)
                current_time = time.time()
                if current_time - last_update_time >= UI_UPDATE_INTERVAL:
                    self.update_progress(processed_count, total_files, f"처리 중...")
                    last_update_time = current_time

                batch = []

        # 남은 파일 처리
        if batch:
            success, error = self.file_processor.process_batch(
                batch, is_delete, is_permanent, is_copy, operation
            )
            success_count += success
            error_count += error
            processed_count += len(batch)

        self.log(f"\n=== 작업 완료 ===")
        self.log(f"성공: {success_count}개 파일")
        self.log(f"실패: {error_count}개 파일")

        # 실패한 파일이 있으면 로그 자동 저장
        if error_count > 0:
            log_path = self.logger.save_error_log(self.log_text.get(1.0, tk.END))
            if log_path:
                self.log(f"\n오류 로그가 저장되었습니다: {log_path}")

        # 진행률 완료
        if error_count > 0:
            self.update_progress(
                total_files, total_files, f"작업 완료! (실패: {error_count}개)"
            )
        else:
            self.update_progress(total_files, total_files, "작업 완료!")

        # 메인 스레드에서 메시지박스 표시
        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "완료",
                f"파일 정리가 완료되었습니다.\n\n성공: {success_count}개\n실패: {error_count}개",
            ),
        )

    def log(self, message):
        """로그 메시지 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, current, total, message=""):
        """진행률 업데이트"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.progress_label.config(
                text=f"{current}/{total} ({progress:.1f}%) {message}"
            )
        else:
            self.progress_var.set(0)
            self.progress_label.config(text=message)

        # update_idletasks()는 update()보다 가벼움
        self.root.update_idletasks()

    def clear_log(self):
        """로그 내용 지우기"""
        self.log_text.delete(1.0, tk.END)
        self.log("로그를 지웠습니다.")

    def save_log(self):
        """로그를 파일로 저장"""
        log_content = self.log_text.get(1.0, tk.END)
        saved_path = self.logger.save_log_with_dialog(log_content)
        if saved_path:
            messagebox.showinfo("저장 완료", f"로그가 저장되었습니다:\n{saved_path}")

    def open_log_window(self):
        """별도 창에서 로그 보기"""
        if self.log_window is not None and self.log_window.is_alive():
            self.log_window.lift()
            return

        log_content = self.log_text.get(1.0, tk.END)
        self.log_window = LogWindow(self.root, log_content, self.refresh_log_window)

    def refresh_log_window(self):
        """로그 창 내용 새로고침"""
        if self.log_window and self.log_window.is_alive():
            self.log_window.update_content(self.log_text.get(1.0, tk.END))

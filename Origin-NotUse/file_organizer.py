#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
from datetime import datetime
import threading
import re
import send2trash


class FileOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("파일 자동 분류 프로그램")
        self.root.geometry("1000x850")

        # 설정 파일 경로
        self.config_file = "config/file_organizer_config.json"
        self.rules = self.load_config()

        # 로그 창 변수
        self.log_window = None

        # 체크박스 상태 저장
        self.check_vars = {}

        # UI 설정
        self.setup_ui()

        # 로그 폴더 생성
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 소스 폴더 선택
        ttk.Label(main_frame, text="대상 폴더:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.source_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.source_var, width=50).grid(
            row=0, column=1, padx=5
        )
        ttk.Button(
            main_frame, text="폴더 선택", command=self.select_source_folder
        ).grid(row=0, column=2)

        # 규칙 추가 섹션
        rule_frame = ttk.LabelFrame(main_frame, text="분류 규칙", padding="10")
        rule_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 첫 번째 줄: 키워드와 매칭 옵션
        ttk.Label(rule_frame, text="키워드:").grid(row=0, column=0, sticky=tk.W)
        self.keyword_var = tk.StringVar()
        ttk.Entry(rule_frame, textvariable=self.keyword_var, width=20).grid(
            row=0, column=1, padx=5
        )

        ttk.Label(rule_frame, text="매칭 옵션:").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 0)
        )
        self.match_mode_var = tk.StringVar(value="포함")
        match_modes = ["포함", "정확히", "시작", "끝", "정규식"]
        self.match_mode_combo = ttk.Combobox(
            rule_frame,
            textvariable=self.match_mode_var,
            values=match_modes,
            width=10,
            state="readonly",
        )
        self.match_mode_combo.grid(row=0, column=3, padx=5)

        # 두 번째 줄: 대상 폴더
        ttk.Label(rule_frame, text="이동할 폴더:").grid(
            row=1, column=0, sticky=tk.W, pady=(5, 0)
        )
        self.dest_var = tk.StringVar()
        ttk.Entry(rule_frame, textvariable=self.dest_var, width=40).grid(
            row=1, column=1, columnspan=2, padx=5, pady=(5, 0)
        )
        ttk.Button(rule_frame, text="폴더 선택", command=self.select_dest_folder).grid(
            row=1, column=3, pady=(5, 0)
        )

        ttk.Button(rule_frame, text="규칙 추가", command=self.add_rule).grid(
            row=1, column=4, padx=10, pady=(5, 0)
        )

        # 규칙 목록
        list_frame = ttk.Frame(main_frame)
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

        # 규칙 삭제 버튼
        ttk.Button(main_frame, text="선택한 규칙 삭제", command=self.delete_rule).grid(
            row=3, column=0, columnspan=3, pady=5
        )

        # 옵션
        option_frame = ttk.LabelFrame(main_frame, text="옵션", padding="10")
        option_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.subfolder_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            option_frame, text="하위 폴더 포함", variable=self.subfolder_var
        ).grid(row=0, column=0, sticky=tk.W)

        # 복사(이동) 옵션
        self.copy_var = tk.BooleanVar(value=False)
        self.copy_check = ttk.Checkbutton(
            option_frame, text="복사 (체크 안하면 이동)", variable=self.copy_var
        )
        self.copy_check.grid(row=0, column=1, sticky=tk.W, padx=20)

        # 삭제 옵션
        self.delete_var = tk.BooleanVar(value=False)
        self.delete_check = ttk.Checkbutton(
            option_frame,
            text="삭제 모드",
            variable=self.delete_var,
            command=self.on_delete_mode_change,
        )
        self.delete_check.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        self.permanent_delete_var = tk.BooleanVar(value=False)
        self.permanent_check = ttk.Checkbutton(
            option_frame,
            text="영구 삭제 (복구 불가)",
            variable=self.permanent_delete_var,
        )
        self.permanent_check.grid(row=1, column=1, sticky=tk.W, padx=20, pady=(5, 0))

        # 실행 버튼
        button_frame = ttk.Frame(main_frame)
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

        # 진행률 표시
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)

        self.progress_label = ttk.Label(progress_frame, text="준비 중...")
        self.progress_label.grid(row=0, column=1, padx=5)

        progress_frame.columnconfigure(0, weight=1)

        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="5")
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

        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(7, weight=1)

        # 저장된 규칙 로드
        self.update_rule_list()

        # 초기에는 영구 삭제 모드 비활성화
        self.permanent_check.config(state="disabled")

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
                    if keyword in self.rules:
                        current = self.rules[keyword].get("enabled", True)
                        self.rules[keyword]["enabled"] = not current
                        self.save_config()
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

    def select_all_rules(self):
        """모든 규칙 선택"""
        for keyword in self.rules:
            self.rules[keyword]["enabled"] = True
        self.save_config()
        self.update_rule_list()

    def deselect_all_rules(self):
        """모든 규칙 해제"""
        for keyword in self.rules:
            self.rules[keyword]["enabled"] = False
        self.save_config()
        self.update_rule_list()

    def toggle_all_rules(self):
        """모든 규칙 선택 반전"""
        for keyword in self.rules:
            current = self.rules[keyword].get("enabled", True)
            self.rules[keyword]["enabled"] = not current
        self.save_config()
        self.update_rule_list()

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="대상 폴더 선택")
        if folder:
            self.source_var.set(folder)

    def select_dest_folder(self):
        folder = filedialog.askdirectory(title="이동할 폴더 선택")
        if folder:
            self.dest_var.set(folder)

    def add_rule(self):
        keyword = self.keyword_var.get().strip()
        dest = self.dest_var.get().strip()
        match_mode = self.match_mode_var.get()

        if not keyword or not dest:
            messagebox.showwarning("경고", "키워드와 대상 폴더를 모두 입력하세요.")
            return

        # 규칙 추가 (새로운 형식)
        self.rules[keyword] = {"dest": dest, "match_mode": match_mode, "enabled": True}
        self.save_config()
        self.update_rule_list()

        # 입력 필드 초기화
        self.keyword_var.set("")
        self.dest_var.set("")
        self.match_mode_var.set("포함")

        self.log(f"규칙 추가: '{keyword}' → '{dest}' (매칭: {match_mode})")

    def delete_rule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 규칙을 선택하세요.")
            return

        item = self.tree.item(selected[0])
        keyword = item["values"][1]

        if messagebox.askyesno("확인", f"'{keyword}' 규칙을 삭제하시겠습니까?"):
            del self.rules[keyword]
            self.save_config()
            self.update_rule_list()
            self.log(f"규칙 삭제: '{keyword}'")

    def update_rule_list(self):
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 규칙 추가
        for i, (keyword, rule_data) in enumerate(self.rules.items(), 1):
            # 이전 버전 호환성 처리
            if isinstance(rule_data, str):
                # 기존 형식: {"keyword": "dest_path"}
                dest = rule_data
                match_mode = "포함"
                enabled = True
            else:
                # 새로운 형식: {"keyword": {"dest": "path", "match_mode": "포함", "enabled": true}}
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
                text=str(i),
                values=(check_mark, keyword, match_mode, dest_display),
            )

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 데이터 형식 업그레이드
                    upgraded_data = {}
                    for key, value in data.items():
                        if isinstance(value, str):
                            # 기존 형식을 새 형식으로 변환
                            upgraded_data[key] = {
                                "dest": value,
                                "match_mode": "포함",
                                "enabled": True,
                            }
                        else:
                            upgraded_data[key] = value
                    return upgraded_data
            except Exception as e:
                self.log(f"설정 파일 로드 중 오류: {str(e)}")
        return {}

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def update_progress(self, current, total, message=""):
        """최적화된 진행률 업데이트 - 과도한 UI 업데이트 방지 -2025.06.23-"""
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

    def match_file(self, filename, keyword, match_mode):
        """파일명과 키워드 매칭"""
        # 파일명만 추출 (경로 제외)
        base_filename = os.path.basename(filename)

        if match_mode == "포함":
            return keyword.lower() in base_filename.lower()
        elif match_mode == "정확히":
            name_without_ext, _ = os.path.splitext(base_filename)
            return keyword.lower() == name_without_ext.lower()
        elif match_mode == "시작":
            return base_filename.lower().startswith(keyword.lower())
        elif match_mode == "끝":
            name_without_ext, _ = os.path.splitext(base_filename)
            return name_without_ext.lower().endswith(keyword.lower())
        elif match_mode == "정규식":
            try:
                return bool(re.search(keyword, base_filename, re.IGNORECASE))
            except re.error:
                self.log(f"잘못된 정규식: {keyword}")
                return False
        return False

    def find_matching_files_generator(self, preview=False):
        """파일을 제너레이터로 반환하여 메모리 효율 개선"""
        source = self.source_var.get()
        if not source or not os.path.exists(source):
            return

        # 활성화된 규칙만 필터링
        active_rules = {
            k: v
            for k, v in self.rules.items()
            if (isinstance(v, dict) and v.get("enabled", True))
        }

        if not active_rules:
            return

        include_subfolders = self.subfolder_var.get()

        # 파일 검색
        if include_subfolders:
            for root, dirs, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    for keyword, rule_data in active_rules.items():
                        dest = rule_data.get("dest", "")
                        match_mode = rule_data.get("match_mode", "포함")
                        if self.match_file(file_path, keyword, match_mode):
                            yield (file_path, dest, keyword, match_mode)
                            break
        else:
            for file in os.listdir(source):
                file_path = os.path.join(source, file)
                if os.path.isfile(file_path):
                    # 심볼릭 링크 제외
                    if os.path.islink(file_path):
                        continue

                    # 시스템/숨김 파일 확인 (Windows)
                    if os.name == "nt":
                        import ctypes

                        FILE_ATTRIBUTE_HIDDEN = 0x02
                        FILE_ATTRIBUTE_SYSTEM = 0x04
                        try:
                            attrs = ctypes.windll.kernel32.GetFileAttributesW(file_path)
                            if attrs & (FILE_ATTRIBUTE_SYSTEM | FILE_ATTRIBUTE_HIDDEN):
                                continue
                        except:  # noqa: E722
                            pass

                    for keyword, rule_data in active_rules.items():
                        dest = rule_data.get("dest", "")
                        match_mode = rule_data.get("match_mode", "포함")
                        if self.match_file(file_path, keyword, match_mode):
                            yield (file_path, dest, keyword, match_mode)
                            break

    def preview_files(self):
        """최적화된 미리보기 -2025.06.23-"""
        self.log_text.delete(1.0, tk.END)
        self.log("=== 미리보기 시작 ===")

        # 활성화된 규칙 수 확인
        active_count = sum(
            1
            for r in self.rules.values()
            if isinstance(r, dict) and r.get("enabled", True)
        )
        total_count = len(self.rules)

        self.log(f"활성 규칙: {active_count}/{total_count}개")

        # 진행률 초기화
        self.update_progress(0, 0, "파일 검색 중...")

        # 제너레이터로 파일 수만 빠르게 카운트
        match_count = 0
        preview_limit = 100  # 미리보기는 처음 100개만 표시

        for i, (file_path, dest, keyword, match_mode) in enumerate(
            self.find_matching_files_generator()
        ):
            match_count += 1

            # 처음 100개만 로그에 표시
            if i < preview_limit:
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
            elif i == preview_limit:
                self.log(
                    f"\n... 그리고 {match_count - preview_limit}개 더 있습니다 ..."
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
        # 환경 검증
        is_valid, warnings = self.validate_before_operation()
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
        matches = self.find_matching_files()
        if not matches:
            messagebox.showinfo("정보", "매칭되는 파일이 없습니다.")
            return

        count = len(matches)

        if self.delete_var.get():
            if self.permanent_delete_var.get():
                message = f"⚠️ 경고 ⚠️\n\n{count}개 파일을 영구 삭제합니다.\n이 작업은 되돌릴 수 없습니다!\n\n정말 계속하시겠습니까?"
                if not messagebox.askyesno("영구 삭제 확인", message, icon="warning"):
                    return
                # 이중 확인
                if not messagebox.askyesno(
                    "최종 확인",
                    f"정말로 {count}개 파일을 영구 삭제하시겠습니까?\n\n마지막 확인입니다!",
                    icon="warning",
                ):
                    return
            else:
                message = (
                    f"{count}개 파일을 휴지통으로 이동합니다.\n\n계속하시겠습니까?"
                )
                if not messagebox.askyesno("삭제 확인", message):
                    return
        else:
            operation = "복사" if self.copy_var.get() else "이동"
            message = f"{count}개 파일을 {operation}합니다.\n\n계속하시겠습니까?"
            if not messagebox.askyesno("확인", message):
                return

        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._organize_files_thread)
        thread.start()

    def _organize_files_thread(self):
        """최적화된 파일 정리 스레드(처리 속도 향상) -2025.06.23-"""
        self.log_text.delete(1.0, tk.END)
        self.log("=== 파일 정리 시작 ===")

        # 진행률 초기화
        self.update_progress(0, 0, "파일 검색 중...")

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

        # batch 처리 설정
        BATCH_SIZE = 100
        batch = []

        # UI 업데이트 주기 설정 (0.1초마다)
        last_update_time = time.time()
        UPDATE_INTERVAL = 0.1

        # 제너레이터로 파일 처리
        file_generator = self.find_matching_files_generator()

        # 전체 파일 수를 미리 계산 (Progress Bar)
        total_files = sum(1 for _ in self.find_matching_files_generator())
        if total_files == 0:
            self.log("매칭되는 파일이 없습니다.")
            self.update_progress(0, 0, "완료 - 매칭 파일 없음")
            return

        self.log(f"총 {total_files}개 파일을 처리합니다.")

        # 다시 제너레이터 생성
        file_generator = self.find_matching_files_generator()

        for file_path, dest_folder, keyword, match_mode in file_generator:
            batch.append((file_path, dest_folder, keyword, match_mode))

            # batch가 가득 차거나 마지막 파일인 경우에 처리
            if len(batch) >= BATCH_SIZE:
                success, error = self._process_batch(
                    batch, is_delete, is_permanent, is_copy, operation
                )
                success_count += success
                error_count += error
                processed_count += len(batch)

                # UI 업데이트(주기적으로)
                current_time = time.time()
                if current_time - last_update_time >= UPDATE_INTERVAL:
                    self.update_progress(processed_count, total_files, "처리 중...")
                    last_update_time = current_time

                batch = []

        # 남은 파일 처리
        if batch:
            success, error = self._process_batch(
                batch, is_delete, is_permanent, is_copy, operation
            )
            success_count += success
            error_count += error
            processed_count += len(batch)

        self.log("\n=== 작업 완료 ===")
        self.log(f"성공: {success_count}개 파일")
        self.log(f"실패: {error_count}개 파일")

        # 실패한 파일이 있으면 로그 자동 저장
        if error_count > 0:
            error_log_path = os.path.join(
                self.log_dir,
                f"file_organizer_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            )
            try:
                with open(error_log_path, "w", encoding="utf-8") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"\n오류 로그가 저장되었습니다: {error_log_path}")
            except:  # noqa: E722
                pass

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

    def _process_batch(self, batch, is_delete, is_permanent, is_copy, operation):
        """batch 단위로 파일 처리"""
        success_count = 0
        error_count = 0

        for file_path, dest_folder, keyword, match_mode in batch:
            try:
                file_name = os.path.basename(file_path)

                if is_delete:
                    # 삭제 모드
                    if not os.path.exists(file_path):
                        self.log(f"❌ 파일이 존재하지 않음: {file_name}")
                        error_count += 1
                        continue

                    if is_permanent:
                        # 영구 삭제
                        try:
                            os.remove(file_path)
                            self.log(f"{operation} 완료: {file_name} (규칙: {keyword})")
                            success_count += 1
                        except Exception as e:
                            # Windows 긴 경로 문제일 수 있으므로 다시 시도
                            try:
                                import subprocess

                                subprocess.run(
                                    ["cmd", "/c", "del", "/f", "/q", file_path],
                                    check=True,
                                    capture_output=True,
                                    text=True,
                                )
                                self.log(
                                    f"{operation} 완료: {file_name} (규칙: {keyword})"
                                )
                                success_count += 1
                            except:  # noqa: E722
                                self.log(f"❌ {operation} 실패: {file_name} - {str(e)}")
                                error_count += 1
                    else:
                        # 휴지통으로 이동
                        try:
                            normalized_path = os.path.normpath(file_path)
                            send2trash.send2trash(normalized_path)
                            self.log(f"{operation} 완료: {file_name} (규칙: {keyword})")
                            success_count += 1
                        except Exception as e:
                            self.log(
                                f"❌ {operation} 실패: {file_name} - {type(e).__name__}: {str(e)}"
                            )
                            error_count += 1
                else:
                    # 복사/이동 모드
                    # 대상 폴더가 없으면 생성
                    if not os.path.exists(dest_folder):
                        os.makedirs(dest_folder)
                        self.log(f"폴더 생성: {dest_folder}")

                    # 파일명 추출
                    dest_path = os.path.join(dest_folder, file_name)

                    # 동일한 파일명이 있을 경우 처리
                    if os.path.exists(dest_path):
                        base_name, ext = os.path.splitext(file_name)
                        counter = 1
                        while os.path.exists(dest_path):
                            new_name = f"{base_name}_{counter}{ext}"
                            dest_path = os.path.join(dest_folder, new_name)
                            counter += 1

                    # 파일 복사 또는 이동
                    if is_copy:
                        shutil.copy2(file_path, dest_path)
                    else:
                        shutil.move(file_path, dest_path)

                    self.log(
                        f"{operation} 완료: {file_name} → {dest_folder} (규칙: {keyword}/{match_mode})"
                    )
                    success_count += 1

            except Exception as e:
                self.log(f"오류 발생: {os.path.basename(file_path)} - {str(e)}")
                error_count += 1

        return success_count, error_count

    def safe_path(self, path):
        """안전한 경로 변환"""
        if os.name == "nt":
            # Windows에서만 처리
            path = path.replace("/", "\\")
            abs_path = os.path.abspath(path)
            # 이미 \\?\ 로 시작하면 그대로 반환
            if abs_path.startswith("\\\\?\\"):
                return abs_path
            # 긴 경로인 경우에만 \\?\ 추가
            if len(abs_path) > 260:
                return "\\\\?\\" + abs_path
        return path

    def clear_log(self):
        """로그 내용 지우기"""
        self.log_text.delete(1.0, tk.END)
        self.log("로그를 지웠습니다.")

    def save_log(self):
        """로그를 파일로 저장"""
        # 로그 폴더에 저장하도록 기본 경로 설정
        default_filename = os.path.join(
            self.log_dir,
            f"file_organizer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialdir=self.log_dir,  # 기본 폴더를 로그 폴더로
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
            initialfile=os.path.basename(default_filename),
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("저장 완료", f"로그가 저장되었습니다:\n{filename}")
            except Exception as e:
                messagebox.showerror("오류", f"로그 저장 중 오류 발생:\n{str(e)}")

    def open_log_window(self):
        """별도 창에서 로그 보기"""
        if self.log_window is not None and self.log_window.winfo_exists():
            self.log_window.lift()
            return

        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("로그 뷰어")
        self.log_window.geometry("800x600")

        # 프레임
        frame = ttk.Frame(self.log_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 버튼
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(button_frame, text="새로고침", command=self.refresh_log_window).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="모두 복사", command=self.copy_all_log).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(button_frame, text="저장", command=self.save_log).pack(
            side=tk.LEFT, padx=2
        )

        # 텍스트 위젯
        self.log_window_text = tk.Text(frame, wrap=tk.WORD, height=30)
        scrollbar = ttk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self.log_window_text.yview
        )
        self.log_window_text.configure(yscrollcommand=scrollbar.set)

        self.log_window_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # 현재 로그 내용 복사
        self.log_window_text.insert(1.0, self.log_text.get(1.0, tk.END))

        # 그리드 가중치
        self.log_window.columnconfigure(0, weight=1)
        self.log_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

    def refresh_log_window(self):
        """로그 창 내용 새로고침"""
        if hasattr(self, "log_window_text"):
            self.log_window_text.delete(1.0, tk.END)
            self.log_window_text.insert(1.0, self.log_text.get(1.0, tk.END))
            self.log_window_text.see(tk.END)

    def copy_all_log(self):
        """전체 로그를 클립보드에 복사"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get(1.0, tk.END))
        messagebox.showinfo("복사 완료", "로그가 클립보드에 복사되었습니다.")

    def validate_before_operation(self):
        """작업 전 환경 검증"""
        source = self.source_var.get()
        warnings = []

        # 1. 소스 폴더 검증
        if not source or not os.path.exists(source):
            return False, ["대상 폴더가 존재하지 않습니다."]

        # 2. 쓰기 권한 검증 (이동/삭제 모드)
        if not self.copy_var.get():
            try:
                test_file = os.path.join(source, ".write_test_temp")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
            except:  # noqa: E722
                warnings.append(
                    "⚠️ 대상 폴더에 쓰기 권한이 없습니다. 관리자 권한으로 실행하세요."
                )

        # 3. 대상 폴더를 검증 (삭제모드가 아닐 경우)
        if not self.delete_var.get():
            for keyword, rule_data in self.rules.items():
                if isinstance(rule_data, dict) and rule_data.get("enabled", True):
                    dest = rule_data.get("dest", "")
                    if dest and not os.path.exists(dest):
                        try:
                            os.makedirs(dest)
                        except Exception as e:
                            warnings.append(f"⚠️ 폴더 생성 실패: {dest} - {str(e)}")

        # 4. 디스크 공간 확인 (복사모드)
        if self.copy_var.get():
            try:
                import shutil

                total_size = sum(
                    os.path.getsize(f[0]) for f in self.find_matching_files()
                )
                free_space = shutil.disk_usage(source).free
                if total_size > free_space * 0.9:  # 90% 이상 사용 시 경고
                    warnings.append(
                        f"⚠️ 디스크 공간 부족 가능성 (필요: {total_size//1024//1024}MB)"
                    )
            except:  # noqa: E722
                pass

        return len(warnings) == 0, warnings


def main():
    root = tk.Tk()
    FileOrganizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

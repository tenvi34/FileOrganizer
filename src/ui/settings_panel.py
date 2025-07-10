#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
설정 패널 UI
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.constants import DEFAULT_MATCH_MODE, MATCH_MODES


class SettingsPanel:
    """설정 패널 클래스"""

    def __init__(self, parent, rule_manager, callbacks):
        """초기화

        Args:
            parent: 부모 위젯
            rule_manager: 규칙 관리자
            callbacks: 콜백 함수 딕셔너리
        """
        self.parent = parent
        self.rule_manager = rule_manager
        self.callbacks = callbacks

        # UI 변수
        self.source_var = tk.StringVar()
        self.keyword_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.match_mode_var = tk.StringVar(value=DEFAULT_MATCH_MODE)
        self.subfolder_var = tk.BooleanVar(value=True)
        self.operation_var = tk.StringVar(value="move")
        self.copy_var = tk.BooleanVar(value=False)
        self.delete_var = tk.BooleanVar(value=False)
        self.permanent_delete_var = tk.BooleanVar(value=False)

        # 프레임 생성
        self.create_panel()

    def create_panel(self):
        """패널 생성"""
        # 설정 패널 프레임
        self.frame = ttk.Frame(self.parent, style="Panel.TFrame", width=400)
        self.frame.pack_propagate(False)

        # 헤더
        header = ttk.Label(self.frame, text="⚙️ 설정", style="Header.TLabel")
        header.pack(pady=5)

        # 탭 위젯
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 탭 생성
        self.create_basic_settings_tab()  # 기본 설정 탭
        self.create_rules_tab()  # 규칙 관리 탭
        self.create_options_tab()  # 작업 옵션 탭

    def create_basic_settings_tab(self):
        """기본 설정 탭"""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="기본 설정")

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

    def create_rules_tab(self):
        """규칙 관리 탭"""
        rules_frame = ttk.Frame(self.notebook)
        self.notebook.add(rules_frame, text="규칙 관리")

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
        self.rule_tree.bind("<Delete>", lambda e: self.delete_rule())

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

    def create_options_tab(self):
        """작업 옵션 탭"""
        options_frame = ttk.Frame(self.notebook)
        self.notebook.add(options_frame, text="작업 옵션")

        # 작업 유형 선택
        operation_frame = ttk.LabelFrame(options_frame, text="작업 유형", padding=10)
        operation_frame.pack(fill=tk.X, padx=10, pady=10)

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

        # 설정 관리 프레임 추가
        config_frame = ttk.LabelFrame(options_frame, text="설정 관리", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        config_button_frame = ttk.Frame(config_frame)
        config_button_frame.pack(fill=tk.X)

        ttk.Button(
            config_button_frame, text="설정 내보내기", command=self.export_config
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            config_button_frame, text="설정 불러오기", command=self.import_config
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            config_button_frame, text="설정 초기화", command=self.reset_config
        ).pack(side=tk.LEFT, padx=5)

        # 작업 버튼
        action_frame = ttk.Frame(options_frame)
        action_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.preview_button = ttk.Button(
            action_frame,
            text="미리보기",
            command=self.callbacks.get("preview"),
            style="TButton",
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.execute_button = ttk.Button(
            action_frame,
            text="작업 실행",
            command=self.callbacks.get("execute"),
            style="Accent.TButton",
        )
        self.execute_button.pack(side=tk.LEFT, padx=5)

    # 이벤트 핸들러
    def select_source_folder(self):
        """소스 폴더 선택"""
        folder = filedialog.askdirectory(title="대상 폴더 선택")
        if folder:
            self.source_var.set(folder)
            self.add_to_recent_folders(folder)
            if self.callbacks.get("refresh_files"):
                self.callbacks["refresh_files"]()

    def select_dest_folder(self):
        """대상 폴더 선택"""
        folder = filedialog.askdirectory(title="이동할 폴더 선택")
        if folder:
            self.dest_var.set(folder)

    def add_to_recent_folders(self, folder):
        """최근 폴더에 추가"""
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
            if self.callbacks.get("refresh_files"):
                self.callbacks["refresh_files"]()

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

            if self.callbacks.get("log"):
                self.callbacks["log"](
                    f"규칙 추가: '{keyword}' → '{dest}' (매칭: {match_mode})"
                )
            if self.callbacks.get("refresh_files"):
                self.callbacks["refresh_files"]()

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
                if self.callbacks.get("log"):
                    self.callbacks["log"](f"규칙 삭제: '{keyword}'")
                if self.callbacks.get("refresh_files"):
                    self.callbacks["refresh_files"]()

    def select_all_rules(self):
        """모든 규칙 선택"""
        self.rule_manager.set_all_rules_enabled(True)
        self.update_rule_list()
        if self.callbacks.get("refresh_files"):
            self.callbacks["refresh_files"]()

    def deselect_all_rules(self):
        """모든 규칙 해제"""
        self.rule_manager.set_all_rules_enabled(False)
        self.update_rule_list()
        if self.callbacks.get("refresh_files"):
            self.callbacks["refresh_files"]()

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
                    if self.callbacks.get("refresh_files"):
                        self.callbacks["refresh_files"]()

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

    def export_config(self):
        """설정 내보내기"""
        from tkinter import filedialog
        import json
        from datetime import datetime

        # 기본 파일명 생성
        default_filename = (
            f"file_organizer_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")],
            initialfile=default_filename,
            title="설정 내보내기",
        )

        if filename:
            try:
                # 현재 설정을 저장
                export_data = {
                    "version": "2.0",
                    "export_date": datetime.now().isoformat(),
                    "rules": self.rule_manager.rules,
                    "settings": {
                        "include_subfolders": self.subfolder_var.get(),
                        "default_operation": self.operation_var.get(),
                        "recent_folders": list(self.recent_listbox.get(0, tk.END)),
                    },
                }

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

                messagebox.showinfo("성공", f"설정을 내보냈습니다:\n{filename}")
                if self.callbacks.get("log"):
                    self.callbacks["log"](f"설정 내보내기 완료: {filename}")

            except Exception as e:
                messagebox.showerror("오류", f"설정 내보내기 실패:\n{str(e)}")

    def import_config(self):
        """설정 불러오기"""
        from tkinter import filedialog
        import json

        filename = filedialog.askopenfilename(
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")],
            title="설정 불러오기",
        )

        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    import_data = json.load(f)

                # 버전 확인
                version = import_data.get("version", "1.0")
                if version not in ["1.0", "2.0"]:
                    messagebox.showwarning(
                        "경고", f"지원하지 않는 설정 파일 버전입니다: {version}"
                    )
                    return

                # 확인 대화상자
                rule_count = len(import_data.get("rules", {}))
                if not messagebox.askyesno(
                    "확인",
                    f"설정을 불러오시겠습니까?\n\n"
                    f"규칙 수: {rule_count}개\n"
                    f"내보낸 날짜: {import_data.get('export_date', '알 수 없음')}\n\n"
                    f"기존 설정은 모두 대체됩니다.",
                ):
                    return

                # 규칙 불러오기
                if "rules" in import_data:
                    self.rule_manager.rules = import_data["rules"]
                    self.rule_manager.save_rules()
                    self.update_rule_list()

                # 설정 불러오기
                if "settings" in import_data:
                    settings = import_data["settings"]

                    # 하위 폴더 포함 옵션
                    if "include_subfolders" in settings:
                        self.subfolder_var.set(settings["include_subfolders"])

                    # 기본 작업 모드
                    if "default_operation" in settings:
                        self.operation_var.set(settings["default_operation"])
                        self.on_operation_change()

                    # 최근 폴더 목록
                    if "recent_folders" in settings:
                        self.recent_listbox.delete(0, tk.END)
                        for folder in settings["recent_folders"]:
                            if os.path.exists(folder):  # 존재하는 폴더만 추가
                                self.recent_listbox.insert(tk.END, folder)

                messagebox.showinfo("성공", "설정을 불러왔습니다.")
                if self.callbacks.get("log"):
                    self.callbacks["log"](f"설정 불러오기 완료: {filename}")

                # 파일 목록 새로고침
                if self.callbacks.get("refresh_files"):
                    self.callbacks["refresh_files"]()

            except json.JSONDecodeError:
                messagebox.showerror("오류", "올바른 JSON 파일이 아닙니다.")
            except Exception as e:
                messagebox.showerror("오류", f"설정 불러오기 실패:\n{str(e)}")

    def reset_config(self):
        """설정 초기화"""
        if messagebox.askyesno(
            "확인",
            "모든 규칙과 설정을 초기화하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.",
        ):
            # 규칙 초기화
            self.rule_manager.rules.clear()
            self.rule_manager.save_rules()
            self.update_rule_list()

            # 설정 초기화
            self.subfolder_var.set(True)
            self.operation_var.set("move")
            self.on_operation_change()

            # 최근 폴더 목록 초기화
            self.recent_listbox.delete(0, tk.END)

            # 입력 필드 초기화
            self.source_var.set("")
            self.keyword_var.set("")
            self.dest_var.set("")
            self.match_mode_var.set(DEFAULT_MATCH_MODE)

            messagebox.showinfo("완료", "설정이 초기화되었습니다.")
            if self.callbacks.get("log"):
                self.callbacks["log"]("설정 초기화 완료")

            # 파일 목록 새로고침
            if self.callbacks.get("refresh_files"):
                self.callbacks["refresh_files"]()

    def get_widget(self):
        """위젯 반환"""
        return self.frame

    def enable(self):
        """패널 활성화"""
        self.notebook.tab(0, state="normal")
        self.notebook.tab(1, state="normal")
        self.notebook.tab(2, state="normal")
        self.preview_button.config(state="normal")
        self.execute_button.config(state="normal")

    def disable(self):
        """패널 비활성화"""
        self.notebook.tab(0, state="disabled")
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.preview_button.config(state="disabled")
        self.execute_button.config(state="disabled")

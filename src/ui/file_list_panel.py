#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 목록 패널 UI
"""

import os
import tkinter as tk
import threading
from tkinter import ttk
from datetime import datetime, timedelta

# from src.utils.icon_manager import IconManager
from src.utils.performance import FileInfoCache, ProgressTracker
from src.ui.progress_dialog import ProgressDialog


class FileListPanel:
    """파일 목록 패널 클래스"""

    def __init__(self, parent, file_matcher, callbacks):
        """초기화

        Args:
            parent: 부모 위젯
            file_matcher: 파일 매처
            callbacks: 콜백 함수 딕셔너리
        """
        self.parent = parent
        self.file_matcher = file_matcher
        self.callbacks = callbacks

        # 파일 목록 관련 변수
        self.file_list_data = []  # 매칭된 파일 정보
        self.file_vars = {}  # 체크박스 변수들

        # 아이콘 매니저 초기화
        # self.icon_manager = IconManager()

        # 성능 개선
        self.file_cache = FileInfoCache()
        self.scan_thread = None
        self.is_scanning = False

        # 필터 변수
        self.filter_var = tk.StringVar()
        self.ext_filter_var = tk.StringVar(value="모든 파일")
        self.size_filter_var = tk.StringVar(value="모든 크기")
        self.date_filter_var = tk.StringVar(value="모든 날짜")
        self.rule_filter_var = tk.StringVar(value="모든 규칙")

        # 프레임 생성
        self.create_panel()

    def create_panel(self):
        """패널 생성"""
        # 파일 목록 프레임
        self.frame = ttk.Frame(self.parent, style="Panel.TFrame", width=600)
        self.frame.pack_propagate(False)

        # 헤더
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(header_frame, text="📁 파일 목록", style="Header.TLabel").pack(
            side=tk.LEFT
        )

        self.file_count_label = ttk.Label(header_frame, text="(0개 파일)")
        self.file_count_label.pack(side=tk.LEFT, padx=10)

        # 필터링 프레임 추가
        self.create_filter_frame()

        # 도구 모음
        self.create_toolbar()

        # 파일 트리뷰
        self.create_file_tree()

    def create_filter_frame(self):
        """필터 프레임 생성"""
        filter_frame = ttk.LabelFrame(self.frame, text="필터", padding=5)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        # 1. 텍스트 필터
        text_filter_frame = ttk.Frame(filter_frame)
        text_filter_frame.pack(fill=tk.X, pady=2)

        ttk.Label(text_filter_frame, text="파일명 검색:").pack(side=tk.LEFT, padx=2)

        self.filter_var.trace_add("write", lambda *args: self.apply_filters())
        filter_entry = ttk.Entry(
            text_filter_frame, textvariable=self.filter_var, width=25
        )
        filter_entry.pack(side=tk.LEFT, padx=2)

        # 검색 지우기 버튼
        ttk.Button(
            text_filter_frame,
            text="x",
            width=3,
            command=lambda: self.filter_var.set(""),
        ).pack(side=tk.LEFT)

        # 2. 확장자 필터
        ext_filter_frame = ttk.Frame(filter_frame)
        ext_filter_frame.pack(fill=tk.X, pady=2)

        ttk.Label(ext_filter_frame, text="확장자:").pack(side=tk.LEFT, padx=2)

        self.ext_filter = ttk.Combobox(
            ext_filter_frame,
            textvariable=self.ext_filter_var,
            values=["모든 파일"],
            state="readonly",
            width=15,
        )
        self.ext_filter.pack(side=tk.LEFT, padx=2)
        self.ext_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # 3. 크기 필터
        ttk.Label(ext_filter_frame, text="크기:").pack(side=tk.LEFT, padx=(10, 2))

        size_filter = ttk.Combobox(
            ext_filter_frame,
            textvariable=self.size_filter_var,
            values=["모든 크기", "< 1MB", "1-10MB", "10-100MB", "> 100MB"],
            state="readonly",
            width=12,
        )
        size_filter.pack(side=tk.LEFT, padx=2)
        size_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # 4. 날짜 필터
        date_filter_frame = ttk.Frame(filter_frame)
        date_filter_frame.pack(fill=tk.X, pady=2)

        ttk.Label(date_filter_frame, text="수정일:").pack(side=tk.LEFT, padx=2)

        date_filter = ttk.Combobox(
            date_filter_frame,
            textvariable=self.date_filter_var,
            values=["모든 날짜", "오늘", "이번 주", "이번 달", "올해"],
            state="readonly",
            width=12,
        )
        date_filter.pack(side=tk.LEFT, padx=2)
        date_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # 5. 규칙 필터
        ttk.Label(date_filter_frame, text="규칙:").pack(side=tk.LEFT, padx=(10, 2))

        self.rule_filter = ttk.Combobox(
            date_filter_frame,
            textvariable=self.rule_filter_var,
            values=["모든 규칙"],
            state="readonly",
            width=15,
        )
        self.rule_filter.pack(side=tk.LEFT, padx=2)
        self.rule_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # 필터 상태 표시
        self.filter_status_label = ttk.Label(filter_frame, text="", foreground="blue")
        self.filter_status_label.pack(fill=tk.X, pady=2)

        # 필터 초기화 버튼
        ttk.Button(filter_frame, text="필터 초기화", command=self.reset_filters).pack(
            pady=2
        )

    def create_toolbar(self):
        """도구 모음 생성"""
        toolbar_frame = ttk.Frame(self.frame)
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

    def create_file_tree(self):
        """파일 트리뷰 생성"""
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_tree = ttk.Treeview(
            tree_frame,
            columns=("check", "filename", "size", "modified", "rule", "destination"),
            show="tree headings",
        )

        self.file_tree.heading("#0", text="")  # 아이콘 열 추가
        self.file_tree.heading("check", text="✓")
        self.file_tree.heading("filename", text="파일명")
        self.file_tree.heading("size", text="크기")
        self.file_tree.heading("modified", text="수정일")
        self.file_tree.heading("rule", text="매칭 규칙")
        self.file_tree.heading("destination", text="대상")

        self.file_tree.column("#0", width=0, stretch=False)  # 아이콘용
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

    # def refresh_file_list(self):
    #     """파일 목록 새로고침"""
    #     # 기존 목록 초기화
    #     for item in self.file_tree.get_children():
    #         self.file_tree.delete(item)

    #     self.file_list_data.clear()
    #     self.file_vars.clear()

    #     # 콜백을 통해 설정 가져오기
    #     source = self.callbacks.get("get_source", lambda: None)()
    #     if not source or not os.path.exists(source):
    #         self.file_count_label.config(text="(0개 파일)")
    #         self.callbacks.get("update_stats", lambda: None)()
    #         return

    #     active_rules = self.callbacks.get("get_active_rules", lambda: {})()
    #     if not active_rules:
    #         self.file_count_label.config(text="(0개 파일)")
    #         self.callbacks.get("update_stats", lambda: None)()
    #         return

    #     include_subfolders = self.callbacks.get("get_subfolder_option", lambda: True)()

    #     # 매칭되는 파일 찾기
    #     count = 0
    #     for (
    #         file_path,
    #         dest_folder,
    #         keyword,
    #         match_mode,
    #     ) in self.file_matcher.find_matching_files_generator(
    #         source, active_rules, include_subfolders
    #     ):
    #         file_info = self.get_file_info(file_path, dest_folder, keyword, match_mode)
    #         self.file_list_data.append(file_info)

    #         # 트리에 추가
    #         item_id = self.file_tree.insert(
    #             "",
    #             "end",
    #             # image=self.icon_manager.get_icon(file_info["filename"]),  # 아이콘 추가
    #             values=(
    #                 "✓",  # 기본적으로 체크
    #                 file_info["filename"],
    #                 file_info["size"],
    #                 file_info["modified"],
    #                 file_info["rule"],
    #                 file_info["destination"],
    #             ),
    #         )

    #         # 체크박스 상태 저장
    #         self.file_vars[item_id] = tk.BooleanVar(value=True)
    #         count += 1

    #     # 파일 목록을 모두 로드한 후
    #     self.file_count_label.config(text=f"({count}개 파일)")
    #     self.callbacks.get("update_stats", lambda: None)()

    #     # 확장자와 규칙 필터 옵션 업데이트
    #     self.update_extension_filter_options()

    def refresh_file_list(self):
        """파일 목록 새로고침 - 성능 개선 버전"""
        # 이미 스캔 중이면 중지
        if self.is_scanning and self.scan_thread and self.scan_thread.is_alive():
            return

        # 기존 목록 초기화
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        self.file_list_data.clear()
        self.file_vars.clear()
        self.file_cache.clear()

        # 설정 가져오기
        source = self.callbacks.get("get_source", lambda: None)()
        if not source or not os.path.exists(source):
            self.file_count_label.config(text="(0개 파일)")
            self.callbacks.get("update_stats", lambda: None)()
            return

        active_rules = self.callbacks.get("get_active_rules", lambda: {})()
        if not active_rules:
            self.file_count_label.config(text="(0개 파일)")
            self.callbacks.get("update_stats", lambda: None)()
            return

        # 진행률 다이얼로그 표시
        self.progress_dialog = ProgressDialog(
            self.frame.winfo_toplevel(), title="파일 검색 중", can_cancel=True
        )
        self.progress_dialog.set_indeterminate("파일을 검색하는 중...")

        # 백그라운드 스레드에서 스캔
        self.is_scanning = True
        self.scan_thread = threading.Thread(
            target=self._scan_files_thread, args=(source, active_rules), daemon=True
        )
        self.scan_thread.start()

    def _scan_files_thread(self, source, active_rules):
        """백그라운드에서 파일 스캔"""
        try:
            include_subfolders = self.callbacks.get(
                "get_subfolder_option", lambda: True
            )()

            # 먼저 전체 파일 수 계산 (빠른 추정)
            total_estimate = self._estimate_file_count(source, include_subfolders)

            # 진행률 트래커 설정
            tracker = ProgressTracker(
                total=total_estimate,
                callback=lambda cur, tot, pct, msg: self.frame.after(
                    0, self._update_scan_progress, cur, tot, msg
                ),
            )

            batch = []
            batch_size = 100

            for (
                file_path,
                dest_folder,
                keyword,
                match_mode,
            ) in self.file_matcher.find_matching_files_generator(
                source, active_rules, include_subfolders
            ):

                # 취소 확인
                if self.progress_dialog.cancelled:
                    break

                # 캐시된 정보 사용
                file_info = self._get_file_info_cached(
                    file_path, dest_folder, keyword, match_mode
                )
                batch.append(file_info)

                # 배치 처리
                if len(batch) >= batch_size:
                    self.frame.after(0, self._add_files_batch, batch.copy())
                    batch.clear()
                    tracker.update(
                        batch_size, f"{len(self.file_list_data)}개 파일 발견"
                    )

            # 남은 파일 처리
            if batch:
                self.frame.after(0, self._add_files_batch, batch)

            # 완료
            self.frame.after(0, self._scan_complete)

        except Exception as e:
            print(f"파일 스캔 오류: {e}")
            self.frame.after(0, self._scan_error, str(e))
        finally:
            self.is_scanning = False

    def _estimate_file_count(self, source, include_subfolders):
        """파일 수 추정 (빠른 계산)"""
        count = 0
        try:
            if include_subfolders:
                for root, dirs, files in os.walk(source):
                    count += len(files)
                    # 너무 깊으면 추정치 사용
                    if count > 1000:
                        # 현재까지의 비율로 추정
                        return count * 2
            else:
                count = len(
                    [
                        f
                        for f in os.listdir(source)
                        if os.path.isfile(os.path.join(source, f))
                    ]
                )
        except:
            return 100  # 기본값

        return max(count, 100)

    def _get_file_info_cached(self, file_path, dest_folder, keyword, match_mode):
        """캐시를 사용한 파일 정보 가져오기"""
        # 캐시 확인
        cached_info = self.file_cache.get(file_path)

        if cached_info:
            file_stat_info = cached_info
        else:
            # 새로 가져오기
            try:
                file_stat = os.stat(file_path)
                file_stat_info = {
                    "size": file_stat.st_size,
                    "modified": file_stat.st_mtime,
                }
                self.file_cache.set(file_path, file_stat_info)
            except:
                file_stat_info = {"size": 0, "modified": 0}

        # 파일 정보 생성
        size = self.format_file_size(file_stat_info["size"])
        modified = datetime.fromtimestamp(file_stat_info["modified"]).strftime(
            "%Y-%m-%d %H:%M"
        )

        is_delete = self.callbacks.get("is_delete_mode", lambda: False)()
        is_permanent = self.callbacks.get("is_permanent_delete", lambda: False)()

        if is_delete:
            destination = "삭제" if not is_permanent else "영구삭제"
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

    def _add_files_batch(self, files):
        """파일 배치 추가"""
        for file_info in files:
            self.file_list_data.append(file_info)

            # 트리에 추가
            item_id = self.file_tree.insert(
                "",
                "end",
                values=(
                    "✓",
                    file_info["filename"],
                    file_info["size"],
                    file_info["modified"],
                    file_info["rule"],
                    file_info["destination"],
                ),
            )
            
            self.file_vars[item_id] = tk.BooleanVar(value=True)
        
        # 카운트 업데이트
        self.file_count_label.config(text=f"({len(self.file_list_data)}개 파일)")
        self.callbacks.get('update_stats', lambda: None)()

    def _update_scan_progress(self, current, total, message):
        """스캔 진행률 업데이트"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.update_progress(
                current, total, 
                "파일을 검색하는 중...", 
                message
            )

    def _scan_complete(self):
        """스캔 완료"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # 필터 옵션 업데이트
        self.update_extension_filter_options()
        
        # 최종 통계 업데이트
        self.callbacks.get('update_stats', lambda: None)()

    def _scan_error(self, error_msg):
        """스캔 오류"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        from tkinter import messagebox
        messagebox.showerror("오류", f"파일 검색 중 오류 발생:\n{error_msg}")

    def get_file_info(self, file_path, dest_folder, keyword, match_mode):
        """파일 정보 가져오기"""
        file_stat = os.stat(file_path)
        size = self.format_file_size(file_stat.st_size)
        modified = datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M")

        is_delete = self.callbacks.get("is_delete_mode", lambda: False)()
        is_permanent = self.callbacks.get("is_permanent_delete", lambda: False)()

        if is_delete:
            destination = "삭제" if not is_permanent else "영구삭제"
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
                    self.callbacks.get("update_stats", lambda: None)()

    def select_all_files(self):
        """모든 파일 선택"""
        for item in self.file_tree.get_children():
            self.file_vars[item].set(True)
            values = list(self.file_tree.item(item)["values"])
            values[0] = "✓"
            self.file_tree.item(item, values=values)
        self.callbacks.get("update_stats", lambda: None)()

    def deselect_all_files(self):
        """모든 파일 선택 해제"""
        for item in self.file_tree.get_children():
            self.file_vars[item].set(False)
            values = list(self.file_tree.item(item)["values"])
            values[0] = ""
            self.file_tree.item(item, values=values)
        self.callbacks.get("update_stats", lambda: None)()

    def apply_filters(self):
        """모든 필터 적용"""
        # 필터 값 가져오기
        text_filter = self.filter_var.get().lower()
        ext_filter = self.ext_filter_var.get()
        size_filter = self.size_filter_var.get()
        date_filter = self.date_filter_var.get()
        rule_filter = self.rule_filter_var.get()

        # 먼저 모든 아이템을 삭제
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        # 필터링된 아이템만 다시 추가
        visible_count = 0
        self.file_vars.clear()

        for i, file_info in enumerate(self.file_list_data):
            # 각 필터 조건 확인
            show = True

            # 1. 텍스트 필터
            if text_filter and text_filter not in file_info["filename"].lower():
                show = False

            # 2. 확장자 필터
            if show and ext_filter != "모든 파일":
                _, ext = os.path.splitext(file_info["filename"])
                if ext.lower() != ext_filter.lower():
                    show = False

            # 3. 크기 필터
            if show and size_filter != "모든 크기":
                size = self.get_file_size_in_bytes(file_info["path"])
                if not self.check_size_filter(size, size_filter):
                    show = False

            # 4. 날짜 필터
            if show and date_filter != "모든 날짜":
                if not self.check_date_filter(file_info["path"], date_filter):
                    show = False

            # 5. 규칙 필터
            if show and rule_filter != "모든 규칙":
                if file_info["keyword"] != rule_filter:
                    show = False

            # 필터 조건에 맞는 아이템만 트리에 추가
            if show:
                item_id = self.file_tree.insert(
                    "",
                    "end",
                    # image=self.icon_manager.get_icon(file_info["filename"]),  # 아이콘 추가
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
                visible_count += 1

        # 필터 상태 업데이트
        total_count = len(self.file_list_data)
        self.update_filter_status(visible_count, total_count)

        # 확장자 필터 옵션 업데이트
        self.update_extension_filter_options()

    def update_extension_filter_options(self):
        """확장자 필터 옵션 업데이트"""
        # 현재 파일들의 확장자 수집
        extensions = set()
        for file_info in self.file_list_data:
            _, ext = os.path.splitext(file_info["filename"])
            if ext:
                extensions.add(ext.lower())

        # 확장자 필터 콤보박스 업데이트
        ext_list = ["모든 파일"] + sorted(list(extensions))
        self.ext_filter["values"] = ext_list

        # 규칙 필터 옵션도 업데이트
        rules = set()
        for file_info in self.file_list_data:
            rules.add(file_info["keyword"])

        rule_list = ["모든 규칙"] + sorted(list(rules))
        self.rule_filter["values"] = rule_list

    def get_file_size_in_bytes(self, file_path):
        """파일 크기를 바이트로 반환"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0

    def check_size_filter(self, size_bytes, filter_value):
        """크기 필터 조건 확인"""
        mb = size_bytes / (1024 * 1024)

        if filter_value == "< 1MB":
            return mb < 1
        elif filter_value == "1-10MB":
            return 1 <= mb <= 10
        elif filter_value == "10-100MB":
            return 10 <= mb <= 100
        elif filter_value == "> 100MB":
            return mb > 100
        return True

    def check_date_filter(self, file_path, filter_value):
        """날짜 필터 조건 확인"""
        try:
            file_time = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(file_time)
            now = datetime.now()

            if filter_value == "오늘":
                return file_date.date() == now.date()
            elif filter_value == "이번 주":
                week_start = now - timedelta(days=now.weekday())
                return file_date >= week_start
            elif filter_value == "이번 달":
                return file_date.year == now.year and file_date.month == now.month
            elif filter_value == "올해":
                return file_date.year == now.year
        except:
            pass
        return True

    def update_filter_status(self, visible_count, total_count):
        """필터 상태 표시 업데이트"""
        if visible_count < total_count:
            status = f"필터링됨: {visible_count}/{total_count}개 표시"
            self.filter_status_label.config(text=status, foreground="blue")
        else:
            self.filter_status_label.config(text="", foreground="black")

        # 파일 개수 라벨도 업데이트
        self.file_count_label.config(text=f"({visible_count}개 파일)")

    def reset_filters(self):
        """모든 필터 초기화"""
        self.filter_var.set("")
        self.ext_filter_var.set("모든 파일")
        self.size_filter_var.set("모든 크기")
        self.date_filter_var.set("모든 날짜")
        self.rule_filter_var.set("모든 규칙")

        # 필터 다시 적용
        self.apply_filters()

    def get_filtered_files(self):
        """필터링된 파일만 반환"""
        filtered_files = []

        for i, item in enumerate(self.file_tree.get_children()):
            # hidden 태그가 없는 파일들만
            if "hidden" not in self.file_tree.item(item)["tags"]:
                if self.file_vars[item].get():  # 체크된 항목만
                    filtered_files.append(self.file_list_data[i])

        return filtered_files

    def get_selected_count(self):
        """선택된 파일 개수 반환"""
        return sum(1 for var in self.file_vars.values() if var.get())

    def get_total_count(self):
        """전체 파일 개수 반환"""
        return len(self.file_list_data)

    def get_widget(self):
        """위젯 반환"""
        return self.frame

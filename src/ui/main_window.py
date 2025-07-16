#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
메인 윈도우 UI - 리팩토링 버전
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import time

from src.constants import *
from src.core import FileMatcher, FileProcessor, RuleManager
from src.ui.dialogs import LogWindow
from src.ui.settings_panel import SettingsPanel
from src.ui.file_list_panel import FileListPanel
from src.ui.status_panel import StatusPanel
from src.ui.menubar import MenuBar
from src.ui.shortcuts import ShortcutManager
from src.utils.logger import Logger
from src.utils.validators import Validator


class MainWindow:
    """메인 윈도우 클래스 - 리팩토링 버전"""

    def __init__(self, root):
        """초기화"""
        self.root = root

        # 플랫폼 감지
        self.is_macos = sys.platform == "darwin"
        self.is_windows = sys.platform == "win32"

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

        # 로그 창 변수
        self.log_window = None

        # UI 설정
        self.setup_ui()

        # 초기 업데이트
        self.settings_panel.update_rule_list()

    def setup_styles(self):
        """스타일 설정 - 흰색/파랑 테마"""
        style = ttk.Style()

        # 테마 설정
        if sys.platform == "darwin":
            style.theme_use("aqua")  # macOS 네이티브 테마
        else:
            style.theme_use("clam")

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
            font=("Helvetica" if sys.platform == "darwin" else "Segoe UI", 12, "bold"),
            background=panel_bg,
            foreground=primary_blue,
        )

        # 일반 라벨 스타일
        style.configure("TLabel", background=panel_bg, foreground=text_primary)

        # 버튼 스타일 - macOS 특별 처리
        if self.is_macos:
            # macOS aqua 테마에서 버튼 글자색만 검은색으로
            style.configure("TButton", foreground="black", font=("Helvetica", 9))

            # 액센트 버튼도 글자색 설정
            style.configure(
                "Accent.TButton", foreground="black", font=("Helvetica", 10, "bold")
            )
        else:
            # Windows/Linux
            style.configure(
                "TButton",
                background=primary_blue,
                foreground="white",
                borderwidth=0,
                focuscolor="none",
                font=("Segoe UI", 10, "bold"),
                padding=(15, 8),
            )

            style.map(
                "TButton",
                background=[("active", hover_blue), ("pressed", hover_blue)],
                foreground=[("active", "white")],
            )

            # 액센트 버튼 (실행 버튼용)
            style.configure(
                "Accent.TButton",
                background="#28A745",
                foreground="white",
                font=("Segoe UI", 10, "bold"),
                padding=(15, 8),
            )

            style.map("Accent.TButton", background=[("active", "#218838")])

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

        # 콜백 함수 정의
        callbacks = {
            # 설정 패널 콜백
            "refresh_files": self.refresh_file_list,
            "log": self.log,
            "preview": self.preview_files,
            "execute": self.organize_files,
            # 파일 목록 패널 콜백
            "get_source": lambda: self.settings_panel.source_var.get(),
            "get_active_rules": lambda: self.rule_manager.get_active_rules(),
            "get_subfolder_option": lambda: self.settings_panel.subfolder_var.get(),
            "is_delete_mode": lambda: self.settings_panel.delete_var.get(),
            "is_permanent_delete": lambda: self.settings_panel.permanent_delete_var.get(),
            "update_stats": self.update_stats,
            # 상태 패널 콜백
            "open_log_window": self.open_log_window,
            # 메뉴바/단축키 콜백
            "select_all_files": lambda: self.file_list_panel.select_all_files(),
            "deselect_all_files": lambda: self.file_list_panel.deselect_all_files(),
            "clear_log": lambda: self.status_panel.clear_log(),
            "save_log": lambda: self.status_panel.save_log(),
            "show_about": self.show_about,
            # 설정 관리 콜백
            "export_config": lambda: self.settings_panel.export_config(),
            "import_config": lambda: self.settings_panel.import_config(),
        }

        # 1. 설정 패널 (왼쪽)
        self.settings_panel = SettingsPanel(
            self.paned_window, self.rule_manager, callbacks
        )
        self.paned_window.add(self.settings_panel.get_widget(), weight=1)

        # 2. 파일 목록 패널 (중앙)
        self.file_list_panel = FileListPanel(
            self.paned_window, self.file_matcher, callbacks
        )
        self.paned_window.add(self.file_list_panel.get_widget(), weight=2)

        # 3. 상태 패널 (오른쪽)
        self.status_panel = StatusPanel(self.paned_window, self.logger, callbacks)
        self.paned_window.add(self.status_panel.get_widget(), weight=1)

        # 메뉴바 설정
        self.menubar = MenuBar(self.root, callbacks)

        # 단축키 설정
        self.shortcuts = ShortcutManager(self.root, callbacks)

    def refresh_file_list(self):
        """파일 목록 새로고침"""
        self.file_list_panel.refresh_file_list()

    def update_stats(self):
        """통계 정보 업데이트"""
        total = self.file_list_panel.get_total_count()
        selected = self.file_list_panel.get_selected_count()

        self.status_panel.update_stat("total_files", total)
        self.status_panel.update_stat("selected_files", selected)

    def log(self, message):
        """로그 메시지 출력"""
        self.status_panel.log(message)
        self.root.update_idletasks()

    def preview_files(self):
        """파일 미리보기"""
        self.status_panel.clear_log()
        self.log("=== 미리보기 시작 ===")

        selected_files = self.file_list_panel.get_filtered_files()
        selected_count = len(selected_files)

        if selected_count == 0:
            messagebox.showinfo("정보", "선택된 파일이 없습니다.")
            return

        operation = self.settings_panel.operation_var.get()
        if operation == "delete":
            delete_type = (
                "영구 삭제"
                if self.settings_panel.permanent_delete_var.get()
                else "휴지통"
            )
            self.log(f"⚠️ {selected_count}개 파일이 {delete_type}될 예정입니다.")
        else:
            action = "복사" if operation == "copy" else "이동"
            self.log(f"{selected_count}개 파일이 {action}될 예정입니다.")

        # 선택된 파일 목록 표시 (최대 20개)
        shown = 0
        for file_info in selected_files[:20]:
            self.log(f"• {file_info['filename']} → {file_info['destination']}")
            shown += 1

        remaining = selected_count - shown
        if remaining > 0:
            self.log(f"... 그리고 {remaining}개 더")

        self.log("=== 미리보기 종료 ===")

    def organize_files(self):
        """파일 정리 시작"""
        # 선택된 파일 확인
        selected_files = self.file_list_panel.get_filtered_files()

        if not selected_files:
            messagebox.showinfo("정보", "선택된 파일이 없습니다.")
            return

        # 확인 대화상자
        operation = self.settings_panel.operation_var.get()
        if operation == "delete":
            if self.settings_panel.permanent_delete_var.get():
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
        """파일 정리 스레드 - 성능 개선 버전"""
        self.status_panel.clear_log()
        self.log("=== 파일 정리 시작 ===")

        # UI 비활성화
        self.root.after(0, self.disable_ui)

        # 진행률 다이얼로그 표시
        self.root.after(0, self._show_progress_dialog, len(selected_files))

        # 진행률 초기화
        self.status_panel.reset_progress()
        self.status_panel.reset_stats()

        operation = self.settings_panel.operation_var.get()
        is_delete = operation == "delete"
        is_copy = operation == "copy"
        is_permanent = self.settings_panel.permanent_delete_var.get()

        success_count = 0
        error_count = 0

        # 통계 초기화
        import time

        stats = {
            "total_size": 0,
            "processed_size": 0,
            "start_time": time.time(),
            "file_times": [],
        }

        # 전체 크기 계산
        for file_info in selected_files:
            try:
                stats["total_size"] += os.path.getsize(file_info["path"])
            except:
                pass

        # 배치 처리를 위한 설정
        batch_size = 10
        batch = []

        # 파일 처리
        for i, file_info in enumerate(selected_files):
            # 취소 확인
            if (
                hasattr(self, "operation_progress")
                and self.operation_progress.cancelled
            ):
                self.log("작업이 취소되었습니다.")
                break

            file_path = file_info["path"]
            dest_folder = file_info["dest_folder"]
            keyword = file_info["keyword"]
            match_mode = file_info["match_mode"]

            # 파일 크기 추가
            try:
                file_size = os.path.getsize(file_path)
                stats["processed_size"] += file_size
            except:
                pass

            batch.append((file_path, dest_folder, keyword, match_mode))

            # 배치 처리
            if len(batch) >= batch_size or i == len(selected_files) - 1:
                success, error = self.file_processor.process_batch(
                    batch,
                    is_delete,
                    is_permanent,
                    is_copy,
                    "삭제" if is_delete else ("복사" if is_copy else "이동"),
                )

                success_count += success
                error_count += error
                batch.clear()

            # 진행률 업데이트 (UI 스레드에서)
            self.root.after(
                0,
                self._update_operation_progress,
                i + 1,
                len(selected_files),
                f"처리 중... ({i + 1}/{len(selected_files)})",
                os.path.basename(file_path),
            )

            # 통계 업데이트
            self.root.after(
                0, lambda: self.status_panel.update_stat("processed_files", i + 1)
            )
            self.root.after(
                0,
                lambda s=success_count: self.status_panel.update_stat(
                    "success_count", s
                ),
            )
            self.root.after(
                0, lambda e=error_count: self.status_panel.update_stat("error_count", e)
            )

        # 처리 시간 계산
        elapsed_time = time.time() - stats["start_time"]

        self.log(f"\n=== 작업 완료 ===")
        self.log(f"성공: {success_count}개 파일")
        self.log(f"실패: {error_count}개 파일")

        # 상세 통계 (stats가 있는 경우)
        if stats["processed_size"] > 0:
            self.log(f"\n=== 상세 통계 ===")
            self.log(f"전체 처리 시간: {self.format_time(elapsed_time)}")
            self.log(f"처리된 데이터: {self.format_file_size(stats['processed_size'])}")
            avg_speed = (
                stats["processed_size"] / elapsed_time if elapsed_time > 0 else 0
            )
            self.log(f"평균 속도: {self.format_file_size(avg_speed)}/초")

        # 진행률 다이얼로그 닫기
        self.root.after(0, self._close_progress_dialog)

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

    def _show_progress_dialog(self, total_files):
        """진행률 다이얼로그 표시"""
        from src.ui.progress_dialog import ProgressDialog

        self.operation_progress = ProgressDialog(
            self.root, title="파일 정리 중", can_cancel=True
        )
        self.operation_progress.update_progress(
            0, total_files, "작업을 시작하는 중...", ""
        )

    def _update_operation_progress(self, current, total, message, detail):
        """작업 진행률 업데이트"""
        if hasattr(self, "operation_progress") and self.operation_progress:
            self.operation_progress.update_progress(current, total, message, detail)

    def _close_progress_dialog(self):
        """진행률 다이얼로그 닫기"""
        if hasattr(self, "operation_progress") and self.operation_progress:
            self.operation_progress.close()
            self.operation_progress = None

    def format_file_size(self, size):
        """파일 크기 포맷팅"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def format_time(self, seconds):
        """시간 포맷팅"""
        if seconds < 60:
            return f"{seconds:.1f}초"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}분"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}시간"

    def disable_ui(self):
        """UI 비활성화"""
        self.settings_panel.disable()

    def enable_ui(self):
        """UI 활성화"""
        self.settings_panel.enable()

    def open_log_window(self):
        """별도 창에서 로그 보기"""
        if hasattr(self, "log_window") and self.log_window is not None:
            try:
                if self.log_window.is_alive():
                    self.log_window.lift()
                    return
            except:
                pass

        log_content = self.status_panel.get_log_content()
        self.log_window = LogWindow(self.root, log_content, self.refresh_log_window)

    def refresh_log_window(self):
        """로그 창 내용 새로고침"""
        if hasattr(self, "log_window") and self.log_window is not None:
            try:
                if self.log_window.is_alive():
                    self.log_window.update_content(self.status_panel.get_log_content())
            except:
                pass

    def show_about(self):
        """프로그램 정보 표시"""
        about_text = f"""
{APP_TITLE}
버전: {APP_VERSION}

파일을 자동으로 분류하는 프로그램입니다.
키워드 기반으로 파일을 원하는 폴더로 이동/복사/삭제할 수 있습니다.

Copyright © 2025
        """
        messagebox.showinfo("프로그램 정보", about_text.strip())

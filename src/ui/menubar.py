#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
메뉴바 관리
"""

import tkinter as tk
import sys


class MenuBar:
    """메뉴바 클래스"""

    def __init__(self, root, callbacks):
        """초기화

        Args:
            root: 루트 윈도우
            callbacks: 콜백 함수 딕셔너리
        """
        self.root = root
        self.callbacks = callbacks

        # 플랫폼 감지
        self.is_macos = sys.platform == "darwin"

        # 메뉴바 생성
        self.create_menubar()

    def create_menubar(self):
        """메뉴바 생성"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # 파일 메뉴
        self.create_file_menu()

        # 편집 메뉴
        self.create_edit_menu()

        # 도구 메뉴
        self.create_tools_menu()

        # 도움말 메뉴
        self.create_help_menu()

    def create_file_menu(self):
        """파일 메뉴 생성"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="파일", menu=file_menu)

        modifier = "⌘" if self.is_macos else "Ctrl+"

        file_menu.add_command(
            label=f"새로고침 ({modifier}R)",
            command=self.callbacks.get("refresh_files"),
            accelerator=f"{modifier}R",
        )
        file_menu.add_separator()

        file_menu.add_command(
            label=f"로그 저장 ({modifier}S)",
            command=self.callbacks.get("save_log"),
            accelerator=f"{modifier}S",
        )
        file_menu.add_separator()

        # 설정 관리 메뉴 추가
        file_menu.add_command(
            label="설정 내보내기...", command=self.callbacks.get("export_config")
        )
        file_menu.add_command(
            label="설정 불러오기...", command=self.callbacks.get("import_config")
        )
        file_menu.add_separator()

        file_menu.add_command(
            label=f"로그 저장 ({modifier}S)",
            command=self.callbacks.get("save_log"),
            accelerator=f"{modifier}S",
        )
        file_menu.add_separator()

        file_menu.add_command(label="종료", command=self.root.quit)

    def create_edit_menu(self):
        """편집 메뉴 생성"""
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="편집", menu=edit_menu)

        modifier = "⌘" if self.is_macos else "Ctrl+"

        edit_menu.add_command(
            label=f"전체 선택 ({modifier}A)",
            command=self.callbacks.get("select_all_files"),
            accelerator=f"{modifier}A",
        )
        edit_menu.add_command(
            label=f"전체 해제 ({modifier}D)",
            command=self.callbacks.get("deselect_all_files"),
            accelerator=f"{modifier}D",
        )
        edit_menu.add_separator()

        edit_menu.add_command(
            label=f"로그 지우기 ({modifier}L)",
            command=self.callbacks.get("clear_log"),
            accelerator=f"{modifier}L",
        )

    def create_tools_menu(self):
        """도구 메뉴 생성"""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="도구", menu=tools_menu)

        modifier = "⌘" if self.is_macos else "Ctrl+"

        tools_menu.add_command(
            label=f"미리보기 ({modifier}P)",
            command=self.callbacks.get("preview_files"),
            accelerator=f"{modifier}P",
        )
        tools_menu.add_command(
            label=f"실행 ({modifier}Enter)",
            command=self.callbacks.get("organize_files"),
            accelerator=f"{modifier}Enter",
        )
        tools_menu.add_separator()

        tools_menu.add_command(
            label="로그 별도창", command=self.callbacks.get("open_log_window")
        )

    def create_help_menu(self):
        """도움말 메뉴 생성"""
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="도움말", menu=help_menu)

        help_menu.add_command(
            label="프로그램 정보", command=self.callbacks.get("show_about")
        )

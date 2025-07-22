#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
드래그 앤 드롭 기능을 추가하는 Mixin 클래스
"""

import os
import platform
import tkinter as tk
from tkinter import StringVar, Widget, filedialog
from typing import Callable, Optional

# tkinterdnd2 안전하게 임포트
try:
    import tkinterdnd2

    HAS_DND = True
except ImportError:
    HAS_DND = False
    tkinterdnd2 = None


class DragDropMixin:
    """드래그 앤 드롭 기능을 추가하는 Mixin 클래스"""

    def setup_drag_drop(
        self,
        widget: Widget,
        string_var: StringVar,
        callback: Optional[Callable] = None,
        accept_files: bool = False,
        accept_folders: bool = True,
    ):
        """위젯에 드래그 앤 드롭 기능 설정

        Args:
            widget: 드래그 앤 드롭을 받을 위젯
            string_var: 경로를 저장할 StringVar
            callback: 드롭 후 실행할 콜백 함수
            accept_files: 파일 허용 여부
            accept_folders: 폴더 허용 여부
        """
        if not HAS_DND:
            # tkinterdnd2가 없으면 기본 동작만 설정
            self._setup_basic_dnd(widget, string_var, callback)
            return

        system = platform.system()

        if system == "Windows":
            self._setup_windows_dnd(
                widget, string_var, callback, accept_files, accept_folders
            )
        elif system == "Darwin":  # macOS
            self._setup_macos_dnd(
                widget, string_var, callback, accept_files, accept_folders
            )
        else:  # Linux
            self._setup_linux_dnd(
                widget, string_var, callback, accept_files, accept_folders
            )

    def _setup_windows_dnd(
        self,
        widget: Widget,
        string_var: StringVar,
        callback: Optional[Callable],
        accept_files: bool,
        accept_folders: bool,
    ):
        """Windows용 드래그 앤 드롭 설정"""
        if not HAS_DND or not tkinterdnd2:
            self._setup_basic_dnd(widget, string_var, callback)
            return

        try:
            widget.drop_target_register(tkinterdnd2.DND_FILES)

            def drop_handler(event):
                # Windows에서는 경로가 중괄호에 둘러싸여 있을 수 있음
                paths = widget.tk.splitlist(event.data)

                for path in paths:
                    # 중괄호 제거
                    path = path.strip("{}")

                    if os.path.exists(path):
                        if accept_folders and os.path.isdir(path):
                            string_var.set(path)
                            if callback:
                                callback(path)
                            break
                        elif accept_files and os.path.isfile(path):
                            string_var.set(path)
                            if callback:
                                callback(path)
                            break

            widget.dnd_bind("<<Drop>>", drop_handler)

        except Exception as e:
            print(f"드래그 앤 드롭 설정 실패: {e}")
            self._setup_basic_dnd(widget, string_var, callback)

    def _setup_macos_dnd(
        self,
        widget: Widget,
        string_var: StringVar,
        callback: Optional[Callable],
        accept_files: bool,
        accept_folders: bool,
    ):
        """macOS용 드래그 앤 드롭 설정"""
        if not HAS_DND or not tkinterdnd2:
            self._setup_basic_dnd(widget, string_var, callback)
            return

        try:
            widget.drop_target_register(tkinterdnd2.DND_FILES)

            def drop_handler(event):
                paths = widget.tk.splitlist(event.data)

                for path in paths:
                    # file:// URL 처리
                    if path.startswith("file://"):
                        path = path[7:]

                    # URL 디코딩
                    from urllib.parse import unquote

                    path = unquote(path)

                    if os.path.exists(path):
                        if accept_folders and os.path.isdir(path):
                            string_var.set(path)
                            if callback:
                                callback(path)
                            break
                        elif accept_files and os.path.isfile(path):
                            string_var.set(path)
                            if callback:
                                callback(path)
                            break

            widget.dnd_bind("<<Drop>>", drop_handler)

        except Exception as e:
            print(f"드래그 앤 드롭 설정 실패: {e}")
            self._setup_basic_dnd(widget, string_var, callback)

    def _setup_linux_dnd(
        self,
        widget: Widget,
        string_var: StringVar,
        callback: Optional[Callable],
        accept_files: bool,
        accept_folders: bool,
    ):
        """Linux용 드래그 앤 드롭 설정"""
        self._setup_windows_dnd(
            widget, string_var, callback, accept_files, accept_folders
        )

    def _setup_basic_dnd(
        self, widget: Widget, string_var: StringVar, callback: Optional[Callable]
    ):
        """기본 드래그 앤 드롭 UI (실제 DnD는 아님)"""
        # 드래그 앤 드롭을 시각적으로 표시
        original_bg = None

        # 위젯 타입에 따라 배경색 가져오기
        try:
            if hasattr(widget, "cget"):
                # Frame의 경우 'bg' 사용
                try:
                    original_bg = widget.cget("bg")
                except tk.TclError:
                    try:
                        original_bg = widget.cget("background")
                    except tk.TclError:
                        original_bg = "#ffffff"  # 기본값
        except:
            original_bg = "#ffffff"

        def on_enter(event):
            if original_bg and hasattr(widget, "config"):
                try:
                    widget.config(bg="#e0e0e0")
                except tk.TclError:
                    try:
                        widget.config(background="#e0e0e0")
                    except:
                        pass
            widget.config(cursor="hand2")

        def on_leave(event):
            if original_bg and hasattr(widget, "config"):
                try:
                    widget.config(bg=original_bg)
                except tk.TclError:
                    try:
                        widget.config(background=original_bg)
                    except:
                        pass
            widget.config(cursor="")

        def on_click(event):
            # 클릭 시 폴더 선택 다이얼로그 열기
            folder = filedialog.askdirectory(title="폴더를 선택하거나 드래그하세요")
            if folder:
                string_var.set(folder)
                if callback:
                    callback(folder)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_click)

        # 도움말 텍스트 추가 (Text 위젯인 경우)
        if hasattr(widget, "insert"):
            if isinstance(widget, tk.Text):
                widget.insert("1.0", "클릭하여 폴더를 선택하세요.")
            elif isinstance(widget, tk.Listbox):
                widget.insert(tk.END, "클릭하여 폴더를 선택하세요.")
            widget.config(state="disabled")


class DragDropFrame:
    """드래그 앤 드롭을 받는 전용 프레임"""

    def __init__(
        self, parent, string_var: StringVar, text: str = "폴더를 여기로 드래그하세요"
    ):
        """초기화

        Args:
            parent: 부모 위젯
            string_var: 경로를 저장할 StringVar
            text: 표시할 텍스트
        """
        import tkinter as tk
        from tkinter import ttk

        self.frame = ttk.Frame(parent, relief="sunken", borderwidth=2)
        self.string_var = string_var

        # 중앙 라벨
        self.label = ttk.Label(
            self.frame,
            text=text,
            anchor="center",
            font=("Arial", 10),
            foreground="#666666",
        )
        self.label.pack(expand=True, fill="both", padx=20, pady=20)

        # 드래그 앤 드롭 설정
        mixin = DragDropMixin()
        mixin.setup_drag_drop(
            self.frame, string_var, callback=self._on_drop, accept_folders=True
        )

        # StringVar 변경 감지
        string_var.trace_add("write", self._on_path_change)

    def _on_drop(self, path: str):
        """드롭 이벤트 처리"""
        self.label.config(text=f"✅ {os.path.basename(path)}", foreground="#008000")

    def _on_path_change(self, *args):
        """경로 변경 시 라벨 업데이트"""
        path = self.string_var.get()
        if path:
            self.label.config(text=f"✅ {os.path.basename(path)}", foreground="#008000")
        else:
            self.label.config(text="폴더를 여기로 드래그하세요", foreground="#666666")

    def grid(self, **kwargs):
        """그리드 레이아웃"""
        return self.frame.grid(**kwargs)

    def pack(self, **kwargs):
        """팩 레이아웃"""
        return self.frame.pack(**kwargs)

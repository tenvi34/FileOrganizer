#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
키보드 단축키 관리
"""

import sys


class ShortcutManager:
    """단축키 관리 클래스"""

    def __init__(self, root, callbacks):
        """초기화
        
        Args:
            root: 루트 윈도우
            callbacks: 콜백 함수 딕셔너리
        """
        self.root = root
        self.callbacks = callbacks
        
        # 플랫폼별 modifier 키 설정
        if sys.platform == "darwin":
            self.modifier = "Command"
            self.mod_key = "Cmd"  # 표시용
        else:
            self.modifier = "Control"
            self.mod_key = "Ctrl"  # 표시용
            
        # 단축키 설정
        self.setup_shortcuts()
        
    def setup_shortcuts(self):
        """모든 단축키 설정"""
        # 파일 작업 단축키
        self.bind_shortcut("r", self.callbacks.get('refresh_files'))  # 새로고침
        self.bind_shortcut("a", self.callbacks.get('select_all_files'))  # 전체 선택
        self.bind_shortcut("d", self.callbacks.get('deselect_all_files'))  # 전체 해제
        
        # 실행 단축키
        self.bind_shortcut("Return", self.callbacks.get('organize_files'))  # 실행
        self.bind_shortcut("p", self.callbacks.get('preview_files'))  # 미리보기
        
        # 로그 관련
        self.bind_shortcut("l", self.callbacks.get('clear_log'))  # 로그 지우기
        self.bind_shortcut("s", self.callbacks.get('save_log'))  # 로그 저장
        
        # F5로 새로고침
        self.root.bind("<F5>", lambda e: self.safe_call('refresh_files'))
        
        # Escape로 작업 취소 (필요시)
        self.root.bind("<Escape>", lambda e: self.safe_call('cancel_operation'))
        
    def bind_shortcut(self, key, callback):
        """단축키 바인딩
        
        Args:
            key: 키 (예: "r", "Return")
            callback: 콜백 함수
        """
        if callback:
            self.root.bind(
                f"<{self.modifier}-{key}>", 
                lambda e: callback()
            )
            
    def safe_call(self, callback_name):
        """안전한 콜백 호출
        
        Args:
            callback_name: 콜백 이름
        """
        callback = self.callbacks.get(callback_name)
        if callback:
            callback()
            
    def get_shortcut_text(self, key):
        """단축키 표시 텍스트 반환
        
        Args:
            key: 키
            
        Returns:
            표시용 텍스트 (예: "Ctrl+R", "⌘R")
        """
        if sys.platform == "darwin":
            return f"⌘{key.upper()}"
        else:
            return f"Ctrl+{key.upper()}"
            
    def unbind_all(self):
        """모든 단축키 해제"""
        # 필요시 구현
        pass
        
    def rebind_all(self):
        """모든 단축키 다시 바인딩"""
        self.setup_shortcuts()
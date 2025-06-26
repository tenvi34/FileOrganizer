#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 매칭 관련 로직
"""

import os
import re
from typing import Generator, Tuple, Dict
from src.constants import FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_SYSTEM

class FileMatcher:
    """파일 매칭 클래스"""
    
    @staticmethod
    def match_file(filename: str, keyword: str, match_mode: str) -> bool:
        """파일명과 키워드 매칭
        
        Args:
            filename: 파일명 (전체 경로)
            keyword: 검색 키워드
            match_mode: 매칭 모드 (포함/정확히/시작/끝/정규식)
            
        Returns:
            매칭 여부
        """
        
        # 파일명만 추출(경로 제외)
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
                return False
        return False
    
    @staticmethod
    def is_system_file(file_path: str) -> bool:
        """시스템/숨김 파일 여부 확인
        
        Args:
            file_path: 파일 경로
            
        Returns:
            시스템/숨김 파일 여부
        """
        
        # 심볼릭 링크 확인
        if os.path.islink(file_path):
            return True
        
        # Windows 시스템/숨김 파일 확인
        if os.name == "nt" and FILE_ATTRIBUTE_HIDDEN is not None:
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(file_path)
                if attrs & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM):
                    return True
            except:  # noqa: E722
                pass
            
        return False
    
    def find_matching_files_generator(self, source: str, rules: Dict, 
                                    include_subfolders: bool = True) -> Generator[Tuple[str, str, str, str], None, None]:
        """매칭되는 파일을 찾아 제너레이터로 반환
        
        Args:
            source: 검색할 소스 디렉토리
            rules: 활성화된 규칙 딕셔너리
            include_subfolders: 하위 폴더 포함 여부
            
        Yields:
            (파일경로, 대상폴더, 키워드, 매칭모드) 튜플
        """
        
        if not source or not os.path.exists(source):
            return
        
        if not rules:
            return
        
        
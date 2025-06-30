#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 이동/복사/삭제 처리 로직
"""

import os
import shutil
import send2trash
from typing import List, Tuple, Callable, Optional


class FileProcessor:
    """파일 처리 클래스"""

    def __init__(self, log_callback: Optional[Callable] = None):
        """초기화

        Args:
            log_callback: 로그 출력 콜백 함수
        """
        self.log_callback = log_callback

    def log(self, message: str):
        """로그 메세지 출력"""
        if self.log_callback:
            self.log_callback(message)

    def process_batch(
        self,
        batch: List[Tuple[str, str, str, str]],
        is_delete: bool,
        is_permanent: bool,
        is_copy: bool,
        operation: str,
    ) -> Tuple[int, int]:
        """배치 단위로 파일 처리

        Args:
            batch: [(파일경로, 대상폴더, 키워드, 매칭모드)] 리스트
            is_delete: 삭제 모드 여부
            is_permanent: 영구 삭제 여부
            is_copy: 복사 모드 여부
            operation: 작업 이름

        Returns:
            (성공_개수, 실패_개수) 튜플
        """
        success_count = 0
        error_count = 0

        for (file_path, dest_folder, keyword, match_mode) in batch:
            try:
                file_name = os.path.basename(file_path)
                
                if is_delete:
                    # 삭제 모드
                    if self._delete_file(file_path, is_permanent):
                        self.log(f"{operation} 완료: {file_name} (규칙: {keyword})")
                        success_count += 1
                    else:
                        error_count += 1
                
                else:
                    # 복사/이동 모드
                    if self._copy_or_move_file(file_path, dest_folder, file_name, is_copy, keyword, match_mode, operation):
                        success_count += 1
                    else:
                        error_count += 1

            except Exception as e:
                self.log(f"오류 발생: {os.path.basename(file_path)} - {str(e)}")
                error_count += 1

        return success_count, error_count
    
    def _delete_file(self, file_path: str, is_permanent: bool) -> bool:
        """파일 삭제
        
        Args:
            file_path: 파일 경로
            is_permanent: 영구 삭제 여부
            
        Returns:
            성공 여부
        """
        file_name = os.path.basename(file_path)

        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            self.log(f"❌ 파일이 존재하지 않음: {file_name}")
            self.log(f"   경로: {file_path}")
            return False

        if is_permanent:
            # 영구 삭제
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                # Windows의 긴 경로 문제일수도 있어 다시 시도
                if os.name == "nt":
                    try:
                        import subprocess
                        if os.name == "nt":
                            # Windows
                            subprocess.run(['cmd', '/c', 'del', '/f', '/q', file_path], ...)
                        else:
                            # macOS/Linux - 그냥 os.remove 사용
                            os.remove(file_path)
                        return True
                    except:  # noqa: E722
                        pass
                self.log(f"❌ 영구 삭제 실패: {file_name} - {str(e)}")
                return False

        else:
            # 휴지통으로 이동
            try:
                # send2trash는 정규화된 경로 필요
                normalized_path = os.path.normpath(file_path)
                send2trash.send2trash(normalized_path)
                return True
            except Exception as e:
                self.log(f"❌ 삭제 실패: {file_name} - {type(e).__name__}: {str(e)}")
                self.log(f"   경로: {file_path}")
                return False
            
    def _copy_or_move_file(self, file_path: str, dest_folder: str, file_name: str,
                          is_copy: bool, keyword: str, match_mode: str, 
                          operation: str) -> bool:
        """파일 복사 또는 이동
        
        Args:
            file_path: 원본 파일 경로
            dest_folder: 대상 폴더
            file_name: 파일명
            is_copy: 복사 여부
            keyword: 매칭 키워드
            match_mode: 매칭 모드
            operation: 작업 이름
            
        Returns:
            성공 여부
        """
        try:
            # 대상 폴더가 없으면 생성
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
                self.log(f"폴더 생성: {dest_folder}")
            
            # 대상 경로 생성
            dest_path = os.path.join(dest_folder, file_name)
            
            # 동일한 파일명이 있는 경우 처리
            if os.path.exists(dest_path):
                dest_path = self._get_unique_path(dest_path)
                
            # 파일 복사 또는 이동
            if is_copy:
                shutil.copy2(file_path, dest_path)
            else:
                shutil.move(file_path, dest_path)
                
            self.log(f"{operation} 완료: {file_name} → {dest_folder} (규칙: {keyword}/{match_mode})")
            return True
            
        except Exception as e:
            self.log(f"❌ {operation} 실패: {file_name} - {str(e)}")
            return False
        
    def _get_unique_path(self, dest_path: str) -> str:
        """중복되지 않는 파일 경로 생성
        
        Args:
            dest_path: 원래 대상 경로
            
        Returns:
            유니크한 파일 경로
        """
        dir_path = os.path.dirname(dest_path)
        file_name = os.path.basename(dest_path)
        base_name, ext = os.path.splitext(file_name)
        
        counter = 1
        while os.path.exists(dest_path):
            new_name = f"{base_name}_{counter}{ext}"
            dest_path = os.path.join(dir_path, new_name)
            counter += 1
            
        return dest_path
    
    @staticmethod
    def safe_path(path: str) -> str:
        """안전한 경로 변환 (Windows 긴 경로 처리)
        
        Args:
            path: 원본 경로
            
        Returns:
            변환된 경로
        """
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
        return os.path.abspath(path)
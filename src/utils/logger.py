#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
로그 관리
"""

import os
from datetime import datetime
from tkinter import filedialog


class Logger:
    """로그 관리 클래스"""

    def __init__(self, log_dir: str = "logs"):
        """초기화

        Args:
            log_dir: 로그 디렉토리
        """
        self.log_dir = log_dir
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """로그 디렉토리 생성"""
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir)
            except Exception as e:
                print(f"로그 디렉토리 생성 실패: {str(e)}")

    def save_log(self, content: str, prefix: str = "file_organizer_log") -> str:
        """로그 저장

        Args:
            content: 로그 내용
            prefix: 파일명 접두사

        Returns:
            저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.txt"
        filepath = os.path.join(self.log_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return filepath
        except Exception as e:
            print(f"로그 저장 실패: {str(e)}")
            return None

    def save_error_log(self, content: str) -> str:
        """에러 로그 저장

        Args:
            content: 로그 내용

        Returns:
            저장된 파일 경로
        """
        return self.save_log(content, prefix="file_organizer_errors")

    def save_log_with_dialog(self, content: str) -> str:
        """다이얼로그를 통한 로그 저장

        Args:
            content: 로그 내용

        Returns:
            저장된 파일 경로
        """
        default_filename = os.path.join(
            self.log_dir,
            f"file_organizer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialdir=self.log_dir,
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
            initialfile=os.path.basename(default_filename),
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                return filename
            except Exception as e:
                print(f"로그 저장 중 오류: {str(e)}")

        return None

    def get_log_files(self) -> list:
        """로그 파일 목록 반환

        Returns:
            로그 파일 경로 리스트
        """
        try:
            files = []
            for filename in os.listdir(self.log_dir):
                if filename.endswith(".txt"):
                    filepath = os.path.join(self.log_dir, filename)
                    files.append(filepath)
            return sorted(files, reverse=True)  # 최신 파일이 앞에
        except Exception:
            return []

    def clean_old_logs(self, days: int = 30):
        """오래된 로그 파일 삭제

        Args:
            days: 보관 일수
        """
        import time

        try:
            current_time = time.time()
            for filepath in self.get_log_files():
                file_time = os.path.getmtime(filepath)
                if current_time - file_time > days * 24 * 3600:
                    os.remove(filepath)
        except Exception as e:
            print(f"오래된 로그 정리 실패: {str(e)}")

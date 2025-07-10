#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
성능 관련 유틸리티
"""

import os
import time
import threading
from typing import Dict, Any, Callable


class FileInfoCache:
    """파일 정보 캐시"""

    def __init__(self, max_size=5000, ttl=60):
        """초기화

        Args:
            max_size: 최대 캐시 크기
            ttl: Time To Live (초)
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self._lock = threading.Lock()

    def get(self, file_path: str) -> Dict[str, Any]:
        """캐시에서 파일 정보 가져오기"""
        with self._lock:
            if file_path in self.cache:
                info, timestamp = self.cache[file_path]
                if time.time() - timestamp < self.ttl:
                    return info
                else:
                    del self.cache[file_path]
        return None

    def set(self, file_path: str, info: Dict[str, Any]):
        """캐시에 파일 정보 저장"""
        with self._lock:
            # 캐시 크기 제한
            if len(self.cache) >= self.max_size:
                # 가장 오래된 항목 제거
                oldest = min(self.cache.items(), key=lambda x: x[1][1])
                del self.cache[oldest[0]]

            self.cache[file_path] = (info, time.time())

    def clear(self):
        """캐시 초기화"""
        with self._lock:
            self.cache.clear()


class ProgressTracker:
    """진행률 추적기"""

    def __init__(self, total: int, callback: Callable = None):
        """초기화

        Args:
            total: 전체 작업 수
            callback: 진행률 업데이트 콜백
        """
        self.total = total
        self.current = 0
        self.callback = callback
        self._lock = threading.Lock()
        self._cancelled = False
        self._last_update = 0
        self._update_interval = 0.1  # 최소 업데이트 간격 (초)

    def update(self, increment: int = 1, message: str = ""):
        """진행률 업데이트"""
        with self._lock:
            self.current += increment
            current_time = time.time()

            # 업데이트 간격 제한 (너무 자주 업데이트하지 않도록)
            if current_time - self._last_update >= self._update_interval:
                if self.callback:
                    progress = (
                        (self.current / self.total * 100) if self.total > 0 else 0
                    )
                    self.callback(self.current, self.total, progress, message)
                self._last_update = current_time

    def cancel(self):
        """작업 취소"""
        with self._lock:
            self._cancelled = True

    @property
    def is_cancelled(self):
        """취소 여부 확인"""
        return self._cancelled

    def reset(self):
        """초기화"""
        with self._lock:
            self.current = 0
            self._cancelled = False
            self._last_update = 0


def copy_file_with_progress(
    src: str,
    dst: str,
    progress_callback: Callable = None,
    chunk_size: int = 1024 * 1024,
):
    """진행률 표시가 있는 파일 복사

    Args:
        src: 원본 파일
        dst: 대상 파일
        progress_callback: 진행률 콜백 (bytes_copied, total_bytes, progress_percent)
        chunk_size: 청크 크기
    """
    file_size = os.path.getsize(src)

    # 작은 파일은 한 번에 복사
    if file_size < 10 * 1024 * 1024:  # 10MB 미만
        import shutil

        shutil.copy2(src, dst)
        if progress_callback:
            progress_callback(file_size, file_size, 100)
        return

    # 대용량 파일은 청크 단위로 복사
    copied = 0
    last_progress = -1

    with open(src, "rb") as fsrc:
        with open(dst, "wb") as fdst:
            while True:
                chunk = fsrc.read(chunk_size)
                if not chunk:
                    break

                fdst.write(chunk)
                copied += len(chunk)

                # 진행률 계산 (1% 단위로 업데이트)
                progress = int((copied / file_size) * 100)
                if progress != last_progress and progress_callback:
                    progress_callback(copied, file_size, progress)
                    last_progress = progress

    # 메타데이터 복사
    import shutil

    shutil.copystat(src, dst)

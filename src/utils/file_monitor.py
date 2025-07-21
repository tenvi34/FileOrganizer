#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 시스템 모니터링 유틸리티
"""

import os
import time
import threading
from typing import Callable, Set, Dict, Optional
from datetime import datetime


class FileSystemMonitor:
    """파일 시스템 변경 모니터링 클래스"""

    def __init__(self, callback: Callable[[str, str], None]):
        """초기화

        Args:
            callback: 파일 변경 시 호출될 콜백 (파일경로, 이벤트타입)
        """
        self.callback = callback
        self.monitored_paths: Set[str] = set()
        self.file_snapshots: Dict[str, Dict] = {}
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.check_interval = 2.0  # 2초마다 체크
        self._lock = threading.Lock()

    def add_path(self, path: str):
        """모니터링 할 경로 추가"""
        if os.path.exists(path):
            with self._lock:
                self.monitored_paths.add(path)
                self._take_snapshot(path)

    def remove_path(self, path: str):
        """모니터링 경로 제거"""
        with self._lock:
            self.monitored_paths.discard(path)
            if path in self.file_snapshots:
                del self.file_snapshots[path]

    def start_monitoring(self):
        """모니터링 시작"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True
            )
            self.monitor_thread.start()

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def monitor_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            with self._lock:
                paths_to_check = list(self.monitored_paths)

            for path in paths_to_check:
                if os.path.exists(path):
                    self._check_for_changes(path)
                else:
                    # 경로가 삭제된 경우
                    with self._lock:
                        self.monitored_paths.discard(path)
                        if path in self.file_snapshots:
                            del self.file_snapshots[path]
                    self.callback(path, "deleted")

            time.sleep(self.check_interval)

    def _take_snapshot(self, path: str):
        """디렉토리 스냅샷 생성"""
        snapshot = {}

        try:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            stat = os.stat(filepath)
                            snapshot[filepath] = {
                                "size": stat.st_size,
                                "mtime": stat.st_mtime,
                            }
                        except:
                            pass
            else:
                # 단일 파일
                try:
                    stat = os.stat(path)
                    snapshot[path] = {"size": stat.st_size, "mtime": stat.st_mtime}
                except:
                    pass

            self.file_snapshots[path] = snapshot

        except Exception as e:
            print(f"스냅샷 생성 오류: {e}")

    def _check_for_changes(self, path: str):
        """변경사항 확인"""
        old_snapshot = self.file_snapshots.get(path, {})
        
        
        
        
        
        
        
        
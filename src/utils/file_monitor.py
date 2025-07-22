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

    def _monitor_loop(self):
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
        new_snapshot = {}

        try:
            if os.path.isdir(path):
                # 디렉토리 스캔
                for root, dirs, files in os.walk(path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            stat = os.stat(filepath)
                            file_info = {"size": stat.st_size, "mtime": stat.st_mtime}
                            new_snapshot[filepath] = file_info

                            # 변경 감지
                            if filepath not in old_snapshot:
                                # 새 파일
                                self.callback(filepath, "created")
                            elif (
                                old_snapshot[filepath]["size"] != file_info["size"]
                                or old_snapshot[filepath]["mtime"] != file_info["mtime"]
                            ):
                                # 수정된 파일
                                self.callback(filepath, "modified")
                        except:
                            pass

                # 삭제된 파일 확인
                for filepath in old_snapshot:
                    if filepath not in new_snapshot:
                        self.callback(filepath, "deleted")

            else:
                # 단일 파일
                try:
                    stat = os.stat(path)
                    file_info = {"size": stat.st_size, "mtime": stat.st_mtime}
                    new_snapshot[path] = file_info

                    if path in old_snapshot:
                        if (
                            old_snapshot[path]["size"] != file_info["size"]
                            or old_snapshot[path]["mtime"] != file_info["mtime"]
                        ):
                            self.callback(path, "modified")
                except:
                    pass

            # 스냅샷 업데이트
            with self._lock:
                self.file_snapshots[path] = new_snapshot

        except Exception as e:
            print(f"변경 확인 오류: {e}")


class AutoOrganizer:
    """자동 파일 정리 기능"""

    def __init__(self, rule_manager, file_processor, log_callback: Callable):
        """초기화

        Args:
            rule_manager: 규칙 관리자
            file_processor: 파일 처리기
            log_callback: 로그 콜백
        """
        self.rule_manager = rule_manager
        self.file_processor = file_processor
        self.log_callback = log_callback
        self.monitor = FileSystemMonitor(self._on_file_change)

        # 자동 정리 설정
        self.auto_organize_enabled = False
        self.watch_folders: Set[str] = set()
        self.organize_delay = 5.0  # 파일 생성 후 5초 대기
        self.pending_files: Dict[str, float] = {}  # 파일경로: 발견시간
        self.organize_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def add_watch_folder(self, folder: str):
        """감시 폴더 추가"""
        if os.path.exists(folder) and os.path.isdir(folder):
            self.watch_folders.add(folder)
            self.monitor.add_path(folder)
            self.log_callback(f"감시 폴더 추가: {folder}")

    def remove_watch_folder(self, folder: str):
        """감시 폴더 제거"""
        self.watch_folders.discard(folder)
        self.monitor.remove_path(folder)
        self.log_callback(f"감시 폴더 제거: {folder}")

    def start_auto_organize(self):
        """자동 정리 시작"""
        if not self.auto_organize_enabled:
            self.auto_organize_enabled = True
            self.monitor.start_monitoring()
            self.organize_thread = threading.Thread(
                target=self._organize_loop, daemon=True
            )
            self.organize_thread.start()
            self.log_callback("자동 파일 정리가 시작되었습니다.")

    def stop_auto_organize(self):
        """자동 정리 중지"""
        if self.auto_organize_enabled:
            self.auto_organize_enabled = False
            self.monitor.stop_monitoring()
            if self.organize_thread:
                self.organize_thread.join(timeout=5)
            self.log_callback("자동 파일 정리가 중지되었습니다.")

    def _on_file_change(self, filepath: str, event_type: str):
        """파일 변경 이벤트 처리"""
        if event_type == "created":
            # 새 파일이 생성되면 대기 목록에 추가
            with self._lock:
                self.pending_files[filepath] = time.time()
            self.log_callback(f"새 파일 감지: {os.path.basename(filepath)}")

    def _organize_loop(self):
        """자동 정리 루프"""
        while self.auto_organize_enabled:
            current_time = time.time()
            files_to_process = []

            with self._lock:
                # 대기 시간이 지난 파일들 선택
                for filepath, added_time in list(self.pending_files.items()):
                    if current_time - added_time >= self.organize_delay:
                        if os.path.exists(filepath) and os.path.isfile(filepath):
                            files_to_process.append(filepath)
                        del self.pending_files[filepath]

            # 파일 처리
            for filepath in files_to_process:
                self._process_file(filepath)

            time.sleep(1)  # 1초마다 체크

    def _process_file(self, filepath: str):
        """단일 파일 처리"""
        try:
            # 활성화된 규칙 가져오기
            active_rules = self.rule_manager.get_active_rules()
            if not active_rules:
                return

            # 파일 매칭 확인
            filename = os.path.basename(filepath)

            for keyword, rule_data in active_rules.items():
                dest = rule_data.get("dest", "")
                match_mode = rule_data.get("match_mode", "포함")

                # 파일 매칭 확인
                if self._match_file(filename, keyword, match_mode):
                    # 파일 이동
                    batch = [(filepath, dest, keyword, match_mode)]
                    success, error = self.file_processor.process_batch(
                        batch, False, False, False, "자동 이동"
                    )

                    if success > 0:
                        self.log_callback(
                            f"자동 정리: {filename} → {os.path.basename(dest)}"
                        )
                    break
        except Exception as e:
            self.log_callback(f"자동 정리 오류: {str(e)}")

    def _match_file(self, filename: str, keyword: str, match_mode: str) -> bool:
        """파일명 매칭 확인"""
        if match_mode == "포함":
            return keyword.lower() in filename.lower()
        elif match_mode == "정확히":
            name_without_ext, _ = os.path.splitext(filename)
            return keyword.lower() == name_without_ext.lower()
        elif match_mode == "시작":
            return filename.lower().startswith(keyword.lower())
        elif match_mode == "끝":
            name_without_ext, _ = os.path.splitext(filename)
            return name_without_ext.lower().endswith(keyword.lower())
        elif match_mode == "정규식":
            import re

            try:
                return bool(re.search(keyword, filename, re.IGNORECASE))
            except re.error:
                return False
        return False

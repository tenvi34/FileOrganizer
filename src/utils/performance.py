#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
성능 관련 유틸리티
"""

import os
import time
import threading
import hashlib
import platform
import concurrent.futures
import shutil
from typing import Dict, Any, Callable, Optional, Tuple


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


def get_optimal_chunk_size(file_size: int) -> int:
    """파일 크기에 따른 최적 청크 크기 계산

    Args:
        file_size: 파일 크기 (바이트)

    Returns:
        최적 청크 크기
    """
    if file_size < 10 * 1024 * 1024:  # 10MB 미만
        return 512 * 1024  # 512KB
    elif file_size < 100 * 1024 * 1024:  # 100MB 미만
        return 1024 * 1024  # 1MB
    elif file_size < 1024 * 1024 * 1024:  # 1GB 미만
        return 10 * 1024 * 1024  # 10MB
    elif file_size < 10 * 1024 * 1024 * 1024:  # 10GB 미만
        return 50 * 1024 * 1024  # 50MB
    else:  # 10GB 이상
        return 100 * 1024 * 1024  # 100MB


def is_network_drive(path: str) -> bool:
    """네트워크 드라이브 여부 확인

    Args:
        path: 확인할 경로

    Returns:
        네트워크 드라이브 여부
    """
    if platform.system() == "Windows":
        import win32file

        drive = os.path.splitdrive(path)[0] + "\\"
        drive_type = win32file.GetDriveType(drive)
        return drive_type == win32file.DRIVE_REMOTE
    else:
        # Linux/Mac: 마운트 정보 확인
        import subprocess

        try:
            result = subprocess.run(["df", "-P", path], capture_output=True, text=True)
            output = result.stdout.strip().split("\n")[-1]
            # 네트워크 파일시스템 패턴 확인
            network_patterns = ["://", "nfs", "cifs", "smb", "afp"]
            return any(pattern in output.lower() for pattern in network_patterns)
        except:
            return False


def copy_file_with_progress_optimized(
    src: str,
    dst: str,
    progress_callback: Optional[Callable] = None,
    verify: bool = False,
    use_multithread: bool = False,
) -> Tuple[bool, Optional[str]]:
    """최적화된 파일 복사

    Args:
        src: 원본 파일
        dst: 대상 파일
        progress_callback: 진행률 콜백
        verify: 복사 후 검증 여부
        use_multithread: 멀티스레드 사용 여부

    Returns:
        (성공 여부, 에러 메시지)
    """
    file_size = os.path.getsize(src)

    # 네트워크 드라이브 확인
    is_network = is_network_drive(dst)

    # 최적 청크 크기 결정
    chunk_size = get_optimal_chunk_size(file_size)
    if is_network:
        chunk_size = max(chunk_size, 50 * 1024 * 1024)  # 네트워크는 최소 50MB

    try:
        # 대용량 파일이고 로컬 드라이브면 멀티스레드 사용
        if use_multithread and file_size > 1024 * 1024 * 1024 and not is_network:
            success = copy_file_multithread(src, dst, progress_callback)
        else:
            success = copy_file_single_thread(src, dst, chunk_size, progress_callback)

        if not success:
            return False, "복사 실패"

        # 복사 후 검증
        if verify:
            if not verify_copy(src, dst, progress_callback):
                os.remove(dst)  # 검증 실패 시 삭제
                return False, "파일 검증 실패"

        return True, None

    except Exception as e:
        if os.path.exists(dst):
            os.remove(dst)  # 실패 시 부분 파일 삭제
        return False, str(e)


def copy_file_single_thread(
    src: str, dst: str, chunk_size: int, progress_callback: Optional[Callable] = None
) -> bool:
    """단일 스레드 파일 복사"""
    file_size = os.path.getsize(src)
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

                # 진행률 계산
                progress = int((copied / file_size) * 100)
                if progress != last_progress and progress_callback:
                    progress_callback(copied, file_size, progress)
                    last_progress = progress

    # 메타데이터 복사
    import shutil

    shutil.copystat(src, dst)
    return True


def copy_file_multithread(
    src: str,
    dst: str,
    progress_callback: Optional[Callable] = None,
    num_threads: int = 4,
) -> bool:
    """멀티스레드 파일 복사

    대용량 파일을 여러 스레드로 나누어 복사
    """
    file_size = os.path.getsize(src)
    chunk_size = file_size // num_threads

    # 임시 파일들 생성
    temp_files = []
    futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_threads):
            start_pos = i * chunk_size
            end_pos = start_pos + chunk_size if i < num_threads - 1 else file_size
            temp_file = f"{dst}.part{i}"
            temp_files.append(temp_file)

            future = executor.submit(
                copy_file_range,
                src,
                temp_file,
                start_pos,
                end_pos,
                i,
                num_threads,
                progress_callback,
            )
            futures.append(future)

        # 모든 스레드 완료 대기
        for future in concurrent.futures.as_completed(futures):
            if not future.result():
                # 실패 시 임시 파일 정리
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                return False

    # 임시 파일들을 하나로 합치기
    with open(dst, "wb") as fdst:
        for temp_file in temp_files:
            with open(temp_file, "rb") as fsrc:
                shutil.copyfileobj(fsrc, fdst)
            os.remove(temp_file)

    # 메타데이터 복사
    import shutil

    shutil.copystat(src, dst)
    return True


def copy_file_range(
    src: str,
    dst: str,
    start: int,
    end: int,
    thread_id: int,
    total_threads: int,
    progress_callback: Optional[Callable] = None,
) -> bool:
    """파일의 특정 범위 복사"""
    try:
        with open(src, "rb") as fsrc:
            fsrc.seek(start)
            remaining = end - start

            with open(dst, "wb") as fdst:
                chunk_size = 10 * 1024 * 1024  # 10MB
                copied = 0

                while remaining > 0:
                    to_read = min(chunk_size, remaining)
                    chunk = fsrc.read(to_read)
                    if not chunk:
                        break

                    fdst.write(chunk)
                    copied += len(chunk)
                    remaining -= len(chunk)

                    # 스레드별 진행률 계산
                    if progress_callback:
                        thread_progress = (copied / (end - start)) * 100
                        overall_progress = (
                            (thread_id + thread_progress / 100) / total_threads * 100
                        )
                        progress_callback(
                            start + copied,
                            end - start,
                            overall_progress,
                            f"스레드 {thread_id + 1}/{total_threads}",
                        )

        return True
    except Exception as e:
        print(f"스레드 {thread_id} 복사 실패: {e}")
        return False


def calculate_file_hash(
    file_path: str,
    algorithm: str = "md5",
    chunk_size: int = 8192,
    progress_callback: Optional[Callable] = None,
) -> str:
    """파일 해시 계산

    Args:
        file_path: 파일 경로
        algorithm: 해시 알고리즘 ('md5', 'sha1', 'sha256')
        chunk_size: 읽기 청크 크기
        progress_callback: 진행률 콜백

    Returns:
        해시 값
    """
    hash_obj = hashlib.new(algorithm)
    file_size = os.path.getsize(file_path)
    processed = 0

    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
            processed += len(chunk)

            if progress_callback:
                progress = int((processed / file_size) * 100)
                progress_callback(
                    processed,
                    file_size,
                    progress,
                    f"해시 계산 중... ({algorithm.upper()})",
                )

    return hash_obj.hexdigest()


def verify_copy(
    src: str,
    dst: str,
    progress_callback: Optional[Callable] = None,
    quick_check: bool = True,
) -> bool:
    """파일 복사 검증

    Args:
        src: 원본 파일
        dst: 복사된 파일
        progress_callback: 진행률 콜백
        quick_check: 빠른 검사 (크기와 수정 시간만)

    Returns:
        검증 성공 여부
    """
    # 1. 파일 크기 확인
    if os.path.getsize(src) != os.path.getsize(dst):
        return False

    # 빠른 검사면 여기서 종료
    if quick_check:
        return True

    # 2. 해시 비교 (완전 검증)
    if progress_callback:
        progress_callback(0, 100, 0, "원본 파일 해시 계산 중...")

    src_hash = calculate_file_hash(src, "md5", progress_callback=progress_callback)

    if progress_callback:
        progress_callback(50, 100, 50, "복사본 해시 계산 중...")

    dst_hash = calculate_file_hash(dst, "md5", progress_callback=progress_callback)

    return src_hash == dst_hash


class FileOperationQueue:
    """파일 작업 큐 - 대량 작업 최적화"""

    def __init__(self, max_concurrent: int = 3):
        """초기화

        Args:
            max_concurrent: 최대 동시 작업 수
        """
        self.queue = []
        self.max_concurrent = max_concurrent
        self.active_operations = []
        self.completed = []
        self.failed = []
        self._lock = threading.Lock()
        self._stop_flag = False

    def add_operation(self, operation_type: str, src: str, dst: str = None):
        """작업 추가"""
        with self._lock:
            self.queue.append(
                {
                    "type": operation_type,  # 'copy', 'move', 'delete'
                    "src": src,
                    "dst": dst,
                    "status": "pending",
                    "progress": 0,
                }
            )

    def process_queue(self, progress_callback: Optional[Callable] = None):
        """큐 처리"""
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent
        ) as executor:
            futures = []

            while self.queue or futures:
                if self._stop_flag:
                    break

                # 새 작업 시작
                while len(futures) < self.max_concurrent and self.queue:
                    operation = self.queue.pop(0)
                    future = executor.submit(self._process_operation, operation)
                    futures.append((future, operation))

                # 완료된 작업 확인
                for future, operation in futures[:]:
                    if future.done():
                        futures.remove((future, operation))
                        try:
                            result = future.result()
                            if result:
                                self.completed.append(operation)
                            else:
                                self.failed.append(operation)
                        except Exception as e:
                            operation["error"] = str(e)
                            self.failed.append(operation)

                        if progress_callback:
                            total = (
                                len(self.completed)
                                + len(self.failed)
                                + len(self.queue)
                                + len(futures)
                            )
                            done = len(self.completed) + len(self.failed)
                            progress_callback(done, total, (done / total) * 100)

                time.sleep(0.1)  # CPU 사용률 제어

    def _process_operation(self, operation: dict) -> bool:
        """개별 작업 처리"""
        try:
            if operation["type"] == "copy":
                return copy_file_with_progress_optimized(
                    operation["src"], operation["dst"], verify=True
                )[0]
            elif operation["type"] == "move":
                shutil.move(operation["src"], operation["dst"])
                return True
            elif operation["type"] == "delete":
                os.remove(operation["src"])
                return True
        except Exception as e:
            print(f"작업 실패: {e}")
            return False

    def stop(self):
        """큐 처리 중지"""
        self._stop_flag = True

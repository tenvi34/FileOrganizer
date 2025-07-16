#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
성능 벤치마크 도구
"""

import os
import time
import tempfile
import platform
import threading
from typing import Dict, List, Tuple, Optional, Callable
from datetime import datetime
import json

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("psutil이 설치되지 않았습니다. 일부 시스템 정보를 사용할 수 없습니다.")


class PerformanceBenchmark:
    """성능 벤치마크 클래스"""

    def __init__(self, log_callback: Optional[Callable] = None):
        """초기화

        Args:
            log_callback: 로그 출력 콜백 함수
        """
        self.log_callback = log_callback
        self.results = []
        self.current_test = None
        self._stop_flag = False

    def log(self, message: str):
        """로그 메시지 출력"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[벤치마크] {message}")

    def run_complete_benchmark(
        self, progress_callback: Optional[Callable] = None
    ) -> Dict:
        """완전한 벤치마크 실행

        Args:
            progress_callback: 진행률 콜백 (current, total, message)

        Returns:
            벤치마크 결과
        """
        self.log("성능 벤치마크를 시작합니다...")
        self._stop_flag = False

        results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.get_system_info(),
            "disk_info": self.get_disk_info(),
            "copy_tests": {},
            "io_tests": {},
            "recommendations": {},
        }

        total_steps = 10
        current_step = 0

        try:
            # 1. 시스템 정보 수집
            if progress_callback:
                progress_callback(current_step, total_steps, "시스템 정보 수집 중...")
            current_step += 1

            # 2. 디스크 공간 확인
            if progress_callback:
                progress_callback(current_step, total_steps, "디스크 공간 확인 중...")
            available_space = self._get_available_space()
            self.log(f"사용 가능한 공간: {self._format_size(available_space)}")
            current_step += 1

            # 3. 테스트 크기 결정
            test_sizes = self._determine_test_sizes(available_space)
            self.log(f"테스트 크기: {[self._format_size(s) for s in test_sizes]}")

            # 4. 순차 읽기/쓰기 테스트
            if not self._stop_flag:
                if progress_callback:
                    progress_callback(
                        current_step, total_steps, "순차 I/O 테스트 중..."
                    )
                results["io_tests"]["sequential"] = self._test_sequential_io(
                    test_sizes[0]
                )
                current_step += 1

            # 5. 랜덤 읽기/쓰기 테스트
            if not self._stop_flag:
                if progress_callback:
                    progress_callback(
                        current_step, total_steps, "랜덤 I/O 테스트 중..."
                    )
                results["io_tests"]["random"] = self._test_random_io(
                    min(test_sizes[0], 100 * 1024 * 1024)
                )
                current_step += 1

            # 6. 파일 복사 테스트
            copy_test_count = min(len(test_sizes), 4)
            for i, size in enumerate(test_sizes[:copy_test_count]):
                if self._stop_flag:
                    break

                if progress_callback:
                    progress_callback(
                        current_step + i,
                        total_steps,
                        f"복사 테스트 중... ({self._format_size(size)})",
                    )

                results["copy_tests"][self._format_size(size)] = (
                    self._test_copy_performance(size)
                )

            current_step += copy_test_count

            # 7. 결과 분석
            if progress_callback:
                progress_callback(current_step, total_steps, "결과 분석 중...")
            results["recommendations"] = self._analyze_results(results)

            # 8. 완료
            if progress_callback:
                progress_callback(total_steps, total_steps, "벤치마크 완료!")

            self.log("벤치마크가 완료되었습니다.")

        except Exception as e:
            self.log(f"벤치마크 중 오류 발생: {str(e)}")
            results["error"] = str(e)

        return results

    def stop_benchmark(self):
        """벤치마크 중지"""
        self._stop_flag = True
        self.log("벤치마크 중지 요청...")

    def _determine_test_sizes(self, available_space: int) -> List[int]:
        """테스트 크기 결정

        Args:
            available_space: 사용 가능한 공간

        Returns:
            테스트 크기 리스트
        """
        # 기본 테스트 크기
        base_sizes = [
            10 * 1024 * 1024,  # 10MB
            50 * 1024 * 1024,  # 50MB
            100 * 1024 * 1024,  # 100MB
            500 * 1024 * 1024,  # 500MB
            1024 * 1024 * 1024,  # 1GB
            2 * 1024 * 1024 * 1024,  # 2GB
        ]

        # 사용 가능한 공간의 10%를 넘지 않도록 필터링
        max_test_size = available_space * 0.1
        test_sizes = [size for size in base_sizes if size <= max_test_size]

        # 최소한 10MB는 테스트
        if not test_sizes:
            test_sizes = [10 * 1024 * 1024]

        return test_sizes[:4]  # 최대 4개까지만

    def _test_sequential_io(self, size: int) -> Dict:
        """순차 I/O 테스트"""
        results = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "sequential_test.bin")

            # 순차 쓰기 테스트
            start_time = time.time()
            self._create_test_file(test_file, size)
            write_time = time.time() - start_time
            write_speed = size / write_time / (1024 * 1024)  # MB/s
            results["write_speed"] = write_speed

            # 순차 읽기 테스트
            start_time = time.time()
            with open(test_file, "rb") as f:
                while f.read(1024 * 1024):  # 1MB씩 읽기
                    pass
            read_time = time.time() - start_time
            read_speed = size / read_time / (1024 * 1024)  # MB/s
            results["read_speed"] = read_speed

            self.log(
                f"순차 I/O: 읽기 {read_speed:.1f} MB/s, 쓰기 {write_speed:.1f} MB/s"
            )

        return results

    def _test_random_io(self, size: int) -> Dict:
        """랜덤 I/O 테스트"""
        results = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "random_test.bin")
            self._create_test_file(test_file, size)

            # 랜덤 읽기 테스트 (4KB 블록)
            import random

            block_size = 4096
            num_blocks = size // block_size
            test_blocks = 1000  # 1000개 블록 테스트

            start_time = time.time()
            with open(test_file, "rb") as f:
                for _ in range(min(test_blocks, num_blocks)):
                    pos = random.randint(0, num_blocks - 1) * block_size
                    f.seek(pos)
                    f.read(block_size)

            elapsed = time.time() - start_time
            iops = test_blocks / elapsed
            results["random_read_iops"] = iops

            self.log(f"랜덤 I/O: {iops:.0f} IOPS")

        return results

    def _test_copy_performance(self, size: int) -> Dict:
        """파일 복사 성능 테스트"""
        from src.utils.performance import copy_file_with_progress_optimized

        results = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            src_file = os.path.join(temp_dir, f"test_{size}.bin")
            dst_file = os.path.join(temp_dir, f"test_{size}_copy.bin")

            # 테스트 파일 생성
            self.log(f"테스트 파일 생성 중... ({self._format_size(size)})")
            self._create_test_file(src_file, size)

            # 단일 스레드 복사 테스트
            self.log("단일 스레드 복사 테스트...")
            start_time = time.time()
            success, error = copy_file_with_progress_optimized(
                src_file, dst_file, use_multithread=False, verify=False
            )
            single_time = time.time() - start_time

            if success:
                single_speed = size / single_time / (1024 * 1024)  # MB/s
                results["single_thread"] = {"time": single_time, "speed": single_speed}
                self.log(f"단일 스레드: {single_speed:.1f} MB/s")
                os.remove(dst_file)

            # 멀티스레드 복사 테스트 (1GB 이상만)
            if size >= 1024 * 1024 * 1024:
                self.log("멀티스레드 복사 테스트...")
                start_time = time.time()
                success, error = copy_file_with_progress_optimized(
                    src_file, dst_file, use_multithread=True, verify=False
                )
                multi_time = time.time() - start_time

                if success:
                    multi_speed = size / multi_time / (1024 * 1024)  # MB/s
                    results["multi_thread"] = {"time": multi_time, "speed": multi_speed}
                    improvement = ((multi_speed / single_speed) - 1) * 100
                    results["improvement"] = improvement
                    self.log(
                        f"멀티스레드: {multi_speed:.1f} MB/s (향상: {improvement:.1f}%)"
                    )

        return results

    def _create_test_file(self, path: str, size: int):
        """테스트 파일 생성"""
        chunk_size = 1024 * 1024  # 1MB
        remaining = size

        with open(path, "wb") as f:
            while remaining > 0:
                chunk = min(chunk_size, remaining)
                # 압축이 안 되는 랜덤 데이터 생성
                data = os.urandom(chunk)
                f.write(data)
                remaining -= chunk

    def _analyze_results(self, results: Dict) -> Dict:
        """결과 분석 및 권장사항 생성"""
        recommendations = {
            "storage_type": "Unknown",
            "performance_level": "Unknown",
            "settings": {},
        }

        # 순차 I/O 속도로 스토리지 타입 판단
        if "sequential" in results["io_tests"]:
            seq_read = results["io_tests"]["sequential"].get("read_speed", 0)
            seq_write = results["io_tests"]["sequential"].get("write_speed", 0)
            avg_speed = (seq_read + seq_write) / 2

            if avg_speed > 1000:
                recommendations["storage_type"] = "NVMe SSD"
                recommendations["performance_level"] = "Excellent"
            elif avg_speed > 300:
                recommendations["storage_type"] = "SATA SSD"
                recommendations["performance_level"] = "Good"
            elif avg_speed > 100:
                recommendations["storage_type"] = "HDD (7200 RPM)"
                recommendations["performance_level"] = "Average"
            else:
                recommendations["storage_type"] = "HDD (5400 RPM) or Network"
                recommendations["performance_level"] = "Below Average"

        # 권장 설정
        if recommendations["performance_level"] == "Excellent":
            recommendations["settings"] = {
                "multithread_copy": True,
                "thread_count": 4,
                "verify_copy": True,
                "verify_method": "quick",
                "batch_size": 1000,
                "cache_size": 10000,
            }
        elif recommendations["performance_level"] == "Good":
            recommendations["settings"] = {
                "multithread_copy": True,
                "thread_count": 2,
                "verify_copy": True,
                "verify_method": "quick",
                "batch_size": 500,
                "cache_size": 5000,
            }
        else:
            recommendations["settings"] = {
                "multithread_copy": False,
                "thread_count": 1,
                "verify_copy": False,
                "verify_method": "none",
                "batch_size": 100,
                "cache_size": 1000,
            }

        return recommendations

    def get_system_info(self) -> Dict[str, str]:
        """시스템 정보 가져오기"""
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count() or 1,
        }

        if HAS_PSUTIL:
            # CPU 정보
            info["cpu_physical_cores"] = psutil.cpu_count(logical=False)
            info["cpu_logical_cores"] = psutil.cpu_count(logical=True)

            # 메모리 정보
            mem = psutil.virtual_memory()
            info["memory_total"] = self._format_size(mem.total)
            info["memory_available"] = self._format_size(mem.available)
            info["memory_percent"] = f"{mem.percent:.1f}%"

        return info

    def get_disk_info(self) -> Dict[str, Dict]:
        """디스크 정보 가져오기"""
        disk_info = {}

        if HAS_PSUTIL:
            for partition in psutil.disk_partitions():
                if partition.device:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_info[partition.device] = {
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": self._format_size(usage.total),
                            "used": self._format_size(usage.used),
                            "free": self._format_size(usage.free),
                            "percent": f"{usage.percent:.1f}%",
                        }
                    except:
                        pass
        else:
            # 기본 정보만
            import shutil

            usage = shutil.disk_usage(".")
            disk_info["current"] = {
                "total": self._format_size(usage.total),
                "used": self._format_size(usage.used),
                "free": self._format_size(usage.free),
                "percent": f"{(usage.used / usage.total * 100):.1f}%",
            }

        return disk_info

    def _get_available_space(self) -> int:
        """사용 가능한 디스크 공간 가져오기"""
        import shutil

        stat = shutil.disk_usage(".")
        return stat.free

    def _format_size(self, size: int) -> str:
        """크기를 읽기 쉬운 형식으로 변환"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def estimate_operation_time(
        self, file_sizes: List[int], operation: str = "copy"
    ) -> Dict:
        """작업 시간 예측

        Args:
            file_sizes: 파일 크기 리스트
            operation: 작업 유형 ('copy', 'move', 'delete')

        Returns:
            예상 시간 정보
        """
        total_size = sum(file_sizes)
        file_count = len(file_sizes)

        # 최근 벤치마크 결과가 있으면 사용
        if self.results and "copy_tests" in self.results[-1]:
            # 가장 적합한 테스트 결과 찾기
            copy_tests = self.results[-1]["copy_tests"]
            speeds = []
            for test_size, test_result in copy_tests.items():
                if "single_thread" in test_result:
                    speeds.append(test_result["single_thread"]["speed"])

            if speeds:
                avg_speed = sum(speeds) / len(speeds)
            else:
                avg_speed = 100  # 기본값 100 MB/s
        else:
            # 기본 추정값
            avg_speed = 100  # MB/s

        # 작업별 속도 조정
        if operation == "move":
            # 같은 드라이브면 매우 빠름 (메타데이터만 변경)
            avg_speed *= 10
        elif operation == "delete":
            # 삭제는 매우 빠름
            avg_speed *= 20

        # 예상 시간 계산
        time_seconds = total_size / (avg_speed * 1024 * 1024)

        # 파일 수에 따른 오버헤드
        overhead = file_count * 0.01  # 파일당 0.01초
        total_time = time_seconds + overhead

        return {
            "estimated_seconds": total_time,
            "estimated_time": self._format_time(total_time),
            "total_size": self._format_size(total_size),
            "file_count": file_count,
            "average_speed": f"{avg_speed:.1f} MB/s",
        }

    def _format_time(self, seconds: float) -> str:
        """시간을 읽기 쉬운 형식으로 변환"""
        if seconds < 60:
            return f"{seconds:.1f}초"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}분"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}시간"

    def save_results(self, filepath: str):
        """벤치마크 결과 저장"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def load_results(self, filepath: str):
        """벤치마크 결과 로드"""
        with open(filepath, "r", encoding="utf-8") as f:
            self.results = json.load(f)

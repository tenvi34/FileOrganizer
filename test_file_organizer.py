#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 정리 프로그램 자동 테스트 (최신 버전)
"""

import unittest
import os
import shutil
import tempfile
import json
import time
import threading
from pathlib import Path
import tkinter as tk
from unittest.mock import patch, MagicMock, Mock
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 모듈 임포트
from src.core.file_matcher import FileMatcher
from src.core.file_processor import FileProcessor
from src.core.rule_manager import RuleManager
from src.utils.config import ConfigManager
from src.utils.logger import Logger
from src.utils.validators import Validator
from src.utils.performance import FileInfoCache, ProgressTracker, get_optimal_chunk_size, is_network_drive
from src.utils.benchmark import PerformanceBenchmark
from src.utils.file_monitor import FileSystemMonitor, AutoOrganizer
from src.ui.main_window import MainWindow
from src.constants import *


class TestFileMatcher(unittest.TestCase):
    """FileMatcher 클래스 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.matcher = FileMatcher()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_match_file_contains(self):
        """포함 매칭 테스트"""
        self.assertTrue(self.matcher.match_file("test_document.pdf", "doc", "포함"))
        self.assertFalse(self.matcher.match_file("test_file.pdf", "doc", "포함"))

    def test_match_file_exact(self):
        """정확히 매칭 테스트"""
        self.assertTrue(self.matcher.match_file("report.pdf", "report", "정확히"))
        self.assertFalse(self.matcher.match_file("report_2025.pdf", "report", "정확히"))

    def test_match_file_starts(self):
        """시작 매칭 테스트"""
        self.assertTrue(self.matcher.match_file("report_2025.pdf", "report", "시작"))
        self.assertFalse(self.matcher.match_file("2025_report.pdf", "report", "시작"))

    def test_match_file_ends(self):
        """끝 매칭 테스트"""
        self.assertTrue(self.matcher.match_file("doc_report.pdf", "report", "끝"))
        self.assertFalse(self.matcher.match_file("report_doc.pdf", "report", "끝"))

    def test_match_file_regex(self):
        """정규식 매칭 테스트"""
        self.assertTrue(
            self.matcher.match_file("2025_report.pdf", r"^\d{4}_", "정규식")
        )
        self.assertFalse(
            self.matcher.match_file("report_2025.pdf", r"^\d{4}_", "정규식")
        )

    def test_find_matching_files_generator(self):
        """파일 검색 제너레이터 테스트"""
        # 테스트 파일 생성
        test_files = ["doc1.txt", "doc2.pdf", "image.jpg"]
        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w") as f:
                f.write("test")

        # 규칙 설정
        rules = {"doc": {"dest": "/dest", "match_mode": "포함", "enabled": True}}

        # 매칭 파일 찾기
        matches = list(
            self.matcher.find_matching_files_generator(
                self.temp_dir, rules, include_subfolders=False
            )
        )

        # 검증
        self.assertEqual(len(matches), 2)  # doc1.txt, doc2.pdf
        matched_names = [os.path.basename(m[0]) for m in matches]
        self.assertIn("doc1.txt", matched_names)
        self.assertIn("doc2.pdf", matched_names)

    def test_is_system_file(self):
        """시스템 파일 판별 테스트"""
        # 일반 파일 생성
        normal_path = os.path.join(self.temp_dir, "visible.txt")
        with open(normal_path, "w") as f:
            f.write("visible")

        # 검증
        self.assertFalse(self.matcher.is_system_file(normal_path))
        
        # 심볼릭 링크 테스트 (가능한 경우)
        if hasattr(os, 'symlink'):
            try:
                link_path = os.path.join(self.temp_dir, "link.txt")
                os.symlink(normal_path, link_path)
                self.assertTrue(self.matcher.is_system_file(link_path))
            except:
                pass  # 심볼릭 링크 생성 실패 시 패스


class TestFileProcessor(unittest.TestCase):
    """FileProcessor 클래스 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        os.makedirs(self.source_dir)
        os.makedirs(self.dest_dir)

        # 로그 콜백 모의
        self.log_messages = []
        self.processor = FileProcessor(
            log_callback=lambda msg: self.log_messages.append(msg)
        )

        # get_config 메서드 모킹
        self.processor.get_config = lambda key, default: default

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_process_batch_move(self):
        """파일 이동 테스트"""
        # 테스트 파일 생성
        test_file = os.path.join(self.source_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # 배치 처리
        batch = [(test_file, self.dest_dir, "test", "포함")]
        success, error = self.processor.process_batch(
            batch, is_delete=False, is_permanent=False, is_copy=False, operation="이동"
        )

        # 검증
        self.assertEqual(success, 1)
        self.assertEqual(error, 0)
        self.assertFalse(os.path.exists(test_file))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "test.txt")))

    def test_process_batch_copy(self):
        """파일 복사 테스트"""
        # 테스트 파일 생성
        test_file = os.path.join(self.source_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # format_file_size 메서드 추가
        if not hasattr(self.processor, "format_file_size"):
            self.processor.format_file_size = lambda size: f"{size} B"

        # 배치 처리
        batch = [(test_file, self.dest_dir, "test", "포함")]
        success, error = self.processor.process_batch(
            batch, is_delete=False, is_permanent=False, is_copy=True, operation="복사"
        )

        # 검증
        self.assertEqual(success, 1)
        self.assertEqual(error, 0)
        self.assertTrue(os.path.exists(test_file))  # 원본 유지
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "test.txt")))

    def test_process_batch_delete(self):
        """파일 삭제 테스트"""
        # 테스트 파일 생성
        test_file = os.path.join(self.source_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # 배치 처리 (휴지통)
        batch = [(test_file, "", "test", "포함")]
        success, error = self.processor.process_batch(
            batch, is_delete=True, is_permanent=False, is_copy=False, operation="삭제"
        )

        # 검증
        self.assertEqual(success, 1)
        self.assertEqual(error, 0)
        self.assertFalse(os.path.exists(test_file))

    def test_duplicate_file_handling(self):
        """중복 파일 처리 테스트"""
        # 같은 이름의 파일 생성
        test_file = os.path.join(self.source_dir, "test.txt")
        existing_file = os.path.join(self.dest_dir, "test.txt")

        with open(test_file, "w") as f:
            f.write("new content")
        with open(existing_file, "w") as f:
            f.write("existing content")

        # 배치 처리
        batch = [(test_file, self.dest_dir, "test", "포함")]
        success, error = self.processor.process_batch(
            batch, is_delete=False, is_permanent=False, is_copy=False, operation="이동"
        )

        # 검증
        self.assertEqual(success, 1)
        self.assertEqual(error, 0)
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "test_1.txt")))

    def test_safe_path(self):
        """안전한 경로 변환 테스트"""
        # 일반 경로
        normal_path = "/home/user/file.txt"
        result = self.processor.safe_path(normal_path)
        self.assertTrue(os.path.isabs(result))

        # Windows 긴 경로 테스트 (Windows에서만)
        if os.name == 'nt':
            long_path = "C:\\" + "a" * 300 + "\\file.txt"
            result = self.processor.safe_path(long_path)
            self.assertTrue(result.startswith("\\\\?\\"))


class TestRuleManager(unittest.TestCase):
    """RuleManager 클래스 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.rule_manager = RuleManager(self.config_file)

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_rule(self):
        """규칙 추가 테스트"""
        result = self.rule_manager.add_rule("test", "/dest/path", "포함")

        self.assertTrue(result)
        self.assertIn("test", self.rule_manager.rules)
        self.assertEqual(self.rule_manager.rules["test"]["dest"], "/dest/path")
        self.assertEqual(self.rule_manager.rules["test"]["match_mode"], "포함")
        self.assertTrue(self.rule_manager.rules["test"]["enabled"])

    def test_delete_rule(self):
        """규칙 삭제 테스트"""
        # 규칙 추가
        self.rule_manager.add_rule("test", "/dest/path", "포함")

        # 규칙 삭제
        result = self.rule_manager.delete_rule("test")

        self.assertTrue(result)
        self.assertNotIn("test", self.rule_manager.rules)

    def test_toggle_rule(self):
        """규칙 활성화/비활성화 토글 테스트"""
        # 규칙 추가
        self.rule_manager.add_rule("test", "/dest/path", "포함")

        # 토글
        new_state = self.rule_manager.toggle_rule("test")
        self.assertFalse(new_state)
        self.assertFalse(self.rule_manager.rules["test"]["enabled"])

        # 다시 토글
        new_state = self.rule_manager.toggle_rule("test")
        self.assertTrue(new_state)
        self.assertTrue(self.rule_manager.rules["test"]["enabled"])

    def test_get_active_rules(self):
        """활성화된 규칙만 가져오기 테스트"""
        # 규칙 추가
        self.rule_manager.add_rule("rule1", "/dest1", "포함")
        self.rule_manager.add_rule("rule2", "/dest2", "포함")

        # 하나 비활성화
        self.rule_manager.toggle_rule("rule2")

        # 활성 규칙 가져오기
        active_rules = self.rule_manager.get_active_rules()

        self.assertEqual(len(active_rules), 1)
        self.assertIn("rule1", active_rules)
        self.assertNotIn("rule2", active_rules)

    def test_set_all_rules_enabled(self):
        """모든 규칙 활성화/비활성화 테스트"""
        # 규칙 추가
        self.rule_manager.add_rule("rule1", "/dest1", "포함")
        self.rule_manager.add_rule("rule2", "/dest2", "포함")

        # 모두 비활성화
        self.rule_manager.set_all_rules_enabled(False)
        
        for rule in self.rule_manager.rules.values():
            self.assertFalse(rule["enabled"])

        # 모두 활성화
        self.rule_manager.set_all_rules_enabled(True)
        
        for rule in self.rule_manager.rules.values():
            self.assertTrue(rule["enabled"])


class TestConfigManager(unittest.TestCase):
    """ConfigManager 클래스 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.config_manager = ConfigManager(self.config_file)

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_and_load_config(self):
        """설정 저장 및 로드 테스트"""
        # 테스트 데이터
        test_rules = {
            "rule1": {"dest": "/path1", "match_mode": "포함", "enabled": True},
            "rule2": {"dest": "/path2", "match_mode": "정확히", "enabled": False},
        }

        # 저장
        self.config_manager.save_config(test_rules)

        # 로드
        loaded_rules = self.config_manager.load_config()

        # 검증
        self.assertEqual(loaded_rules, test_rules)

    def test_upgrade_config_format(self):
        """구 버전 설정 형식 업그레이드 테스트"""
        # 구 버전 형식의 설정 파일 생성
        old_format = {"rule1": "/path1", "rule2": "/path2"}

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(old_format, f)

        # 로드 (자동 업그레이드)
        loaded_rules = self.config_manager.load_config()

        # 검증
        self.assertEqual(loaded_rules["rule1"]["dest"], "/path1")
        self.assertEqual(loaded_rules["rule1"]["match_mode"], "포함")
        self.assertTrue(loaded_rules["rule1"]["enabled"])

    def test_backup_config(self):
        """설정 백업 테스트"""
        # 설정 파일 생성
        test_rules = {"rule1": {"dest": "/path1", "match_mode": "포함", "enabled": True}}
        self.config_manager.save_config(test_rules)

        # 백업
        backup_file = self.config_manager.backup_config()

        # 검증
        self.assertIsNotNone(backup_file)
        self.assertTrue(os.path.exists(backup_file))
        self.assertTrue(backup_file.endswith(".backup"))


class TestValidator(unittest.TestCase):
    """Validator 클래스 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.validator = Validator()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_validate_rule_input(self):
        """규칙 입력 검증 테스트"""
        # 정상 입력
        valid, msg = self.validator.validate_rule_input("test", "/path")
        self.assertTrue(valid)

        # 빈 키워드
        valid, msg = self.validator.validate_rule_input("", "/path")
        self.assertFalse(valid)

        # 빈 경로
        valid, msg = self.validator.validate_rule_input("test", "")
        self.assertFalse(valid)

        # 잘못된 문자
        valid, msg = self.validator.validate_rule_input("test/file", "/path")
        self.assertFalse(valid)

    def test_is_valid_regex(self):
        """정규식 검증 테스트"""
        # 유효한 정규식
        self.assertTrue(self.validator.is_valid_regex(r"^\d{4}"))
        self.assertTrue(self.validator.is_valid_regex(r".*\.pdf$"))

        # 잘못된 정규식
        self.assertFalse(self.validator.is_valid_regex(r"["))
        self.assertFalse(self.validator.is_valid_regex(r"(unclosed"))

    def test_validate_before_operation(self):
        """작업 전 환경 검증 테스트"""
        # 규칙 설정
        rules = {"test": {"dest": self.temp_dir, "match_mode": "포함", "enabled": True}}

        # 정상 케이스
        valid, warnings = self.validator.validate_before_operation(
            self.temp_dir, rules, is_copy=False, is_delete=False
        )
        self.assertTrue(valid)
        self.assertEqual(len(warnings), 0)

        # 소스 폴더 없음
        valid, warnings = self.validator.validate_before_operation(
            "/non/existent/path", rules, is_copy=False, is_delete=False
        )
        self.assertFalse(valid)
        self.assertIn("대상 폴더가 존재하지 않습니다.", warnings)


class TestPerformanceUtils(unittest.TestCase):
    """성능 유틸리티 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.cache = FileInfoCache(max_size=10, ttl=1)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_file_info_cache(self):
        """파일 정보 캐시 테스트"""
        # 캐시 저장
        test_info = {"size": 1024, "modified": 12345}
        self.cache.set("/path/to/file", test_info)

        # 캐시 읽기
        cached = self.cache.get("/path/to/file")
        self.assertEqual(cached, test_info)

        # TTL 만료 테스트
        time.sleep(1.1)
        cached = self.cache.get("/path/to/file")
        self.assertIsNone(cached)

    def test_cache_size_limit(self):
        """캐시 크기 제한 테스트"""
        # 최대 크기보다 많은 항목 추가
        for i in range(15):
            self.cache.set(f"/path/{i}", {"size": i})

        # 캐시 크기 확인
        self.assertLessEqual(len(self.cache.cache), 10)

    def test_progress_tracker(self):
        """진행률 추적기 테스트"""
        progress_values = []
        
        def callback(current, total, percent, message):
            progress_values.append(percent)

        tracker = ProgressTracker(100, callback)
        
        # 진행률 업데이트
        for i in range(10):
            tracker.update(10)
            time.sleep(0.02)  # 업데이트 간격 확보

        # 검증
        self.assertTrue(len(progress_values) > 0)
        self.assertLessEqual(progress_values[-1], 100)

    def test_get_optimal_chunk_size(self):
        """최적 청크 크기 계산 테스트"""
        # 작은 파일
        self.assertEqual(get_optimal_chunk_size(5 * 1024 * 1024), 512 * 1024)
        
        # 중간 파일
        self.assertEqual(get_optimal_chunk_size(50 * 1024 * 1024), 1024 * 1024)
        
        # 큰 파일
        self.assertEqual(get_optimal_chunk_size(5 * 1024 * 1024 * 1024), 50 * 1024 * 1024)

    def test_is_network_drive(self):
        """네트워크 드라이브 확인 테스트"""
        # UNC 경로
        self.assertTrue(is_network_drive("\\\\server\\share"))
        self.assertTrue(is_network_drive("//server/share"))
        
        # 로컬 경로
        self.assertFalse(is_network_drive("/home/user"))
        self.assertFalse(is_network_drive("C:\\Users"))


class TestFileMonitor(unittest.TestCase):
    """파일 모니터링 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.events = []
        self.monitor = FileSystemMonitor(
            callback=lambda path, event: self.events.append((path, event))
        )

    def tearDown(self):
        """테스트 후 정리"""
        self.monitor.stop_monitoring()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_file_creation_detection(self):
        """파일 생성 감지 테스트"""
        self.monitor.add_path(self.temp_dir)
        self.monitor.start_monitoring()

        # 파일 생성
        test_file = os.path.join(self.temp_dir, "new_file.txt")
        time.sleep(0.5)  # 모니터링 시작 대기
        
        with open(test_file, "w") as f:
            f.write("test")

        # 이벤트 감지 대기
        time.sleep(3)

        # 검증
        event_types = [e[1] for e in self.events]
        self.assertIn("created", event_types)

    def test_monitor_multiple_paths(self):
        """다중 경로 모니터링 테스트"""
        path1 = os.path.join(self.temp_dir, "dir1")
        path2 = os.path.join(self.temp_dir, "dir2")
        os.makedirs(path1)
        os.makedirs(path2)

        self.monitor.add_path(path1)
        self.monitor.add_path(path2)

        self.assertEqual(len(self.monitor.monitored_paths), 2)

        self.monitor.remove_path(path1)
        self.assertEqual(len(self.monitor.monitored_paths), 1)


class TestAutoOrganizer(unittest.TestCase):
    """자동 파일 정리 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        os.makedirs(self.source_dir)
        os.makedirs(self.dest_dir)

        # 컴포넌트 초기화
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.rule_manager = RuleManager(self.config_file)
        self.log_messages = []
        self.file_processor = FileProcessor(
            log_callback=lambda msg: self.log_messages.append(msg)
        )
        
        self.auto_organizer = AutoOrganizer(
            self.rule_manager, 
            self.file_processor, 
            lambda msg: self.log_messages.append(msg)
        )

    def tearDown(self):
        """테스트 후 정리"""
        self.auto_organizer.stop_auto_organize()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_auto_organize_file(self):
        """자동 파일 정리 테스트"""
        # 규칙 추가
        self.rule_manager.add_rule("test", self.dest_dir, "포함")

        # 자동 정리 시작
        self.auto_organizer.organize_delay = 0.5  # 테스트를 위해 대기 시간 단축
        self.auto_organizer.add_watch_folder(self.source_dir)
        self.auto_organizer.start_auto_organize()

        # 모니터링이 시작되도록 대기
        time.sleep(1)

        # 파일 생성
        test_file = os.path.join(self.source_dir, "test_document.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # 자동 정리가 완료되도록 충분히 대기
        max_wait = 5  # 최대 5초 대기
        wait_interval = 0.5
        elapsed = 0
        
        while os.path.exists(test_file) and elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval

        # 검증
        self.assertFalse(os.path.exists(test_file), "원본 파일이 이동되지 않았습니다")
        self.assertTrue(
            os.path.exists(os.path.join(self.dest_dir, "test_document.txt")),
            "대상 폴더에 파일이 없습니다"
        )

    def test_match_file_methods(self):
        """파일 매칭 메서드 테스트"""
        # 포함
        self.assertTrue(
            self.auto_organizer._match_file("test_document.txt", "doc", "포함")
        )
        
        # 정확히
        self.assertTrue(
            self.auto_organizer._match_file("report.txt", "report", "정확히")
        )
        
        # 시작
        self.assertTrue(
            self.auto_organizer._match_file("report_2025.txt", "report", "시작")
        )
        
        # 끝
        self.assertTrue(
            self.auto_organizer._match_file("annual_report.txt", "report", "끝")
        )
        
        # 정규식
        self.assertTrue(
            self.auto_organizer._match_file("2025_01_report.txt", r"^\d{4}_", "정규식")
        )


class TestBenchmark(unittest.TestCase):
    """벤치마크 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.benchmark = PerformanceBenchmark()

    def test_system_info(self):
        """시스템 정보 수집 테스트"""
        info = self.benchmark.get_system_info()
        
        self.assertIn("os", info)
        self.assertIn("python_version", info)
        self.assertIn("cpu_count", info)

    def test_disk_info(self):
        """디스크 정보 수집 테스트"""
        info = self.benchmark.get_disk_info()
        
        self.assertTrue(len(info) > 0)
        # 적어도 하나의 디스크 정보가 있어야 함

    def test_format_size(self):
        """크기 포맷팅 테스트"""
        self.assertEqual(self.benchmark._format_size(1024), "1.0 KB")
        self.assertEqual(self.benchmark._format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(self.benchmark._format_size(1024 * 1024 * 1024), "1.0 GB")

    def test_estimate_operation_time(self):
        """작업 시간 예측 테스트"""
        file_sizes = [100 * 1024 * 1024, 200 * 1024 * 1024, 50 * 1024 * 1024]
        
        result = self.benchmark.estimate_operation_time(file_sizes, "copy")
        
        self.assertIn("estimated_seconds", result)
        self.assertIn("estimated_time", result)
        self.assertIn("total_size", result)
        self.assertIn("file_count", result)
        self.assertEqual(result["file_count"], 3)

    def test_benchmark_stop(self):
        """벤치마크 중지 테스트"""
        self.benchmark.stop_benchmark()
        self.assertTrue(self.benchmark._stop_flag)


class TestIntegration(unittest.TestCase):
    """통합 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        os.makedirs(self.source_dir)
        os.makedirs(self.dest_dir)

        # 컴포넌트 초기화
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.rule_manager = RuleManager(self.config_file)
        self.file_matcher = FileMatcher()
        self.file_processor = FileProcessor()

    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_workflow(self):
        """전체 워크플로우 테스트"""
        # 1. 테스트 파일 생성
        test_files = [
            "contract_2025.pdf",
            "invoice_ABC.xlsx",
            "report_final.docx",
            "random_file.txt",
        ]

        for filename in test_files:
            filepath = os.path.join(self.source_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"Content of {filename}")

        # 2. 규칙 추가
        self.rule_manager.add_rule("contract", self.dest_dir, "포함")
        self.rule_manager.add_rule("invoice", self.dest_dir, "포함")

        # 3. 활성 규칙 가져오기
        active_rules = self.rule_manager.get_active_rules()

        # 4. 매칭 파일 찾기
        matches = list(
            self.file_matcher.find_matching_files_generator(
                self.source_dir, active_rules, include_subfolders=False
            )
        )

        # 5. 파일 처리
        success_total = 0
        error_total = 0

        if matches:
            success, error = self.file_processor.process_batch(
                matches,
                is_delete=False,
                is_permanent=False,
                is_copy=False,
                operation="이동",
            )
            success_total += success
            error_total += error

        # 6. 검증
        self.assertEqual(len(matches), 2)  # contract와 invoice 파일
        self.assertEqual(success_total, 2)
        self.assertEqual(error_total, 0)

        # 이동된 파일 확인
        self.assertTrue(
            os.path.exists(os.path.join(self.dest_dir, "contract_2025.pdf"))
        )
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "invoice_ABC.xlsx")))

        # 이동되지 않은 파일 확인
        self.assertTrue(
            os.path.exists(os.path.join(self.source_dir, "report_final.docx"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.source_dir, "random_file.txt"))
        )

    def test_complex_rules_workflow(self):
        """복잡한 규칙 워크플로우 테스트"""
        # 1. 여러 대상 폴더 생성
        folders = {
            "documents": os.path.join(self.dest_dir, "documents"),
            "images": os.path.join(self.dest_dir, "images"),
            "archives": os.path.join(self.dest_dir, "archives"),
        }
        
        for folder in folders.values():
            os.makedirs(folder)

        # 2. 다양한 파일 생성
        test_files = {
            "report_2025.pdf": "documents",
            "photo_vacation.jpg": "images",
            "backup_2025.zip": "archives",
            "data.xlsx": "documents",
            "IMG_1234.png": "images",
            "archive_old.rar": "archives",
            "readme.txt": None,  # 매칭 안 됨
        }

        for filename in test_files.keys():
            filepath = os.path.join(self.source_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"Content of {filename}")

        # 3. 다양한 규칙 추가
        self.rule_manager.add_rule("report", folders["documents"], "시작")
        self.rule_manager.add_rule(".pdf", folders["documents"], "끝")
        self.rule_manager.add_rule("IMG_", folders["images"], "시작")
        self.rule_manager.add_rule("photo", folders["images"], "포함")
        self.rule_manager.add_rule(r"\.(zip|rar)$", folders["archives"], "정규식")

        # 4. 매칭 및 처리
        active_rules = self.rule_manager.get_active_rules()
        matches = list(
            self.file_matcher.find_matching_files_generator(
                self.source_dir, active_rules, include_subfolders=False
            )
        )

        success, error = self.file_processor.process_batch(
            matches,
            is_delete=False,
            is_permanent=False,
            is_copy=True,  # 복사 모드
            operation="복사",
        )

        # 5. 검증
        self.assertTrue(
            os.path.exists(os.path.join(folders["documents"], "report_2025.pdf"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(folders["images"], "photo_vacation.jpg"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(folders["images"], "IMG_1234.png"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(folders["archives"], "backup_2025.zip"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(folders["archives"], "archive_old.rar"))
        )
        
        # 원본 파일들은 복사 모드이므로 유지
        for filename in test_files.keys():
            self.assertTrue(
                os.path.exists(os.path.join(self.source_dir, filename))
            )

    def test_performance_with_many_files(self):
        """대량 파일 처리 성능 테스트"""
        # 100개의 테스트 파일 생성
        file_count = 100
        for i in range(file_count):
            filename = f"test_file_{i:03d}.txt"
            filepath = os.path.join(self.source_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"Content {i}")

        # 규칙 추가
        self.rule_manager.add_rule("test", self.dest_dir, "포함")

        # 시간 측정
        start_time = time.time()

        # 파일 매칭
        active_rules = self.rule_manager.get_active_rules()
        matches = list(
            self.file_matcher.find_matching_files_generator(
                self.source_dir, active_rules, include_subfolders=False
            )
        )

        # 파일 처리
        success, error = self.file_processor.process_batch(
            matches,
            is_delete=False,
            is_permanent=False,
            is_copy=False,
            operation="이동",
        )

        elapsed_time = time.time() - start_time

        # 검증
        self.assertEqual(success, file_count)
        self.assertEqual(error, 0)
        self.assertLess(elapsed_time, 10)  # 10초 이내 완료

        # 모든 파일이 이동되었는지 확인
        moved_files = os.listdir(self.dest_dir)
        self.assertEqual(len(moved_files), file_count)


class TestUI(unittest.TestCase):
    """UI 컴포넌트 테스트 (기본적인 테스트만)"""

    def setUp(self):
        """테스트 환경 설정"""
        self.root = tk.Tk()
        self.root.withdraw()  # 테스트 중 윈도우 숨김

    def tearDown(self):
        """테스트 후 정리"""
        try:
            self.root.destroy()
        except:
            pass

    @patch('src.ui.main_window.messagebox')
    @patch('tkinterdnd2.TkinterDnD', tk.Tk)  # TkinterDnD를 일반 Tk로 모킹
    def test_main_window_creation(self, mock_messagebox):
        """메인 윈도우 생성 테스트"""
        from src.ui.main_window import MainWindow
        
        # tkinterdnd2 관련 함수 모킹
        with patch('src.ui.drag_drop_mixin.HAS_DND', False):
            try:
                main_window = MainWindow(self.root)
                self.assertIsNotNone(main_window)
                self.assertIsNotNone(main_window.settings_panel)
                self.assertIsNotNone(main_window.file_list_panel)
                self.assertIsNotNone(main_window.status_panel)
            except Exception as e:
                # 더 자세한 오류 정보를 포함
                import traceback
                self.fail(f"메인 윈도우 생성 실패: {str(e)}\n{traceback.format_exc()}")

    def test_drag_drop_mixin(self):
        """드래그 앤 드롭 Mixin 테스트"""
        from src.ui.drag_drop_mixin import DragDropMixin
        
        # tkinterdnd2가 없는 상황을 시뮬레이션
        with patch('src.ui.drag_drop_mixin.HAS_DND', False):
            class TestWidget(DragDropMixin):
                def __init__(self, root):
                    self.root = root
                    self.string_var = tk.StringVar()
                    self.widget = tk.Label(self.root)
                    
            test_widget = TestWidget(self.root)
            
            # 드래그 앤 드롭 설정 (오류 없이 실행되는지 확인)
            try:
                test_widget.setup_drag_drop(
                    test_widget.widget,
                    test_widget.string_var,
                    accept_folders=True
                )
                # 기본 동작이 설정되었는지 확인
                self.assertTrue(True)  # 오류 없이 실행됨
            except Exception as e:
                self.fail(f"드래그 앤 드롭 설정 실패: {str(e)}")

    def test_drag_drop_frame(self):
        """DragDropFrame 테스트"""
        from src.ui.drag_drop_mixin import DragDropFrame
        
        with patch('src.ui.drag_drop_mixin.HAS_DND', False):
            string_var = tk.StringVar()
            
            # DragDropFrame 생성
            frame = DragDropFrame(self.root, string_var, "테스트 텍스트")
            
            # 기본 요소 확인
            self.assertIsNotNone(frame.frame)
            self.assertIsNotNone(frame.label)
            
            # 경로 설정 테스트
            test_path = "/test/path"
            string_var.set(test_path)
            
            # 라벨이 업데이트되었는지 확인 (콜백 실행 대기)
            self.root.update_idletasks()
            
            # StringVar 값 확인
            self.assertEqual(string_var.get(), test_path)


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 70)
    print("🧪 파일 정리 프로그램 자동 테스트 (최신 버전)")
    print("=" * 70)

    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()

    # 각 테스트 클래스 추가
    test_classes = [
        TestFileMatcher,
        TestFileProcessor,
        TestRuleManager,
        TestConfigManager,
        TestValidator,
        TestPerformanceUtils,
        TestFileMonitor,
        TestAutoOrganizer,
        TestBenchmark,
        TestIntegration,
        TestUI,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 결과 요약
    print("\n" + "=" * 70)
    print("📊 테스트 결과 요약")
    print("=" * 70)
    print(f"✅ 성공: {result.testsRun - len(result.failures) - len(result.errors)}개")
    print(f"❌ 실패: {len(result.failures)}개")
    print(f"⚠️  오류: {len(result.errors)}개")

    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")

    if result.errors:
        print("\n오류 발생 테스트:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 모든 테스트 통과! 프로그램이 정상 작동합니다.")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 확인이 필요합니다.")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    # 간단한 실행 옵션
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # 빠른 테스트 (핵심 기능만)
            suite = unittest.TestSuite()
            suite.addTest(TestFileMatcher("test_match_file_contains"))
            suite.addTest(TestFileProcessor("test_process_batch_move"))
            suite.addTest(TestRuleManager("test_add_rule"))
            suite.addTest(TestValidator("test_validate_rule_input"))
            suite.addTest(TestPerformanceUtils("test_file_info_cache"))
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
        elif sys.argv[1] == "--integration":
            # 통합 테스트만 실행
            suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
        elif sys.argv[1] == "--performance":
            # 성능 관련 테스트만 실행
            suite = unittest.TestSuite()
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPerformanceUtils))
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBenchmark))
            suite.addTest(TestIntegration("test_performance_with_many_files"))
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
        elif sys.argv[1] == "--auto":
            # 자동 정리 기능 테스트만 실행
            suite = unittest.TestSuite()
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileMonitor))
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAutoOrganizer))
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
    else:
        # 전체 테스트 실행
        success = run_all_tests()
        sys.exit(0 if success else 1)
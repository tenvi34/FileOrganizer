#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 정리 프로그램 자동 테스트 (모듈화 버전)
"""

import unittest
import os
import shutil
import tempfile
import json
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
        self.assertTrue(self.matcher.match_file("2025_report.pdf", r"^\d{4}_", "정규식"))
        self.assertFalse(self.matcher.match_file("report_2025.pdf", r"^\d{4}_", "정규식"))
    
    def test_find_matching_files_generator(self):
        """파일 검색 제너레이터 테스트"""
        # 테스트 파일 생성
        test_files = ["doc1.txt", "doc2.pdf", "image.jpg"]
        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("test")
        
        # 규칙 설정
        rules = {
            "doc": {"dest": "/dest", "match_mode": "포함", "enabled": True}
        }
        
        # 매칭 파일 찾기
        matches = list(self.matcher.find_matching_files_generator(
            self.temp_dir, rules, include_subfolders=False
        ))
        
        # 검증
        self.assertEqual(len(matches), 2)  # doc1.txt, doc2.pdf
        matched_names = [os.path.basename(m[0]) for m in matches]
        self.assertIn("doc1.txt", matched_names)
        self.assertIn("doc2.pdf", matched_names)


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
        self.processor = FileProcessor(log_callback=lambda msg: self.log_messages.append(msg))
    
    def tearDown(self):
        """테스트 후 정리"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_process_batch_move(self):
        """파일 이동 테스트"""
        # 테스트 파일 생성
        test_file = os.path.join(self.source_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # 배치 처리
        batch = [(test_file, self.dest_dir, "test", "포함")]
        success, error = self.processor.process_batch(
            batch, is_delete=False, is_permanent=False, 
            is_copy=False, operation="이동"
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
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # 배치 처리
        batch = [(test_file, self.dest_dir, "test", "포함")]
        success, error = self.processor.process_batch(
            batch, is_delete=False, is_permanent=False, 
            is_copy=True, operation="복사"
        )
        
        # 검증
        self.assertEqual(success, 1)
        self.assertEqual(error, 0)
        self.assertTrue(os.path.exists(test_file))  # 원본 유지
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "test.txt")))
    
    def test_duplicate_file_handling(self):
        """중복 파일 처리 테스트"""
        # 같은 이름의 파일 생성
        test_file = os.path.join(self.source_dir, "test.txt")
        existing_file = os.path.join(self.dest_dir, "test.txt")
        
        with open(test_file, 'w') as f:
            f.write("new content")
        with open(existing_file, 'w') as f:
            f.write("existing content")
        
        # 배치 처리
        batch = [(test_file, self.dest_dir, "test", "포함")]
        success, error = self.processor.process_batch(
            batch, is_delete=False, is_permanent=False, 
            is_copy=False, operation="이동"
        )
        
        # 검증
        self.assertEqual(success, 1)
        self.assertEqual(error, 0)
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "test_1.txt")))


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
            "rule2": {"dest": "/path2", "match_mode": "정확히", "enabled": False}
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
        old_format = {
            "rule1": "/path1",
            "rule2": "/path2"
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(old_format, f)
        
        # 로드 (자동 업그레이드)
        loaded_rules = self.config_manager.load_config()
        
        # 검증
        self.assertEqual(loaded_rules["rule1"]["dest"], "/path1")
        self.assertEqual(loaded_rules["rule1"]["match_mode"], "포함")
        self.assertTrue(loaded_rules["rule1"]["enabled"])


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
            "random_file.txt"
        ]
        
        for filename in test_files:
            filepath = os.path.join(self.source_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Content of {filename}")
        
        # 2. 규칙 추가
        self.rule_manager.add_rule("contract", self.dest_dir, "포함")
        self.rule_manager.add_rule("invoice", self.dest_dir, "포함")
        
        # 3. 활성 규칙 가져오기
        active_rules = self.rule_manager.get_active_rules()
        
        # 4. 매칭 파일 찾기
        matches = list(self.file_matcher.find_matching_files_generator(
            self.source_dir, active_rules, include_subfolders=False
        ))
        
        # 5. 파일 처리
        success_total = 0
        error_total = 0
        
        if matches:
            success, error = self.file_processor.process_batch(
                matches, is_delete=False, is_permanent=False,
                is_copy=False, operation="이동"
            )
            success_total += success
            error_total += error
        
        # 6. 검증
        self.assertEqual(len(matches), 2)  # contract와 invoice 파일
        self.assertEqual(success_total, 2)
        self.assertEqual(error_total, 0)
        
        # 이동된 파일 확인
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "contract_2025.pdf")))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "invoice_ABC.xlsx")))
        
        # 이동되지 않은 파일 확인
        self.assertTrue(os.path.exists(os.path.join(self.source_dir, "report_final.docx")))
        self.assertTrue(os.path.exists(os.path.join(self.source_dir, "random_file.txt")))


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 70)
    print("🧪 파일 정리 프로그램 자동 테스트 (모듈화 버전)")
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
        TestIntegration
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
            # 특정 테스트만 실행
            suite = unittest.TestSuite()
            suite.addTest(TestFileMatcher('test_match_file_contains'))
            suite.addTest(TestRuleManager('test_add_rule'))
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
        elif sys.argv[1] == "--integration":
            # 통합 테스트만 실행
            suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
    else:
        # 전체 테스트 실행
        success = run_all_tests()
        sys.exit(0 if success else 1)
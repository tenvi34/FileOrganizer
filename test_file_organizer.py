#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import tempfile
import tkinter as tk
from unittest.mock import patch
import sys

# file_organizer 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from file_organizer import FileOrganizer


class TestFileOrganizer(unittest.TestCase):
    """파일 정리 프로그램 자동 테스트"""

    def setUp(self):
        """각 테스트 전 실행"""
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()  # test_dir → temp_dir로 변경
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir1 = os.path.join(self.temp_dir, "dest1")
        self.dest_dir2 = os.path.join(self.temp_dir, "dest2")

        # 디렉토리 생성
        os.makedirs(self.source_dir)
        os.makedirs(self.dest_dir1)
        os.makedirs(self.dest_dir2)

        # 테스트용 설정 파일 경로
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

        # Tkinter 루트 생성 (테스트용)
        self.root = tk.Tk()
        self.root.withdraw()  # 창 숨기기

        # FileOrganizer 인스턴스 생성
        self.organizer = FileOrganizer(self.root)
        self.organizer.config_file = self.config_file

        # 테스트 폴더 설정
        self.organizer.source_var.set(self.source_dir)

    def tearDown(self):
        """각 테스트 후 정리"""
        # Tkinter 정리
        self.root.quit()
        self.root.destroy()

        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_files(self, files):
        """테스트 파일 생성"""
        created_files = []
        for filename in files:
            filepath = os.path.join(self.source_dir, filename)
            # 하위 폴더가 필요한 경우 생성
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(f"Test content for {filename}")
            created_files.append(filepath)
        return created_files

    def test_01_basic_file_matching(self):
        """기본 파일 매칭 테스트"""
        print("\n✅ Test 1: 기본 파일 매칭")

        # 테스트 파일 생성
        test_files = [
            "계약서_2025.pdf",
            "엑셀파일_ABC.xlsx",
            "보고서_최종.docx",
            "기타문서.txt",
        ]
        self.create_test_files(test_files)

        # 규칙 추가
        self.organizer.rules = {
            "계약서": {"dest": self.dest_dir1, "match_mode": "포함", "enabled": True},
            "엑셀파일": {"dest": self.dest_dir2, "match_mode": "포함", "enabled": True},
        }

        # 매칭 테스트
        matches = list(self.organizer.find_matching_files_generator())

        # 검증
        self.assertEqual(len(matches), 2)
        matched_files = [os.path.basename(m[0]) for m in matches]
        self.assertIn("계약서_2025.pdf", matched_files)
        self.assertIn("엑셀파일_ABC.xlsx", matched_files)
        print(f"  - 매칭된 파일: {matched_files}")

    def test_02_match_modes(self):
        """다양한 매칭 모드 테스트"""
        print("\n✅ Test 2: 매칭 모드 테스트")

        # 테스트 파일 생성
        test_files = [
            "report.pdf",
            "2025_report.pdf",
            "report_2025.pdf",
            "important_report_final.pdf",
            "test.doc",
        ]
        self.create_test_files(test_files)

        # 각 매칭 모드 테스트
        test_cases = [
            ("report", "포함", 4),  # report가 포함된 모든 파일
            ("report", "정확히", 1),  # 정확히 report인 파일
            ("report", "시작", 2),  # report로 시작하는 파일
            ("2025", "끝", 1),  # 2025로 끝나는 파일
            (r"^\d{4}_", "정규식", 1),  # 4자리 숫자로 시작하는 파일
        ]

        for keyword, mode, expected_count in test_cases:
            self.organizer.rules = {
                keyword: {"dest": self.dest_dir1, "match_mode": mode, "enabled": True}
            }
            matches = list(self.organizer.find_matching_files_generator())
            self.assertEqual(
                len(matches),
                expected_count,
                f"매칭 모드 '{mode}'에서 {keyword} 검색 실패",
            )
            print(f"  - {mode} 모드: '{keyword}' → {expected_count}개 매칭")

    def test_03_file_operations(self):
        """파일 이동/복사 테스트"""
        print("\n✅ Test 3: 파일 작업 테스트")

        # 테스트 파일 생성
        test_file = "test_document.pdf"
        self.create_test_files([test_file])

        # 규칙 설정
        self.organizer.rules = {
            "test": {"dest": self.dest_dir1, "match_mode": "포함", "enabled": True}
        }

        # 1. 이동 테스트
        self.organizer.copy_var.set(False)
        with patch.object(self.organizer, "log"):
            self.organizer._process_batch(
                [
                    (
                        os.path.join(self.source_dir, test_file),
                        self.dest_dir1,
                        "test",
                        "포함",
                    )
                ],
                False,
                False,
                False,
                "이동",
            )

        # 파일이 이동되었는지 확인
        self.assertFalse(os.path.exists(os.path.join(self.source_dir, test_file)))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir1, test_file)))
        print("  - 파일 이동: OK")

        # 2. 복사 테스트 준비
        self.create_test_files([test_file])

        # 복사 테스트
        self.organizer.copy_var.set(True)
        with patch.object(self.organizer, "log"):
            self.organizer._process_batch(
                [
                    (
                        os.path.join(self.source_dir, test_file),
                        self.dest_dir2,
                        "test",
                        "포함",
                    )
                ],
                False,
                False,
                True,
                "복사",
            )

        # 파일이 복사되었는지 확인
        self.assertTrue(os.path.exists(os.path.join(self.source_dir, test_file)))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir2, test_file)))
        print("  - 파일 복사: OK")

    def test_04_duplicate_handling(self):
        """중복 파일 처리 테스트"""
        print("\n✅ Test 4: 중복 파일 처리")

        # 같은 이름의 파일 생성
        test_file = "duplicate.txt"
        self.create_test_files([test_file])

        # 대상 폴더에 미리 파일 생성
        existing_file = os.path.join(self.dest_dir1, test_file)
        with open(existing_file, "w") as f:
            f.write("Existing file")

        # 규칙 설정
        self.organizer.rules = {
            "duplicate": {"dest": self.dest_dir1, "match_mode": "포함", "enabled": True}
        }

        # 파일 이동 시도
        with patch.object(self.organizer, "log"):
            self.organizer._process_batch(
                [
                    (
                        os.path.join(self.source_dir, test_file),
                        self.dest_dir1,
                        "duplicate",
                        "포함",
                    )
                ],
                False,
                False,
                False,
                "이동",
            )

        # 중복 파일이 번호가 붙어서 저장되었는지 확인
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir1, "duplicate_1.txt")))
        print("  - 중복 파일 처리: duplicate_1.txt로 저장됨")

    def test_05_subfolder_processing(self):
        """하위 폴더 처리 테스트"""
        print("\n✅ Test 5: 하위 폴더 처리")

        # 하위 폴더에 파일 생성
        subfolder_files = [
            "subfolder1/document.pdf",
            "subfolder1/subfolder2/report.xlsx",
            "root_file.txt",
        ]
        self.create_test_files(subfolder_files)

        # 규칙 설정
        self.organizer.rules = {
            "document": {"dest": self.dest_dir1, "match_mode": "포함", "enabled": True},
            "report": {"dest": self.dest_dir1, "match_mode": "포함", "enabled": True},
        }

        # 하위 폴더 포함 설정
        self.organizer.subfolder_var.set(True)
        matches_with_subfolder = list(self.organizer.find_matching_files_generator())

        # 하위 폴더 제외 설정
        self.organizer.subfolder_var.set(False)
        matches_without_subfolder = list(self.organizer.find_matching_files_generator())

        # 검증
        self.assertEqual(len(matches_with_subfolder), 2)
        self.assertEqual(len(matches_without_subfolder), 0)
        print(f"  - 하위 폴더 포함: {len(matches_with_subfolder)}개")
        print(f"  - 하위 폴더 제외: {len(matches_without_subfolder)}개")

    def test_06_rule_enable_disable(self):
        """규칙 활성화/비활성화 테스트"""
        print("\n✅ Test 6: 규칙 활성화/비활성화")

        # 테스트 파일 생성
        test_files = ["enabled_file.txt", "disabled_file.txt"]
        self.create_test_files(test_files)

        # 규칙 설정 (하나는 활성화, 하나는 비활성화)
        self.organizer.rules = {
            "enabled": {"dest": self.dest_dir1, "match_mode": "포함", "enabled": True},
            "disabled": {
                "dest": self.dest_dir1,
                "match_mode": "포함",
                "enabled": False,
            },
        }

        # 매칭 테스트
        matches = list(self.organizer.find_matching_files_generator())

        # 검증
        self.assertEqual(len(matches), 1)
        self.assertIn("enabled_file.txt", os.path.basename(matches[0][0]))
        print("  - 활성화된 규칙만 적용됨: OK")

    def test_07_config_save_load(self):
        """설정 저장/불러오기 테스트"""
        print("\n✅ Test 7: 설정 저장/불러오기")

        # 테스트 규칙 생성
        test_rules = {
            "test1": {"dest": "/path/to/dest1", "match_mode": "포함", "enabled": True},
            "test2": {
                "dest": "/path/to/dest2",
                "match_mode": "정확히",
                "enabled": False,
            },
        }

        # 규칙 저장
        self.organizer.rules = test_rules
        self.organizer.save_config()

        # 새 인스턴스에서 규칙 불러오기
        new_organizer = FileOrganizer(self.root)
        new_organizer.config_file = self.config_file
        loaded_rules = new_organizer.load_config()

        # 검증
        self.assertEqual(loaded_rules, test_rules)
        print("  - 설정 저장 및 불러오기: OK")

    def test_08_delete_mode(self):
        """삭제 모드 테스트"""
        print("\n✅ Test 8: 삭제 모드")

        # 테스트 파일 생성
        test_file = "delete_test.txt"
        self.create_test_files([test_file])
        file_path = os.path.join(self.source_dir, test_file)

        # 규칙 설정
        self.organizer.rules = {
            "delete": {"dest": self.dest_dir1, "match_mode": "포함", "enabled": True}
        }

        # 영구 삭제 테스트
        self.organizer.delete_var.set(True)
        self.organizer.permanent_delete_var.set(True)

        with patch.object(self.organizer, "log"):
            success, error = self.organizer._process_batch(
                [(file_path, self.dest_dir1, "delete", "포함")],
                True,
                True,
                False,
                "영구 삭제",
            )

        # 파일이 삭제되었는지 확인
        self.assertFalse(os.path.exists(file_path))
        self.assertEqual(success, 1)
        print("  - 영구 삭제: OK")

    def run_all_tests(self):
        """모든 테스트 실행 및 결과 요약"""
        print("=" * 50)
        print("🧪 파일 정리 프로그램 자동 테스트 시작")
        print("=" * 50)

        # 테스트 메서드 목록
        test_methods = [method for method in dir(self) if method.startswith("test_")]

        passed = 0
        failed = 0
        errors = []

        for test_method in sorted(test_methods):
            try:
                # setUp 실행
                self.setUp()

                # 테스트 실행
                getattr(self, test_method)()
                passed += 1

                # tearDown 실행
                self.tearDown()

            except Exception as e:
                failed += 1
                errors.append((test_method, str(e)))
                # tearDown은 항상 실행
                try:
                    self.tearDown()
                except:  # noqa: E722
                    pass

        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 테스트 결과 요약")
        print("=" * 50)
        print(f"✅ 성공: {passed}개")
        print(f"❌ 실패: {failed}개")

        if errors:
            print("\n실패한 테스트:")
            for test_name, error in errors:
                print(f"  - {test_name}: {error}")

        print("\n" + "=" * 50)
        if failed == 0:
            print("🎉 모든 테스트 통과! 프로그램이 정상 작동합니다.")
        else:
            print("⚠️  일부 테스트가 실패했습니다. 확인이 필요합니다.")
        print("=" * 50)


def run_quick_test():
    """빠른 테스트 실행 (GUI 없이)"""
    print("\n🚀 빠른 기능 테스트 실행\n")

    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        source = os.path.join(temp_dir, "source")
        dest = os.path.join(temp_dir, "dest")
        os.makedirs(source)
        os.makedirs(dest)

        # 테스트 파일 생성
        test_files = ["test1.txt", "test2.pdf", "image.jpg"]
        for f in test_files:
            open(os.path.join(source, f), "w").close()

        print("✅ 테스트 환경 생성 완료")
        print(f"   - 소스: {source}")
        print(f"   - 대상: {dest}")
        print(f"   - 파일: {test_files}")

        # 간단한 매칭 테스트
        matches = []
        for f in os.listdir(source):
            if "test" in f.lower():
                matches.append(f)

        print("\n✅ 매칭 테스트: 'test' 키워드")
        print(f"   - 매칭된 파일: {matches}")
        print(f"   - 결과: {'성공' if len(matches) == 2 else '실패'}")

        print("\n테스트 완료!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 빠른 테스트
        run_quick_test()
    else:
        # 전체 테스트
        tester = TestFileOrganizer()

        # Tkinter 관련 설정을 위한 임시 setUp
        tester.setUp()

        try:
            tester.run_all_tests()
        finally:
            # 정리
            try:
                tester.tearDown()
            except:  # noqa: E722
                pass

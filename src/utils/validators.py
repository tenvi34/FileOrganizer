#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
검증 함수들
"""

import os
import shutil
from typing import Tuple, List, Dict


class Validator:
    """검증 클래스"""

    def validate_before_operation(
        self, source: str, rules: Dict, is_copy: bool, is_delete: bool
    ) -> Tuple[bool, List[str]]:
        """작업 전 환경 검증

        Args:
            source: 소스 폴더
            rules: 활성화된 규칙
            is_copy: 복사 모드 여부
            is_delete: 삭제 모드 여부

        Returns:
            (유효성, 경고 메시지 리스트) 튜플
        """
        warnings = []

        # 1. 소스 폴더 검증
        if not source or not os.path.exists(source):
            return False, ["대상 폴더가 존재하지 않습니다."]

        # 2. 규칙 존재 여부
        if not rules:
            return False, ["활성화된 분류 규칙이 없습니다."]

        # 3. 쓰기 권한 검증 (이동/삭제 모드)
        if not is_copy:
            if not self._check_write_permission(source):
                warnings.append(
                    "⚠️ 대상 폴더에 쓰기 권한이 없습니다. 관리자 권한으로 실행하세요."
                )

        # 4. 대상 폴더를 검증 (삭제모드가 아닐 경우)
        if not is_delete:
            invalid_folders = self._validate_destination_folders(rules)
            if invalid_folders:
                warnings.extend(
                    [f"⚠️ 폴더 생성 실패: {folder}" for folder in invalid_folders]
                )

        # 5. 디스크 공간 확인 (복사모드)
        if is_copy:
            space_warning = self._check_disk_space(source)
            if space_warning:
                warnings.append(space_warning)

        return len(warnings) == 0, warnings

    def _check_write_permission(self, folder: str) -> bool:
        """폴더 쓰기 권한 확인

        Args:
            folder: 확인할 폴더

        Returns:
            쓰기 권한 여부
        """
        try:
            test_file = os.path.join(folder, ".write_test_temp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            return True
        except:
            return False

    def _validate_destination_folders(self, rules: Dict) -> List[str]:
        """대상 폴더 유효성 검증

        Args:
            rules: 규칙 딕셔너리

        Returns:
            생성 실패한 폴더 리스트
        """
        invalid_folders = []

        for keyword, rule_data in rules.items():
            if isinstance(rule_data, dict):
                dest = rule_data.get("dest", "")
                if dest and not os.path.exists(dest):
                    try:
                        os.makedirs(dest)
                    except Exception:
                        invalid_folders.append(dest)

        return invalid_folders

    def _check_disk_space(self, source: str) -> str:
        """디스크 공간 확인

        Args:
            source: 소스 폴더

        Returns:
            경고 메시지 (문제없으면 None)
        """
        try:
            # 간단한 추정 (실제 매칭 파일 크기를 계산하려면 더 복잡함)
            total_size = 0
            for root, dirs, files in os.walk(source):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        pass

            free_space = shutil.disk_usage(source).free

            # 여유 공간이 필요 공간의 110% 미만이면 경고
            if total_size > free_space * 0.9:
                size_mb = total_size // 1024 // 1024
                free_mb = free_space // 1024 // 1024
                return (
                    f"⚠️ 디스크 공간 부족 가능성 (필요: {size_mb}MB, 여유: {free_mb}MB)"
                )
        except:
            pass

        return None

    def validate_rule_input(self, keyword: str, dest: str) -> Tuple[bool, str]:
        """규칙 입력 검증

        Args:
            keyword: 키워드
            dest: 대상 폴더

        Returns:
            (유효성, 에러 메시지) 튜플
        """
        if not keyword or not keyword.strip():
            return False, "키워드를 입력하세요."

        if not dest or not dest.strip():
            return False, "대상 폴더를 입력하세요."

        # 키워드에 사용할 수 없는 문자 확인
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        for char in invalid_chars:
            if char in keyword:
                return False, f"키워드에 '{char}' 문자를 사용할 수 없습니다."

        return True, ""

    def is_valid_regex(self, pattern: str) -> bool:
        """정규식 유효성 검증

        Args:
            pattern: 정규식 패턴

        Returns:
            유효성 여부
        """
        import re

        try:
            re.compile(pattern)
            return True
        except re.error:
            return False

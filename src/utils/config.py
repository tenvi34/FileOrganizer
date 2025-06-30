#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
설정 파일 관리
"""
import json
import os
from typing import Dict, Any


class ConfigManager:
    """설정 파일 관리 클래스"""

    def __init__(self, config_file: str = "file_organizer_config.json"):
        """초기화

        Args:
            config_file: 설정 파일 경로
        """
        self.config_file = config_file

    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드

        Returns:
            설정 딕셔너리
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 데이터 형식 업그레이드
                    return self._upgrade_config_format(data)
            except Exception as e:
                print(f"설정 파일 로드 중 오류: {str(e)}")
        return {}

    def save_config(self, rules: Dict[str, Any]):
        """설정 파일 저장

        Args:
            rules: 저장할 규칙 딕셔너리
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(rules, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 파일 저장 중 오류: {str(e)}")

    def _upgrade_config_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """이전 버전 설정 형식 업그레이드

        Args:
            data: 원본 설정 데이터

        Returns:
            업그레이드된 설정 데이터
        """
        upgraded_data = {}

        for key, value in data.items():
            if isinstance(value, str):
                # 기존 형식: {"keyword": "dest_path"}를
                # 새 형식으로 변환: {"keyword": {"dest": "path", "match_mode": "포함", "enabled": true}}
                upgraded_data[key] = {
                    "dest": value,
                    "match_mode": "포함",
                    "enabled": True,
                }
            else:
                # 이미 새 형식인 경우
                upgraded_data[key] = value

        return upgraded_data

    def backup_config(self):
        """설정 파일 백업"""
        if os.path.exists(self.config_file):
            backup_file = f"{self.config_file}.backup"
            try:
                import shutil

                shutil.copy2(self.config_file, backup_file)
                return backup_file
            except Exception as e:
                print(f"설정 파일 백업 중 오류: {str(e)}")
        return None

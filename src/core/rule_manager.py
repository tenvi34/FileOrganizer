#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
규칙 관리 로직
"""

from typing import Dict, List, Tuple
from src.utils.config import ConfigManager

class RuleManager:
    """규칙 관리 클래스"""
    
    def __init__(self, config_file: str = None):
        """초기화
        
        Args:
            config_file: 설정 파일 경로
        """
        self.config_manager = ConfigManager(config_file)
        self.rules = self.config_manager.load_config()
        
    def add_rule(self, keyword: str, dest: str, match_mode: str = "포함") -> bool:
        """규칙 추가
        
        Args:
            keyword: 키워드
            dest: 대상 폴더
            match_mode: 매칭 모드
            
        Returns:
            성공 여부
        """
        if not keyword or not dest:
            return False
        
        self.rules[keyword] = {
            "dest": dest,
            "match_mode": match_mode,
            "enabled": True
        }
        self.save_rules()
        return True
    
    def delete_rule(self, keyword: str) -> bool:
        """규칙 삭제
        
        Args:
            keyword: 삭제할 키워드
            
        Returns:
            성공 여부
        """
        if keyword in self.rules:
            del self.rules[keyword]
            self.save_rules()
            return True
        return False
    
    def toggle_rule(self, keyword: str) -> bool:
        """규칙 활성화/비활성화 토글
        
        Args:
            keyword: 토글할 키워드
            
        Returns:
            현재 활성화 상태
        """
        if keyword in self.rules:
            current = self.rules[keyword].get("enabled", True)
            self.rules[keyword]["enabled"] = not current
            self.save_rules()
            return self.rules[keyword]["enabled"]
        return False
    
    def set_all_rules_enabled(self, enabled: bool):
        """모든 규칙 활성화/비활성화
        
        Args:
            enabled: 활성화 여부
        """
        for keyword in self.rules:
            self.rules[keyword]["enabled"] = enabled
        self.save_rules()
    
    def toggle_all_rules(self):
        """모든 규칙 선택 반전"""
        for keyword in self.rules:
            current = self.rules[keyword].get("enabled", True)
            self.rules[keyword]["enabled"] = not current
        self.save_rules()
    
    def get_active_rules(self) -> Dict:
        """활성화된 규칙만 반환
        
        Returns:
            활성화된 규칙 딕셔너리
        """
        return {
            k: v
            for k, v in self.rules.items()
            if isinstance(v, dict) and v.get("enabled", True)
        }
    
    def get_rules_list(self) -> List[Tuple[str, Dict]]:
        """규칙 리스트 반환
        
        Returns:
            [(키워드, 규칙데이터)] 리스트
        """
        return list(self.rules.items())
    
    def save_rules(self):
        """규칙 저장"""
        self.config_manager.save_config(self.rules)
    
    def reload_rules(self):
        """규칙 다시 로드"""
        self.rules = self.config_manager.load_config()
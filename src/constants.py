#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 자동 분류 프로그램
상수 정의
"""

# 애플리케이션 정보
APP_TITLE = "파일 자동 분류 프로그램"
APP_VERSION = "1.2.1"
WINDOW_SIZE = "1000x850"

# 파일 관련
CONFIG_FILE = "config/file_organizer_config.json"
LOG_DIR = "logs"

# 매칭 옵션
MATCH_MODES = ["포함", "정확히", "시작", "끝", "정규식"]
DEFAULT_MATCH_MODE = "포함"

# 배치 처리
BATCH_SIZE = 100
UI_UPDATE_INTERVAL = 0.1  # 초

# 파일 미리보기 제한
PREVIEW_LIMIT = 100

# Windows 파일 속성
if hasattr(__builtins__, "WindowsError"):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    FILE_ATTRIBUTE_SYSTEM = 0x04
else:
    FILE_ATTRIBUTE_HIDDEN = None
    FILE_ATTRIBUTE_SYSTEM = None
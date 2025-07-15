#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
파일 자동 분류 프로그램
상수 정의
"""

# 애플리케이션 정보
APP_TITLE = "파일 자동 분류 프로그램"
APP_VERSION = "2.1.3"
WINDOW_SIZE = "1400x800"
MAC_SIZE = "1200x700"

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

# 성능 관련 설정
SCAN_BATCH_SIZE = 100  # 파일 스캔 배치 크기
PROCESS_BATCH_SIZE = 10  # 파일 처리 배치 크기
CACHE_SIZE = 5000  # 파일 정보 캐시 크기
CACHE_TTL = 60  # 캐시 유효 시간 (초)
LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  # 대용량 파일 기준 (50MB)
PROGRESS_UPDATE_INTERVAL = 0.1  # 진행률 업데이트 간격 (초)

# 고급 성능 설정
ADVANCED_SETTINGS = {
    # 멀티스레드 설정
    "multithread_copy": True,
    "thread_count": 4,
    "multithread_threshold": 1024 * 1024 * 1024,  # 1GB
    # 캐시 설정
    "cache_size": 5000,
    "cache_ttl": 60,
    # 배치 처리 설정
    "scan_batch_size": 100,
    "process_batch_size": 10,
    # 검증 설정
    "verify_copy": True,
    "verify_method": "quick",  # 'quick' or 'full'
    "verify_threshold": 100 * 1024 * 1024,  # 100MB
    "verify_fail_action": "retry",  # 'retry', 'skip', 'abort'
    # 네트워크 설정
    "network_optimize": True,
    "network_chunk_size": 50 * 1024 * 1024,  # 50MB
    "network_timeout": 120,
    # 청크 크기 (파일 크기별)
    "chunk_sizes": {
        "tiny": 512 * 1024,  # < 10MB
        "small": 1024 * 1024,  # < 100MB
        "medium": 10 * 1024 * 1024,  # < 1GB
        "large": 50 * 1024 * 1024,  # < 10GB
        "huge": 100 * 1024 * 1024,  # >= 10GB
    },
}

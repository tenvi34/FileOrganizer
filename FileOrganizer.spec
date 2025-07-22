# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for FileOrganizer

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 데이터 파일 수집
datas = [
    ('src', 'src'),
    ('config', 'config'),
]

# 아이콘 파일이 있는 경우
if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

# hidden imports 정의
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinterdnd2',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'psutil',
    'send2trash',
    'json',
    'threading',
    'concurrent.futures',
    'datetime',
    'tempfile',
    'shutil',
    'pathlib',
    'platform',
    'mimetypes',
    'hashlib',
    're',
    'time',
    'os',
    'sys',
]

# tkinterdnd2 관련 데이터 수집
tkdnd_datas = collect_data_files('tkinterdnd2')
datas.extend(tkdnd_datas)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 플랫폼별 설정
if sys.platform == 'win32':
    icon = 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None
elif sys.platform == 'darwin':
    icon = 'assets/icon.icns' if os.path.exists('assets/icon.icns') else None
else:
    icon = 'assets/icon.png' if os.path.exists('assets/icon.png') else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileOrganizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX 사용 안함 (noupx)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 콘솔 창 숨김 (windowed)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

# macOS용 앱 번들 생성
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='FileOrganizer.app',
        icon=icon,
        bundle_identifier='com.fileorganizer.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'CFBundleShortVersionString': '2.1.5',
            'CFBundleName': 'FileOrganizer',
            'CFBundleDisplayName': '파일 자동 분류 프로그램',
            'NSRequiresAquaSystemAppearance': 'False',  # 다크 모드 지원
        },
    )
# src/utils/icon_manager.py (새 파일)
import os
import tkinter as tk
from PIL import Image, ImageTk
import mimetypes


class IconManager:
    """파일 아이콘 관리 클래스"""

    def __init__(self, icon_dir="assets/icons", size=(16, 16)):
        self.icon_dir = icon_dir
        self.size = size
        self.icons = {}
        self.default_icon = None
        self._load_icons()

    def _load_icons(self):
        """아이콘 로드"""
        icon_mappings = {
            "folder": ["folder.png"],
            "image": ["jpg", "jpeg", "png", "gif", "bmp", "ico", "svg"],
            "document": ["doc", "docx", "odt"],
            "spreadsheet": ["xls", "xlsx", "csv"],
            "presentation": ["ppt", "pptx"],
            "pdf": ["pdf"],
            "text": ["txt", "log", "md"],
            "code": ["py", "js", "html", "css", "java", "cpp", "c"],
            "archive": ["zip", "rar", "7z", "tar", "gz"],
            "audio": ["mp3", "wav", "flac", "aac"],
            "video": ["mp4", "avi", "mkv", "mov", "wmv"],
            "executable": ["exe", "app", "deb", "dmg"],
        }

        # 기본 아이콘 로드
        default_path = os.path.join(self.icon_dir, "file.png")
        if os.path.exists(default_path):
            self.default_icon = self._load_and_resize(default_path)

        # 각 타입별 아이콘 로드
        for icon_type, extensions in icon_mappings.items():
            icon_path = os.path.join(self.icon_dir, f"{icon_type}.png")
            if os.path.exists(icon_path):
                icon = self._load_and_resize(icon_path)
                if isinstance(extensions[0], str) and "." not in extensions[0]:
                    # 확장자 리스트인 경우
                    for ext in extensions:
                        self.icons[ext.lower()] = icon
                else:
                    # 단일 아이콘 타입
                    self.icons[icon_type] = icon

    def _load_and_resize(self, path):
        """이미지 로드 및 리사이즈"""
        try:
            image = Image.open(path)
            image = image.resize(self.size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"아이콘 로드 실패: {path} - {e}")
            return None

    def get_icon(self, filename):
        """파일명에 맞는 아이콘 반환"""
        # 확장자 추출
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip(".")

        # 확장자에 맞는 아이콘 반환
        if ext in self.icons:
            return self.icons[ext]

        # MIME 타입으로 판단
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            if mime_type.startswith("image/"):
                return self.icons.get("image", self.default_icon)
            elif mime_type.startswith("audio/"):
                return self.icons.get("audio", self.default_icon)
            elif mime_type.startswith("video/"):
                return self.icons.get("video", self.default_icon)

        return self.default_icon

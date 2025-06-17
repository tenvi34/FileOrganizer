import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import json
from datetime import datetime
import threading


class FileOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("파일 자동 분류 프로그램")
        self.root.geometry("800x600")

        # 설정 파일 경로
        self.config_file = "file_organizer_config.json"
        self.rules = self.load_config()

        # UI 설정
        self.setup_ui()

    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 소스 폴더 선택
        ttk.Label(main_frame, text="대상 폴더:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.source_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="폴더 선택", command=self.select_source_folder).grid(row=0, column=2)
        
        # 규칙 추가 섹션
        rule_frame = ttk.LabelFrame(main_frame, text="분류 규칙", padding="10")
        rule_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(rule_frame, text="키워드:").grid(row=0, column=0, sticky=tk.W)
        self.keyword_var = tk.StringVar()
        ttk.Entry(rule_frame, textvariable=self.keyword_var, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(rule_frame, text="이동할 폴더:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.dest_var = tk.StringVar()
        ttk.Entry(rule_frame, textvariable=self.dest_var, width=30).grid(row=0, column=3, padx=5)
        ttk.Button(rule_frame, text="폴더 선택", command=self.select_dest_folder).grid(row=0, column=4)
        
        ttk.Button(rule_frame, text="규칙 추가", command=self.add_rule).grid(row=0, column=5, padx=10)
        
        # 규칙 목록
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # 트리뷰로 규칙 표시
        self.tree = ttk.Treeview(list_frame, columns=('키워드', '대상 폴더'), show='tree headings', height=10)
        self.tree.heading('#0', text='번호')
        self.tree.heading('키워드', text='키워드')
        self.tree.heading('대상 폴더', text='대상 폴더')
        
        self.tree.column('#0', width=50)
        self.tree.column('키워드', width=150)
        self.tree.column('대상 폴더', width=400)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 규칙 삭제 버튼
        ttk.Button(main_frame, text="선택한 규칙 삭제", command=self.delete_rule).grid(row=3, column=0, columnspan=3, pady=5)
        
        # 옵션
        option_frame = ttk.LabelFrame(main_frame, text="옵션", padding="10")
        option_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.subfolder_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="하위 폴더 포함", variable=self.subfolder_var).grid(row=0, column=0, sticky=tk.W)
        
        self.copy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(option_frame, text="복사 (체크 안하면 이동)", variable=self.copy_var).grid(row=0, column=1, sticky=tk.W, padx=20)
        
        # 실행 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="파일 정리 시작", command=self.organize_files, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="미리보기", command=self.preview_files).pack(side=tk.LEFT, padx=5)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=70)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # 저장된 규칙 로드
        self.update_rule_list()
        
    def select_source_folder(self):
        folder = filedialog.askdirectory(title="대상 폴더 선택")
        if folder:
            self.source_var.set(folder)
            
    def select_dest_folder(self):
        folder = filedialog.askdirectory(title="이동할 폴더 선택")
        if folder:
            self.dest_var.set(folder)
            
    def add_rule(self):
        keyword = self.keyword_var.get().strip()
        dest = self.dest_var.get().strip()
        
        if not keyword or not dest:
            messagebox.showwarning("경고", "키워드와 대상 폴더를 모두 입력하세요.")
            return
            
        # 규칙 추가
        self.rules[keyword] = dest
        self.save_config()
        self.update_rule_list()
        
        # 입력 필드 초기화
        self.keyword_var.set("")
        self.dest_var.set("")
        
        self.log(f"규칙 추가: '{keyword}' → '{dest}'")
        
    def delete_rule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 규칙을 선택하세요.")
            return
            
        item = self.tree.item(selected[0])
        keyword = item['values'][0]
        
        if messagebox.askyesno("확인", f"'{keyword}' 규칙을 삭제하시겠습니까?"):
            del self.rules[keyword]
            self.save_config()
            self.update_rule_list()
            self.log(f"규칙 삭제: '{keyword}'")
            
    def update_rule_list(self):
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 규칙 추가
        for i, (keyword, dest) in enumerate(self.rules.items(), 1):
            self.tree.insert('', 'end', text=str(i), values=(keyword, dest))
            
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)
            
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def find_matching_files(self, preview=False):
        source = self.source_var.get()
        if not source or not os.path.exists(source):
            messagebox.showerror("오류", "유효한 대상 폴더를 선택하세요.")
            return []
            
        if not self.rules:
            messagebox.showwarning("경고", "분류 규칙이 없습니다.")
            return []
            
        matches = []
        include_subfolders = self.subfolder_var.get()
        
        # 파일 검색
        if include_subfolders:
            for root, dirs, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    for keyword, dest in self.rules.items():
                        if keyword.lower() in file.lower():
                            matches.append((file_path, dest, keyword))
                            if preview:
                                self.log(f"매칭: {file} → {dest} (키워드: {keyword})")
                            break
        else:
            for file in os.listdir(source):
                file_path = os.path.join(source, file)
                if os.path.isfile(file_path):
                    for keyword, dest in self.rules.items():
                        if keyword.lower() in file.lower():
                            matches.append((file_path, dest, keyword))
                            if preview:
                                self.log(f"매칭: {file} → {dest} (키워드: {keyword})")
                            break
                            
        return matches
        
    def preview_files(self):
        self.log_text.delete(1.0, tk.END)
        self.log("=== 미리보기 시작 ===")
        
        matches = self.find_matching_files(preview=True)
        
        if matches:
            self.log(f"\n총 {len(matches)}개 파일이 이동될 예정입니다.")
        else:
            self.log("\n매칭되는 파일이 없습니다.")
            
        self.log("=== 미리보기 종료 ===\n")
        
    def organize_files(self):
        if messagebox.askyesno("확인", "파일 정리를 시작하시겠습니까?"):
            # 별도 스레드에서 실행
            thread = threading.Thread(target=self._organize_files_thread)
            thread.start()
            
    def _organize_files_thread(self):
        self.log_text.delete(1.0, tk.END)
        self.log("=== 파일 정리 시작 ===")
        
        matches = self.find_matching_files()
        is_copy = self.copy_var.get()
        operation = "복사" if is_copy else "이동"
        
        success_count = 0
        error_count = 0
        
        for file_path, dest_folder, keyword in matches:
            try:
                # 대상 폴더가 없으면 생성
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                    self.log(f"폴더 생성: {dest_folder}")
                    
                # 파일명 추출
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(dest_folder, file_name)
                
                # 동일한 파일명이 있을 경우 처리
                if os.path.exists(dest_path):
                    base_name, ext = os.path.splitext(file_name)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_name = f"{base_name}_{counter}{ext}"
                        dest_path = os.path.join(dest_folder, new_name)
                        counter += 1
                        
                # 파일 복사 또는 이동
                if is_copy:
                    shutil.copy2(file_path, dest_path)
                else:
                    shutil.move(file_path, dest_path)
                    
                self.log(f"{operation} 완료: {file_name} → {dest_folder}")
                success_count += 1
                
            except Exception as e:
                self.log(f"오류 발생: {file_name} - {str(e)}")
                error_count += 1
                
        self.log(f"\n=== 작업 완료 ===")
        self.log(f"성공: {success_count}개 파일")
        self.log(f"실패: {error_count}개 파일")
        
        # 메인 스레드에서 메시지박스 표시
        self.root.after(0, lambda: messagebox.showinfo("완료", 
            f"파일 정리가 완료되었습니다.\n\n성공: {success_count}개\n실패: {error_count}개"))

def main():
    root = tk.Tk()
    app = FileOrganizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
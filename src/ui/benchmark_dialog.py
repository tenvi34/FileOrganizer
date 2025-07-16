#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
벤치마크 실행 다이얼로그
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import platform
import threading
from datetime import datetime
from src.utils.benchmark import PerformanceBenchmark
from src.ui.progress_dialog import ProgressDialog


class BenchmarkDialog(tk.Toplevel):
    """벤치마크 실행 다이얼로그"""

    def __init__(self, parent, apply_callback=None):
        """초기화

        Args:
            parent: 부모 윈도우
            apply_callback: 설정 적용 콜백
        """
        super().__init__(parent)
        self.title("성능 테스트")
        self.geometry("700x800")
        self.resizable(False, False)

        # 모달 다이얼로그
        self.transient(parent)
        self.grab_set()

        self.apply_callback = apply_callback
        self.benchmark = None
        self.results = None
        self.benchmark_thread = None

        self.create_widgets()

        # 중앙 배치
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 350
        y = (self.winfo_screenheight() // 2) - 300
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 설명
        info_frame = ttk.LabelFrame(main_frame, text="성능 테스트 정보", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = """이 테스트는 시스템의 파일 처리 성능을 측정합니다.
테스트 항목:
• 순차 읽기/쓰기 속도
• 랜덤 I/O 성능 (IOPS)
• 파일 복사 속도 (단일/멀티스레드)

테스트는 임시 파일을 생성하며, 완료 후 자동으로 삭제됩니다.
약 1-5분 정도 소요됩니다."""

        ttk.Label(info_frame, text=info_text, wraplength=650).pack()

        # 테스트 옵션
        option_frame = ttk.LabelFrame(main_frame, text="테스트 옵션", padding="10")
        option_frame.pack(fill=tk.X, pady=(0, 10))

        self.quick_test_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(
            option_frame,
            text="빠른 테스트 (작은 파일로 빠르게 테스트)",
            variable=self.quick_test_var,
            value=True,
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            option_frame,
            text="전체 테스트 (큰 파일 포함, 정확한 측정)",
            variable=self.quick_test_var,
            value=False,
        ).pack(anchor=tk.W, pady=(5, 0))

        # 결과 표시 영역
        result_frame = ttk.LabelFrame(main_frame, text="테스트 결과", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 결과 텍스트 위젯
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        if platform.system() == "Windows":
            result_font = ("Consolas", 9)
        elif platform.system() == "Darwin":  # macOS
            result_font = ("Monaco", 9)
        else:  # Linux
            result_font = ("Courier New", 9)

        self.result_text = tk.Text(
            text_frame, wrap=tk.WORD, height=20, font=result_font
        )

        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 초기 메시지
        self.result_text.insert(
            tk.END, "테스트를 시작하려면 '테스트 시작' 버튼을 클릭하세요.\n"
        )
        self.result_text.config(state=tk.DISABLED)

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(
            button_frame, text="테스트 시작", command=self.start_benchmark
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.apply_button = ttk.Button(
            button_frame,
            text="권장 설정 적용",
            command=self.apply_recommendations,
            state=tk.DISABLED,
        )
        self.apply_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(
            button_frame, text="결과 저장", command=self.save_results, state=tk.DISABLED
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="닫기", command=self.close).pack(
            side=tk.RIGHT, padx=5
        )

    def start_benchmark(self):
        """벤치마크 시작"""
        self.start_button.config(state=tk.DISABLED)
        self.apply_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)

        # 결과 텍스트 초기화
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "벤치마크를 시작합니다...\n\n")
        self.result_text.config(state=tk.DISABLED)

        # 진행률 다이얼로그
        self.progress_dialog = ProgressDialog(
            self, title="성능 테스트 진행 중", can_cancel=True
        )

        # 벤치마크 객체 생성
        self.benchmark = PerformanceBenchmark(log_callback=self.log_message)

        # 백그라운드 스레드에서 실행
        self.benchmark_thread = threading.Thread(
            target=self.run_benchmark_thread, daemon=True
        )
        self.benchmark_thread.start()

    def run_benchmark_thread(self):
        """벤치마크 실행 스레드"""
        try:
            # 진행률 콜백
            def progress_callback(current, total, message):
                if self.progress_dialog.cancelled:
                    self.benchmark.stop_benchmark()
                    return

                self.after(
                    0, self.progress_dialog.update_progress, current, total, message, ""
                )

            # 벤치마크 실행
            self.results = self.benchmark.run_complete_benchmark(progress_callback)

            # 결과 표시
            self.after(0, self.show_results)

        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
        finally:
            self.after(0, self.benchmark_complete)

    def log_message(self, message):
        """로그 메시지 추가"""
        self.after(0, lambda: self._append_text(f"• {message}\n"))

    def _append_text(self, text):
        """텍스트 추가"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def show_results(self):
        """벤치마크 결과 표시"""
        if not self.results:
            return

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        # 타이틀
        self.result_text.insert(tk.END, "=" * 60 + "\n")
        self.result_text.insert(tk.END, "📊 성능 테스트 결과\n")
        self.result_text.insert(tk.END, "=" * 60 + "\n\n")

        # 시스템 정보
        self.result_text.insert(tk.END, "🖥️ 시스템 정보\n")
        self.result_text.insert(tk.END, "-" * 40 + "\n")
        for key, value in self.results["system_info"].items():
            self.result_text.insert(tk.END, f"• {key}: {value}\n")
        self.result_text.insert(tk.END, "\n")

        # 디스크 정보
        self.result_text.insert(tk.END, "💾 디스크 정보\n")
        self.result_text.insert(tk.END, "-" * 40 + "\n")
        for device, info in self.results["disk_info"].items():
            self.result_text.insert(tk.END, f"• {device}:\n")
            for key, value in info.items():
                self.result_text.insert(tk.END, f"  - {key}: {value}\n")
        self.result_text.insert(tk.END, "\n")

        # I/O 테스트 결과
        if "io_tests" in self.results:
            self.result_text.insert(tk.END, "⚡ I/O 성능\n")
            self.result_text.insert(tk.END, "-" * 40 + "\n")

            if "sequential" in self.results["io_tests"]:
                seq = self.results["io_tests"]["sequential"]
                self.result_text.insert(tk.END, "순차 I/O:\n")
                self.result_text.insert(
                    tk.END, f"  • 읽기: {seq.get('read_speed', 0):.1f} MB/s\n"
                )
                self.result_text.insert(
                    tk.END, f"  • 쓰기: {seq.get('write_speed', 0):.1f} MB/s\n"
                )

            if "random" in self.results["io_tests"]:
                rand = self.results["io_tests"]["random"]
                self.result_text.insert(tk.END, f"랜덤 I/O:\n")
                self.result_text.insert(
                    tk.END, f"  • 읽기: {rand.get('random_read_iops', 0):.0f} IOPS\n"
                )

            self.result_text.insert(tk.END, "\n")

        # 복사 테스트 결과
        if "copy_tests" in self.results and self.results["copy_tests"]:
            self.result_text.insert(tk.END, "📁 파일 복사 성능\n")
            self.result_text.insert(tk.END, "-" * 40 + "\n")

            for size, data in self.results["copy_tests"].items():
                self.result_text.insert(tk.END, f"\n파일 크기: {size}\n")

                if "single_thread" in data:
                    single = data["single_thread"]
                    self.result_text.insert(
                        tk.END, f"  • 단일 스레드: {single['speed']:.1f} MB/s "
                    )
                    self.result_text.insert(tk.END, f"({single['time']:.2f}초)\n")

                if "multi_thread" in data:
                    multi = data["multi_thread"]
                    self.result_text.insert(
                        tk.END, f"  • 멀티 스레드: {multi['speed']:.1f} MB/s "
                    )
                    self.result_text.insert(tk.END, f"({multi['time']:.2f}초)\n")

                    if "improvement" in data:
                        self.result_text.insert(
                            tk.END, f"  • 성능 향상: {data['improvement']:.1f}%\n"
                        )

            self.result_text.insert(tk.END, "\n")

        # 권장사항
        if "recommendations" in self.results:
            rec = self.results["recommendations"]
            self.result_text.insert(tk.END, "💡 분석 및 권장사항\n")
            self.result_text.insert(tk.END, "-" * 40 + "\n")
            self.result_text.insert(
                tk.END, f"스토리지 타입: {rec.get('storage_type', 'Unknown')}\n"
            )
            self.result_text.insert(
                tk.END, f"성능 수준: {rec.get('performance_level', 'Unknown')}\n"
            )

            if "settings" in rec:
                self.result_text.insert(tk.END, "\n권장 설정:\n")
                for key, value in rec["settings"].items():
                    self.result_text.insert(tk.END, f"  • {key}: {value}\n")

        self.result_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.result_text.insert(
            tk.END, "테스트 완료 시간: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        self.result_text.config(state=tk.DISABLED)

    def show_error(self, error_message):
        """에러 표시"""
        self._append_text(f"\n❌ 오류 발생: {error_message}\n")
        messagebox.showerror(
            "오류", f"벤치마크 실행 중 오류가 발생했습니다:\n{error_message}"
        )

    def benchmark_complete(self):
        """벤치마크 완료"""
        if hasattr(self, "progress_dialog") and self.progress_dialog:
            self.progress_dialog.close()

        self.start_button.config(state=tk.NORMAL)

        if self.results and "recommendations" in self.results:
            self.apply_button.config(state=tk.NORMAL)

        self.save_button.config(state=tk.NORMAL)

    def apply_recommendations(self):
        """권장 설정 적용"""
        if not self.results or "recommendations" not in self.results:
            return

        settings = self.results["recommendations"].get("settings", {})

        if messagebox.askyesno(
            "설정 적용",
            "벤치마크 결과에 따른 권장 설정을 적용하시겠습니까?\n\n"
            "현재 설정이 변경됩니다.",
        ):
            if self.apply_callback:
                self.apply_callback(settings)
                messagebox.showinfo("완료", "권장 설정이 적용되었습니다.")
            else:
                messagebox.showwarning("경고", "설정 적용 기능이 연결되지 않았습니다.")

    def save_results(self):
        """결과 저장"""
        if not self.results:
            return

        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("텍스트 파일", "*.txt"),
                ("JSON 파일", "*.json"),
                ("모든 파일", "*.*"),
            ],
            initialfile=f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )

        if filename:
            try:
                if filename.endswith(".json"):
                    # JSON 형식으로 저장
                    import json

                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(self.results, f, ensure_ascii=False, indent=2)
                else:
                    # 텍스트 형식으로 저장
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.result_text.get(1.0, tk.END))

                messagebox.showinfo("저장 완료", f"결과가 저장되었습니다:\n{filename}")
            except Exception as e:
                messagebox.showerror(
                    "저장 실패", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}"
                )

    def close(self):
        """다이얼로그 닫기"""
        # 실행 중인 벤치마크 중지
        if self.benchmark:
            self.benchmark.stop_benchmark()

        # 스레드 종료 대기
        if self.benchmark_thread and self.benchmark_thread.is_alive():
            self.benchmark_thread.join(timeout=1.0)

        self.destroy()

import os
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .constants import APP_TITLE, DEFAULT_OUTPUT_DIR, SUPPORTED_AUDIO
from .core import describe_audio_paths, is_supported_audio, parse_audio_paths_text, transcribe_batch

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("780x560")
        self.minsize(720, 500)
        self.log_queue: "queue.Queue[str]" = queue.Queue()
        self.worker: Optional[threading.Thread] = None
        self.selected_audio_paths: List[Path] = []

        self.audio_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(DEFAULT_OUTPUT_DIR))
        self.model_var = tk.StringVar(value="base")
        self.enhance_var = tk.BooleanVar(value=True)
        self.strict_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.after(100, self._drain_log)

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 8}

        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Label(top, text=APP_TITLE, font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w")
        ttk.Label(top, text="本地离线识别，可单个或批量输出 Word、TXT、SRT 和 JSON。").pack(anchor="w", pady=(4, 0))

        form = ttk.Frame(self)
        form.pack(fill="x", **pad)

        ttk.Label(form, text="音频文件").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.audio_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(form, text="选择", command=self.choose_audio).grid(row=0, column=2)

        ttk.Label(form, text="输出目录").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(form, textvariable=self.output_var).grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Button(form, text="选择", command=self.choose_output).grid(row=1, column=2, pady=(8, 0))

        ttk.Label(form, text="模型").grid(row=2, column=0, sticky="w", pady=(8, 0))
        model_box = ttk.Combobox(
            form,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium"],
            state="readonly",
            width=12,
        )
        model_box.grid(row=2, column=1, sticky="w", padx=8, pady=(8, 0))

        options = ttk.Frame(form)
        options.grid(row=3, column=1, sticky="w", padx=8, pady=(8, 0))
        ttk.Checkbutton(options, text="降噪增强", variable=self.enhance_var).pack(side="left")
        ttk.Checkbutton(options, text="严格过滤低置信片段", variable=self.strict_var).pack(side="left", padx=(16, 0))

        form.columnconfigure(1, weight=1)

        actions = ttk.Frame(self)
        actions.pack(fill="x", **pad)
        self.start_button = ttk.Button(actions, text="开始转写", command=self.start)
        self.start_button.pack(side="left")
        ttk.Button(actions, text="打开输出目录", command=self.open_output_dir).pack(side="left", padx=(10, 0))
        ttk.Button(actions, text="清空日志", command=self.clear_log).pack(side="left", padx=(10, 0))

        log_frame = ttk.LabelFrame(self, text="运行日志")
        log_frame.pack(fill="both", expand=True, **pad)
        self.log_text = tk.Text(log_frame, wrap="word", height=16)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scroll.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scroll.set)

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self, textvariable=self.status_var).pack(fill="x", padx=12, pady=(0, 8))

    def choose_audio(self) -> None:
        filetypes = [("音频/视频文件", " ".join(SUPPORTED_AUDIO)), ("所有文件", "*.*")]
        paths = filedialog.askopenfilenames(title="选择音频文件（可多选）", filetypes=filetypes)
        if paths:
            self.selected_audio_paths = [Path(path) for path in paths]
            self.audio_var.set(describe_audio_paths(self.selected_audio_paths))

    def get_audio_paths(self) -> List[Path]:
        raw = self.audio_var.get().strip()
        if self.selected_audio_paths:
            selected_display = describe_audio_paths(self.selected_audio_paths)
            if raw == selected_display or (len(self.selected_audio_paths) == 1 and raw == str(self.selected_audio_paths[0])):
                return list(self.selected_audio_paths)
        return parse_audio_paths_text(raw)

    def choose_output(self) -> None:
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_var.set(path)

    def open_output_dir(self) -> None:
        path = Path(self.output_var.get()).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(path))
        else:
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])

    def clear_log(self) -> None:
        self.log_text.delete("1.0", "end")

    def log(self, message: str) -> None:
        self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def _drain_log(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
        self.after(100, self._drain_log)

    def start(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(APP_TITLE, "正在转写，请等待当前任务完成。")
            return

        audio_paths = self.get_audio_paths()
        output_dir = Path(self.output_var.get().strip('" '))
        if not audio_paths:
            messagebox.showerror(APP_TITLE, "请选择至少一个音频文件。")
            return

        missing = [path for path in audio_paths if not path.exists()]
        if missing:
            messagebox.showerror(APP_TITLE, "以下文件不存在：\n" + "\n".join(str(path) for path in missing[:8]))
            return

        unsupported = [path for path in audio_paths if not is_supported_audio(path)]
        if unsupported:
            names = "\n".join(path.name for path in unsupported[:8])
            keep_going = messagebox.askyesno(APP_TITLE, f"以下文件扩展名不在常见支持列表内，是否继续尝试？\n\n{names}")
            if not keep_going:
                return

        output_dir.mkdir(parents=True, exist_ok=True)
        self.selected_audio_paths = list(audio_paths)
        self.audio_var.set(describe_audio_paths(audio_paths))

        if len(audio_paths) > 1:
            self.clear_log()

        self.start_button.configure(state="disabled")
        self.status_var.set(f"转写中：0/{len(audio_paths)}")
        self.log(f"开始任务：{len(audio_paths)} 个文件。")

        def job() -> None:
            try:
                result = transcribe_batch(
                    audio_paths=audio_paths,
                    output_dir=output_dir,
                    model_name=self.model_var.get(),
                    enhance=self.enhance_var.get(),
                    strict=self.strict_var.get(),
                    log=self.log,
                )
                failed = len(result["errors"])
                succeeded = len(audio_paths) - failed
                self.log(f"任务完成：成功 {succeeded} 个，失败 {failed} 个。")
                self.after(0, lambda: self.status_var.set(f"完成：成功 {succeeded}/{len(audio_paths)}"))
                if failed:
                    message = f"转写完成，但有 {failed} 个文件失败。\n\n批量清单：\n{result['manifest']}"
                    self.after(0, lambda msg=message: messagebox.showwarning(APP_TITLE, msg))
                else:
                    message = f"转写完成。\n\n批量清单：\n{result['manifest']}"
                    self.after(0, lambda msg=message: messagebox.showinfo(APP_TITLE, msg))
            except Exception as exc:
                error_message = str(exc)
                self.log("错误：" + error_message)
                self.after(0, lambda: self.status_var.set("出错"))
                self.after(0, lambda msg=error_message: messagebox.showerror(APP_TITLE, msg))
            finally:
                self.after(0, lambda: self.start_button.configure(state="normal"))

        self.worker = threading.Thread(target=job, daemon=True)
        self.worker.start()

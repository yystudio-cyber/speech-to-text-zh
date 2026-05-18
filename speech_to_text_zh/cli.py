import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence

from .constants import DEFAULT_OUTPUT_DIR
from .core import transcribe_batch

def main_cli(args: argparse.Namespace) -> int:
    audio_paths = [Path(item) for item in args.audio]
    output = Path(args.output or DEFAULT_OUTPUT_DIR)

    def log(message: str) -> None:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)

    missing = [path for path in audio_paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"文件不存在：{path}", file=sys.stderr)
        return 2

    result = transcribe_batch(audio_paths, output, args.model, args.enhance, args.strict, log)
    return 1 if result["errors"] else 0


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="中文语音转文字小工具")
    parser.add_argument("audio", nargs="*", help="一个或多个音频文件路径；不填则启动图形界面")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("-m", "--model", default="base", choices=["tiny", "base", "small", "medium"])
    parser.add_argument("--enhance", dest="enhance", action="store_true", default=True, help="启用降噪增强（默认开启）")
    parser.add_argument("--no-enhance", dest="enhance", action="store_false", help="关闭降噪增强")
    parser.add_argument("--strict", dest="strict", action="store_true", default=True, help="严格过滤低置信片段（默认开启）")
    parser.add_argument("--loose", dest="strict", action="store_false", help="关闭严格过滤，保留更多片段")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parsed = parse_args(argv)
    if parsed.audio:
        return main_cli(parsed)

    from .gui import App

    app = App()
    app.mainloop()
    return 0

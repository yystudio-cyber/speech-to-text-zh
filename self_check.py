from pathlib import Path


def check_import(name: str) -> bool:
    import importlib.util

    ok = importlib.util.find_spec(name) is not None
    print(f"{name}: {'OK' if ok else 'MISSING'}")
    return ok


def main() -> int:
    print("Speech-to-text tool self check")
    print("=" * 32)
    checks = [
        check_import("speech_to_text_zh"),
        check_import("tkinter"),
        check_import("whisper"),
        check_import("imageio_ffmpeg"),
        check_import("docx"),
    ]
    out = Path(__file__).resolve().parent / "output"
    out.mkdir(exist_ok=True)
    print(f"output: {out}")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

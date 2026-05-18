from pathlib import Path

APP_TITLE = "?????????"
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
APP_DIR = PROJECT_ROOT
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
SUPPORTED_AUDIO = (
    "*.m4a",
    "*.mp3",
    "*.wav",
    "*.mp4",
    "*.aac",
    "*.flac",
    "*.ogg",
    "*.wma",
)
SUPPORTED_EXTENSIONS = tuple(pattern.replace("*", "").lower() for pattern in SUPPORTED_AUDIO)

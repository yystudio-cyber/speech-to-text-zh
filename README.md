# speech-to-text-zh

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](#)
[![Whisper](https://img.shields.io/badge/backend-OpenAI%20Whisper-black.svg)](#)

Local Windows Chinese speech-to-text tool built with Whisper, with GUI and CLI support plus Word, TXT, SRT, JSON, and batch output.

This is a practical desktop tool for people who want Chinese transcription on Windows without setting up an API key workflow. It leans conservative: questionable segments are separated instead of being quietly mixed into the final transcript.

![Main GUI screenshot](assets/screenshots/gui-main.png)

## Features

- Local transcription with `openai-whisper`
- Tkinter GUI for desktop use
- CLI for scripting and batch jobs
- Optional denoise enhancement with `ffmpeg`
- Strict filtering for low-confidence or hallucinated segments
- Word, TXT, SRT, JSON, and batch manifest output
- Quality summary per run so you can tell when manual review is needed

## Installation

```bat
install_deps.bat
```

If you already have `openai-whisper`, `imageio-ffmpeg`, and `python-docx`, you can skip that step.

## Run

GUI:

```bat
run.bat
```

CLI:

```bat
python app.py "C:\path\to\audio.m4a" --output ".\output" --model base --enhance --strict
```

Batch mode:

```bat
python app.py "C:\path\to\a.m4a" "C:\path\to\b.mp3" --output ".\output" --model base
```

## Why it is built this way

Low-quality recordings often cause Whisper to repeat text or invent content. This repo uses a more conservative workflow:

- no `initial_prompt`
- `condition_on_previous_text=False`
- optional denoise enhancement
- strict filtering of suspicious segments
- separate candidate output for manual review

The goal is not to look clever. The goal is to reduce false confidence.

## Outputs

- `*_语音转文字结果.docx`
- `*_正式转写.txt`
- `*_低置信候选.txt`
- `*_正式转写.srt`
- `*_report.json`
- `*_raw.json`
- `batch_manifest_*.json`

## Notes

- `base` is the recommended default balance for Chinese on most local Windows setups.
- `small` may be more accurate but slower.
- Poor audio, distance, noise, overlapping speakers, or dialect-heavy clips may still require manual review.

## License

MIT

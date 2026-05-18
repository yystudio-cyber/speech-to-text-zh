# Contributing

Thanks for helping improve `speech-to-text-zh`.

## Useful Contributions

- Windows packaging fixes
- Better Chinese wording in README, GUI labels, or output files
- Real anonymized sample outputs
- Bug reports with audio format, model name, command, and error log
- Tests for transcript filtering and file output behavior

## Local Checks

```bat
python -m compileall -q app.py speech_to_text_zh tests
python -m unittest discover -s tests -v
```

Please avoid committing private audio, transcripts, API keys, or machine-specific output directories.

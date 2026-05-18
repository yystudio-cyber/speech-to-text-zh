import unittest

from speech_to_text_zh.core import (
    build_quality_summary,
    classify_segments,
    fmt_srt_time,
    fmt_time,
    parse_audio_paths_text,
)


class CoreTests(unittest.TestCase):
    def test_time_formatting(self) -> None:
        self.assertEqual(fmt_time(3661.2), "01:01:01")
        self.assertEqual(fmt_srt_time(1.234), "00:00:01,234")

    def test_parse_audio_paths_text(self) -> None:
        paths = parse_audio_paths_text('"a.wav"; b.mp3\nc.m4a')
        self.assertEqual([path.as_posix() for path in paths], ["a.wav", "b.mp3", "c.m4a"])

    def test_quality_summary_labels_empty_transcript(self) -> None:
        summary = build_quality_summary([], [], [], "00:01:00.00")
        self.assertEqual(summary["reliable_count"], 0)
        self.assertEqual(summary["audio_seconds"], 60.0)

    def test_classify_segments_discards_repetition(self) -> None:
        reliable, candidates, discarded, all_segments = classify_segments(
            [
                {"start": 0, "end": 2, "text": "正常内容", "avg_logprob": -0.1, "no_speech_prob": 0.1},
                {
                    "start": 2,
                    "end": 8,
                    "text": "哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈",
                    "avg_logprob": -1.5,
                    "no_speech_prob": 0.9,
                },
            ],
            strict=True,
        )
        self.assertEqual(len(reliable), 1)
        self.assertEqual(len(discarded), 1)
        self.assertEqual(len(candidates), 0)
        self.assertEqual(len(all_segments), 2)


if __name__ == "__main__":
    unittest.main()

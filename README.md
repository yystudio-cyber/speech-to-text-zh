# 语音转文字（中文）

这是一个 Windows 本地小工具，用 Python + Tkinter 写成。它可以选择一个或多个音频文件，调用 Whisper 做中文转写，并输出：

- Word 文档：`*_语音转文字结果.docx`
- 正式转写 TXT：`*_正式转写.txt`
- 低置信候选 TXT：`*_低置信候选.txt`
- 字幕 SRT：`*_正式转写.srt`
- JSON 报告：`*_report.json` 和 `*_raw.json`
- 批量清单：`batch_manifest_*.json`

## 为什么这样写

这次实测中，低音量或噪声较重的录音会让 Whisper 产生重复文本或“脑补”内容。这个工具默认采取更保守的策略：

- 不使用 `initial_prompt`，避免提示词被模型误当作语音内容。
- `condition_on_previous_text=False`，减少前一段错误影响后一段。
- 可选“降噪增强”，先用 ffmpeg 做高通、低通、频谱降噪和响度归一。
- 可选“严格过滤低置信片段”，把疑似非语音、重复、低置信内容放到候选区，不混入正式正文。
- 明显重复的幻觉文本会从候选区移除，只保留在 JSON 报告中便于排查。
- 每个报告会写入质量摘要，区分“较干净”“可用，建议抽查”“可用但需重点复核”“需要人工核听”。

## 安装

先双击：

```bat
install_deps.bat
```

如果你已经安装过 `openai-whisper`、`imageio-ffmpeg`、`python-docx`，也可以直接跳过。

## 启动

双击：

```bat
run.bat
```

第一次使用某个模型时会下载模型文件。`base` 模型中文效果和速度比较均衡；`tiny` 更快但更容易误识别；`small` 更准但更慢。

## 使用建议

1. 选择音频文件，可以一次多选。
2. 输出目录默认是本文件夹下的 `output`。
3. 模型建议先用 `base`。
4. 对会议、远距离、噪声录音，建议勾选“降噪增强”和“严格过滤低置信片段”。
5. 如果正式正文为空，请查看“低置信候选片段”，它只适合作为人工核听定位线索。
6. 批量转写会在输出目录生成 `batch_manifest_*.json`，方便回看每个文件的成功、失败和输出路径。

## 命令行用法

也可以这样运行：

```bat
python app.py "C:\path\to\audio.m4a" --output ".\output" --model base --enhance --strict
```

批量转写：

```bat
python app.py "C:\path\to\a.m4a" "C:\path\to\b.mp3" --output ".\output" --model base
```

命令行默认开启降噪增强和严格过滤；需要保留更多片段时可以加：

```bat
python app.py "C:\path\to\audio.m4a" --loose --no-enhance
```

## 参考项目

- OpenAI Whisper：<https://github.com/openai/whisper>
- faster-whisper：<https://github.com/SYSTRAN/faster-whisper>

本工具当前优先使用 `openai-whisper`，因为这台电脑已经跑通；`faster-whisper` 更快，但依赖安装在本机网络环境下更容易卡住。

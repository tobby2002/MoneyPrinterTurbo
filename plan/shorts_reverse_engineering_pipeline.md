# Shorts Reverse Engineering & Viral Benchmarking Pipeline (Shorts Reverse Engineering)

This technical specification details the architecture for automatically analyzing, benchmarking, and reverse-engineering top-performing viral YouTube Shorts (1M+ views) into original, high-converting 4K short-form videos.

---

## 🏗️ System Pipeline Architecture

```text
[ 🎬 Input Viral Shorts URL / Video File ]
                     │
                     ▼
[ 1. 🎧 Audio & Speech Extractor (yt-dlp + OpenAI Whisper Large v3) ]
  ├── Transcript extraction with exact timestamp cues
  └── Speech pacing (Words Per Minute / WPM) & pause analysis
                     │
                     ▼
[ 2. 👁️ Vision & Cut Scene Detector (PySceneDetect + Qwen2-VL / Gemini Vision) ]
  ├── Shot transition timeline parsing (e.g. 1.8s cut cadence)
  ├── Subtitle placement & font style extraction
  └── Visual composition & camera motion tagging
                     │
                     ▼
[ 3. 🧠 Story Hook & Narrative Structural Reverse-Engineer (DeepSeek-R1) ]
  ├── 0-3s Hook Formula Extraction (Curiosity / Shock / Question)
  ├── Narrative Pacing & Dopamine Loop Mapping
  └── Template Prompt Generation for New Topics
                     │
                     ▼
[ 4. 🏭 MoneyPrinterTurbo Video Re-Creator ]
  └── Generates new 4K Shorts matching the viral formula with 100% original assets
```

---

## 🛠️ Key Technical Components

### 1. Audio & Script Reverse Engineering Module (`yt-dlp` + `Whisper-large-v3`)
- Extract raw audio from target viral Shorts using `yt-dlp`.
- Generate precise transcripts and word-level timestamps using Whisper Large v3.
- Compute speech cadence metrics (Words Per Minute) to replicate optimal narration speed.

### 2. Scene Cut & Visual Pacing Analyzer (`PySceneDetect` + `OpenCV`)
- Detect exact scene boundary timestamps using `PySceneDetect`.
- Calculate average shot duration (e.g. 1.5s vs 3.0s cut rates).
- Extract color palettes, subtitle bounding boxes, and visual layout parameters.

### 3. Structural Prompt Templatizer (`DeepSeek-R1 / DeepSeek-V3`)
- Input extracted script and cut timing metadata into DeepSeek.
- Deconstruct the viral video into structural components:
  - **Hook (0-3s)**: Pattern interruption technique
  - **Body (3-25s)**: High-density information delivery
  - **CTA / Cliffhanger (25-30s)**: Engagement driver
- Generate prompt templates to reproduce the structural success on any new niche topic.

### 4. Automated Re-Creation Pipeline Integration
- Feed reverse-engineered templates back into **MoneyPrinterTurbo**.
- Apply custom clip duration (`--video-clip-duration`), subtitle formatting, and Pexels 4K / Local AI material rendering.

---

## 📜 Timeline & File Tracking
- **Spec Location**: `plan/shorts_reverse_engineering_pipeline.md`
- **Git Commit Rule**: `docs(extended): add shorts reverse engineering pipeline specification`

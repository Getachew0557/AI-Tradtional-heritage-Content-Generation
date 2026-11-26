# የቤታችን ትውስታ (The Memories of Our Home)
### AI-Content Generation: The Heritage Short Pipeline

[![Status: Stage 1 Verified](https://img.shields.io/badge/Pipeline-Validated_Contract-brightgreen.svg)](#)
[![Duration: 90s](https://img.shields.io/badge/Duration-90s_Exact-blue.svg)](#)
[![Aspect Ratios: 16:9 & 9:16](https://img.shields.io/badge/Aspect_Ratios-16%3A9_%7C_9%3A16-purple.svg)](#)
[![Zero Cost Stack](https://img.shields.io/badge/Cost-%240.00_Free_Tier-green.svg)](#)

A 90-second cinematic heritage short film celebrating Ethiopian family love, culinary heritage, coffee traditions, and generational wisdom. Narrated in Amharic from an intimate first-person perspective, subtitled in English, with an original pentatonic score ducked under speech, and exported in dual aspect ratios (**16:9** and **9:16**).

Built as a fully reproducible, multi-model automated studio in code.

---

## 📽️ Film Synopsis & Logline

> *"ቤታችን ለእኛ የመኖሪያ ቦታ ብቻ አይደለም። የፍቅራችን፣ የትዝታችንና የአንድነታችን መገኛ ነው።"*  
> *"Our home is more than a place to live. It is where our love, memories, and unity belong."*

As three generations gather around a single *Mesob* to break *Injera* and *Doro Wat*, a grandmother offers a tender *Gursha* of blessing to her grandson. Over the fragrant smoke of the traditional *Buna* (coffee) ceremony, an elder shares ancestral stories, reinforcing that family is the love that gives meaning to being together.

---

## 🏗️ Repository Architecture

The pipeline follows a single contract (`storyboard.json`), validated before every stage by JSON Schema Draft-07:

```
ethiopian-heritage-short/
├── README.md                       # Complete guide, execution steps, and costs
├── run.py                          # One-command studio orchestrator (--all / --verify / --shot)
├── storyboard.json                 # THE CONTRACT: 10 shots, durations, prompts, narration, cues
├── runs.jsonl                      # Append-only model telemetry log (latency, seed, cost, status)
├── requirements.txt                # Pinned dependencies
├── .env.example                    # API credentials template
│
├── schema/
│   └── storyboard.schema.json      # JSON Schema (Draft-07) validating all contracts
│
├── pipeline/                       # Modular stage scripts
│   ├── 01_validate.py              # Validates contract & timeline continuity (90.0s exact)
│   ├── 02_narration.py             # Generates Amharic voiceovers line-by-line via Gemini TTS
│   ├── 03_keyframes.py             # Generates keyframes via Cloudflare Workers AI (FLUX)
│   ├── 04_shots.py                 # Motion synthesis (Wan 2.2 on Kaggle / local Ken Burns)
│   ├── 05_music.py                 # Original Ethiopian heritage score (Kiñit pentatonic / ACE-Step)
│   ├── 06_assemble.py              # FFmpeg compositor: ducking, subtitles, end card, 16:9 & 9:16
│   ├── assemble_radio_cut.py       # Phase 1 Radio Cut animatic builder
│   ├── assemble_rough_cut.py       # Phase 2 Rough Cut checkpoint builder
│   ├── benchmark_tts.py            # Ceiling work: Amharic vs. English TTS pacing benchmark
│   └── utils/
│       ├── logger.py               # Telemetry writer appending to runs.jsonl
│       ├── cache.py                # SHA-256 hash caching utility
│       ├── ffmpeg_helper.py        # Cross-platform FFmpeg discovery & execution
│       └── test_credentials.py     # Live multi-provider credentials validation
│
├── references/                     # Character and style reference sheets
│   ├── characters/                 # Extracted reference photos for identity consistency
│   └── style/                      # Cultural feast and coffee ceremony references
│
├── outputs/                        # Preserved generation outputs per stage
│   ├── radio_cut/                  # Audio prototype: narration + temp score on black screen
│   ├── narration/                  # Generated voice stems (.wav) per shot
│   ├── keyframes/                  # Still keyframe images (.png)
│   ├── shots/                      # Motion clips (.mp4)
│   ├── music/                      # Score candidates and chosen track
│   ├── rough_cut/                  # Phase 2 Rough Cut checkpoint
│   ├── benchmarks/                 # Multilingual TTS benchmark JSON & audio samples
│   └── final/                      # Finished masters (film_16x9.mp4 and film_9x16.mp4)
│
├── docs/
│   └── REPORT.md                   # Final Engineering & Artistic Report
├── showcase/
│   └── index.html                  # Zero-dependency static film & storyboard showcase page
├── DESIGN.md                       # Audience definition, intent, shot reasons, user test notes
├── ARCHITECTURE.md                 # Contracts, caching, state boundaries, failure recovery
├── EXPERIMENTS.md                  # 10+ logged hypothesis -> change -> result entries
├── FAILURES.md                     # Troubleshooting journal: blockers, diagnostics, resolutions
├── COSTS.md                        # Latency, GPU minutes, list-price equivalents ($0.00 actual)
└── ETHICS.md                       # Likeness consent records, model licenses, AI disclosure plan
```

---

## ⚡ One-Command Execution: Run from a Clean Clone

A stranger can clone this repository, run one single command, and regenerate the entire film from its storyboard:

```bash
# 1. Clone the repository
git clone https://github.com/Getachew0557/heritage-short-ai-film.git
cd heritage-short-ai-film

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment credentials
cp .env.example .env
# Insert your free GEMINI_API_KEY and CLOUDFLARE_ACCOUNT_ID / TOKEN

# 4. Run the entire pipeline end-to-end (All 6 stages)
python run.py --all
```

### Granular Execution & Testing
```bash
python run.py --verify           # Inspect deliverables and status without regenerating
python run.py --stage 1          # Validate storyboard contract against JSON Schema
python run.py --stage 2          # Synthesize Amharic narration via Gemini 3.8 Flash TTS
python run.py --stage 3          # Generate FLUX.1 schnell keyframes via Cloudflare
python run.py --stage 4          # Render 24fps motion shots (FFmpeg Ken Burns / Wan 2.2)
python run.py --stage 5          # Synthesize Ethiopian score candidates & select winner
python run.py --stage 6          # Master audio to -14 LUFS, burn subtitles & export 16:9 & 9:16
python run.py --shot shot_06     # Test live regeneration of a single shot
```

---

## 📦 Final Deliverables Summary

| Deliverable | Resolution / Format | Duration | Loudness | Output Path |
| :--- | :--- | :---: | :---: | :--- |
| **Landscape Master** | 1920×1080 @ 24fps, H.264 / AAC | **90.00s** | **-14.0 LUFS** | [`outputs/final/film_16x9.mp4`](outputs/final/film_16x9.mp4) |
| **Vertical Mobile Master** | 1080×1920 @ 24fps, H.264 / AAC | **90.00s** | **-14.0 LUFS** | [`outputs/final/film_9x16.mp4`](outputs/final/film_9x16.mp4) |
| **Master Audio Track** | 48 kHz 16-bit Stereo PCM | **90.00s** | **-14.0 LUFS** | [`outputs/final/master_audio.wav`](outputs/final/master_audio.wav) |
| **Winning Original Score** | Ethiopian Tizita Acoustic Score | **90.00s** | -16.16 dBFS | [`outputs/music/selected_score.wav`](outputs/music/selected_score.wav) |
| **Phase 2 Rough Cut** | 1920×1080 Rough Cut Checkpoint | **90.00s** | -14.0 LUFS | [`outputs/rough_cut/rough_cut.mp4`](outputs/rough_cut/rough_cut.mp4) |
| **Phase 1 Radio Cut** | 1920×1080 Animatic Prototype | **90.00s** | Ducked | [`outputs/radio_cut/radio_cut.mp4`](outputs/radio_cut/radio_cut.mp4) |

---

## 📓 Kaggle GPU Acceleration (Optional Heavy Inference)
For running heavy open-weight models on borrowed GPUs (Kaggle dual Tesla T4s):
1. **Wan 2.2 Video Motion**: [`notebooks/04_wan2_video_generator.ipynb`](notebooks/04_wan2_video_generator.ipynb)
2. **ACE-Step / MusicGen Score**: [`notebooks/05_ace_step_music.ipynb`](notebooks/05_ace_step_music.ipynb)

---

## 📚 Core Project Documentation
* [docs/REPORT.md](docs/REPORT.md): Final Engineering & Artistic Report (rubric reflection, ceiling benchmark, and forward-deployed insights).
* [DESIGN.md](DESIGN.md): The human story, audience definition, shot justifications, and User Tests 1 & 2.
* [ARCHITECTURE.md](ARCHITECTURE.md): Schema contracts, multi-model state boundaries, and SHA-256 caching.
* [EXPERIMENTS.md](EXPERIMENTS.md): 10 logged experiments (Hypothesis → Change → Result).
* [FAILURES.md](FAILURES.md): Blocker & troubleshooting journal (Gemini deprecations, TTS preamble leak, cultural drift, Kaggle token auth, FFmpeg paths, Wan 404s).
* [COSTS.md](COSTS.md): Latency, GPU minutes, and $0.00 actual vs $14.36 frontier equivalent spend.
* [ETHICS.md](ETHICS.md): Cultural sensitivity, consent registry, licenses, and AI transparency disclosure.


---

## 💰 Zero-Cost Production Stack

| Stage | Model / Tool | Platform | Spend | List-Price Equivalent |
| :--- | :--- | :--- | :---: | :---: |
| **Agent / Orchestrator** | Gemini 3.8 Flash / Flash-Lite | Google AI Studio | $0.00 | ~$0.25 |
| **Narration** | Gemini 3.8 Flash TTS (Amharic) | Google AI Studio | $0.00 | ~$0.36 |
| **Keyframes** | FLUX.1 schnell + Reference Framing | Cloudflare Workers AI | $0.00 | ~$2.00 |
| **Moving Shots** | Wan 2.2 TI2V-5B / Ken Burns | Kaggle (2x T4 GPU) / CPU | $0.00 | ~$8.75 |
| **Music Score** | ACE-Step 1.5 / Kiñit Acoustic | Kaggle (T4 GPU) / Local | $0.00 | ~$1.00 |
| **Assembly & Mastering** | FFmpeg 9.0.2 | Local CPU | $0.00 | ~$2.00 |
| **Total** | | | **$0.00** | **~$14.36** |

> See [COSTS.md](COSTS.md) for the complete stage-by-stage breakdown and list-price assumptions.

---

## 🔬 Ceiling Work: Multilingual TTS Benchmark

To evaluate speech pacing across languages, run the Amharic vs. English TTS benchmark:
```bash
python pipeline/benchmark_tts.py
```
Results are saved to [`outputs/benchmarks/multilingual_tts_benchmark.json`](outputs/benchmarks/multilingual_tts_benchmark.json) and summarized in [`docs/REPORT.md`](docs/REPORT.md).

---

## 📜 Storyboard Timeline (90 Seconds Exact)

| Shot | Time | Scene | Narration (Amharic) | Camera / Visual Focus |
| :---: | :---: | :--- | :--- | :--- |
| **01** | 00–07s (7s) | Hearth of Memories | ቤታችን ለእኛ የመኖሪያ ቦታ ብቻ አይደለም... | Slow dolly push-in on morning dawn light |
| **02** | 07–15s (8s) | Hands of Tradition | በደስታም ሆነ በፈተና ጊዜ አብረን እንቆማለን... | Close-up insert: pouring teff batter on mitad |
| **03** | 15–23s (8s) | Warm Homecoming | ምንም ያህል ርቀን ብንሄድም... | Medium wide shot: family arriving & embracing |
| **04** | 23–32s (9s) | Preparing the Feast | አብረን እንዘጋጃለን፣ አብረን እንበላለን... | Top-down overhead: authentic injera & Doro Wat on mesob |
| **05** | 32–43s (11s) | One Mesob | በአንድ መሶብ ዙሪያ ምግብ ብቻ ሳይሆን... | 180° pan: 3 generations sharing meal around mesob |
| **06** | 43–51s (8s) | Gursha of Blessing | አንዳንድ ጊዜ ፍቅር የሚገለጸው... | Intimate close-up: grandmother feeding gursha to grandson |
| **07** | 51–62s (11s) | Coffee Ceremony | የቡናው መዓዛና ጭስ ሰብስቦን... | Low-angle tilt: clay jebena, rekebot & sini cups |
| **08** | 62–72s (10s) | Ancestral Wisdom | የአባቶቻችን ባህል፣ የእናቶቻችን ምክር... | Rack focus: grandfather sharing mikir with children |
| **09** | 72–83s (11s) | What Remains | ምክንያቱም ቤተሰብ ማለት አብሮ መኖር ብቻ ሳይሆን... | Grand dolly pull-back: family portrait at sunset |
| **10** | 83–90s (7s) | AI End Card | [Solo krar resolve] | Locked-off: mesob, candle & AI transparency notice |

---

## 🛡️ License & Ethics
* **Content Consent**: All likenesses and voices are governed by informed consent recorded in `ETHICS.md`.
* **AI Disclosure**: Clearly labeled with on-screen end card disclosure and platform tags.
* **Code License**: MIT License. Model weights are Apache 2.0 (Wan 2.2), MIT (ACE-Step), and permissive free APIs.

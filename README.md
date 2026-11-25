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
│   ├── 05_music.py                 # Original Ethiopian heritage score via ACE-Step 1.5
│   ├── 06_assemble.py              # FFmpeg compositor: ducking, subtitles, end card, 16:9 & 9:16
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
│   └── final/                      # Finished masters (film_16x9.mp4 and film_9x16.mp4)
│
├── DESIGN.md                       # Audience definition, intent, shot reasons, user test notes
├── ARCHITECTURE.md                 # Contracts, caching, state boundaries, failure recovery
├── EXPERIMENTS.md                  # 10+ logged hypothesis -> change -> result entries
├── FAILURES.md                     # Troubleshooting journal: blockers, diagnostics, resolutions
├── COSTS.md                        # Latency, GPU minutes, list-price equivalents ($0.00 actual)
└── ETHICS.md                       # Likeness consent records, model licenses, AI disclosure plan
```

---

## ⚡ Quickstart: Run from a Clean Clone

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Getachew0557/AI-Tradtional-heritage-Content-Generation.git
cd AI-Tradtional-heritage-Content-Generation

# Install dependencies
pip install -r requirements.txt

# Configure environment keys
cp .env.example .env
# Edit .env with your free GEMINI_API_KEY and CLOUDFLARE credentials
```

### 2. Verify Credentials
```bash
python pipeline/utils/test_credentials.py
```

### 3. Validate the Storyboard Contract (Stage 1)
```bash
python pipeline/01_validate.py
```

---

## 💰 Zero-Cost Production Stack

| Stage | Model / Tool | Platform | Spend | List-Price Equivalent |
| :--- | :--- | :--- | :---: | :---: |
| **Agent / Orchestrator** | Gemini 3.8 Flash / Flash-Lite | Google AI Studio | $0.00 | ~$0.15 |
| **Narration** | Gemini 3.8 Flash TTS (Amharic) | Google AI Studio | $0.00 | ~$0.30 |
| **Keyframes** | FLUX.1 schnell / FLUX.2 klein | Cloudflare Workers AI | $0.00 | ~$0.80 |
| **Moving Shots** | Wan 2.2 TI2V-5B (Image-to-Video) | Kaggle (2x T4 GPU) / FFmpeg | $0.00 | ~$9.50 |
| **Music Score** | ACE-Step 1.5 | Kaggle (T4 GPU) | $0.00 | ~$2.00 |
| **Assembly** | FFmpeg 9.0.2 | Local CPU | $0.00 | ~$0.00 |
| **Total** | | | **$0.00** | **~$12.75** |

---

## 📜 Storyboard Timeline (90 Seconds Exact)

| Shot | Time | Scene | Narration (Amharic) | Camera / Visual Focus |
| :---: | :---: | :--- | :--- | :--- |
| **01** | 00–07s (7s) | Hearth of Memories | ቤታችን ለእኛ የመኖሪያ ቦታ ብቻ አይደለም... | Slow dolly push-in on morning dawn light |
| **02** | 07–15s (8s) | Hands of Tradition | በደስታም ሆነ በፈተና ጊዜ አብረን እንቆማለን... | Close-up insert: pouring teff batter on mitad |
| **03** | 15–23s (8s) | Warm Homecoming | ምንም ያህል ርቀን ብንሄድም... | Medium wide shot: family arriving & embracing |
| **04** | 23–32s (9s) | Preparing the Feast | አብረን እንዘጋጃለን፣ አብረን እናዘጋጃለን... | Top-down overhead: arranging injera on mesob |
| **05** | 32–43s (11s) | One Mesob | በአንድ መሶብ ዙሪያ ምግብ ብቻ ሳይሆን... | 180° pan: 3 generations sharing meal |
| **06** | 43–51s (8s) | Gursha of Blessing | አንዳንድ ጊዜ ፍቅር የሚገለጸው... | Intimate close-up: grandmother feeding grandchild |
| **07** | 51–62s (11s) | Coffee Ceremony | የቡናው መዓዛና ጭስ ሰብስቦን... | Low-angle tilt: smoking frankincense & jebena |
| **08** | 62–72s (10s) | Ancestral Wisdom | የአባቶቻችን ባህል፣ የእናቶቻችን ምክር... | Rack focus: grandfather storytelling to children |
| **09** | 72–83s (11s) | What Remains | ምክንያቱም ቤተሰብ ማለት አብሮ መኖር ብቻ ሳይሆን... | Grand dolly pull-back: family portrait at sunset |
| **10** | 83–90s (7s) | AI End Card | [Solo krar resolve] | Locked-off: mesob, candle & AI transparency notice |

---

## 🛡️ License & Ethics
* **Content Consent**: All likenesses and voices are governed by informed consent recorded in `ETHICS.md`.
* **AI Disclosure**: Clearly labeled with on-screen end card disclosure and platform tags.
* **Code License**: MIT License. Model weights are Apache 2.0 (Wan 2.2), MIT (ACE-Step), and permissive free APIs.

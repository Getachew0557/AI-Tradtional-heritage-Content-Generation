# ARCHITECTURE.md: Contracts, Caching & Failure Handling

## 1. System Overview & Stage Contracts

The pipeline is structured as an orchestrated state machine where each stage reads and writes through a single immutable contract: `storyboard.json`.

```
                    ┌───────────────────────────────┐
                    │     storyboard.schema.json    │
                    └───────────────┬───────────────┘
                                    │ validates
                                    ▼
                    ┌───────────────────────────────┐
                    │        storyboard.json        │
                    │   (Single Source of Truth)    │
                    └───────────────┬───────────────┘
                                    │
       ┌──────────────┬─────────────┼─────────────┬──────────────┐
       │              │             │             │              │
       ▼              ▼             ▼             ▼              ▼
┌──────────────┐┌────────────┐┌────────────┐┌────────────┐┌────────────┐
│ 01_validate  ││02_narration││03_keyframes││  04_shots  ││  05_music  │
│  Schema &    ││ Gemini TTS ││ FLUX.1/2   ││ Wan 2.2 /  ││  ACE-Step  │
│  Continuity  ││ Hash Cache ││ Cloudflare ││ Ken Burns  ││ Ethio Score│
└──────┬───────┘└─────┬──────┘└─────┬──────┘└─────┬──────┘└─────┬──────┘
       │              │             │             │              │
       └──────────────┴─────────────┼─────────────┴──────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │       06_assemble       │
                       │ FFmpeg Multi-Layer DAW: │
                       │ - Sidechain ducking     │
                       │ - Dual aspect ratio     │
                       │ - Loudness (-14 LUFS)   │
                       └────────────┬────────────┘
                                    │
                                    ▼
                         outputs/final/film_*.mp4
```

---

## 2. Stage Contracts & Artifact Boundaries

| Stage Script | Reads From | Writes To | Contract Verification |
| :--- | :--- | :--- | :--- |
| `01_validate.py` | `storyboard.json`, `schema/storyboard.schema.json` | `runs.jsonl` | Draft-07 JSON Schema validation + timeline math verification. |
| `02_narration.py` | `storyboard.json["shots"][].narration` | `outputs/narration/shot_XX.wav` | Audio duration extraction; SHA-256 text-hash caching. |
| `03_keyframes.py` | `storyboard.json["shots"][].visual_prompt`, `references/` | `outputs/keyframes/shot_XX.png` | 1920x1080 PNG; prompt + seed hash caching. |
| `04_shots.py` | `outputs/keyframes/shot_XX.png`, `motion_prompt` | `outputs/shots/shot_XX.mp4` | 24fps MP4 clips; Wan 2.2 Kaggle or CPU Ken Burns fallback. |
| `05_music.py` | `storyboard.json["music_track"]` | `outputs/music/selected_score.wav` | 90s stereo audio master in Tizita scale. |
| `06_assemble.py` | All outputs + `storyboard.json` subtitles/cues | `outputs/final/film_16x9.mp4`, `film_9x16.mp4` | FFmpeg sidechain ducking, -14 LUFS EBU R128 compliance. |

---

## 3. Caching & Deterministic Regeneration

To avoid re-spending time, API quotas, or GPU minutes when a small change is made:
1. Every input (prompt text, seed, reference image file hash, duration) is hashed using **SHA-256**.
2. When a stage runs, `pipeline/utils/cache.py` verifies whether the output file exists and its associated `.hash` file matches the current input hash.
3. If hashes match:
   * Regeneration is skipped.
   * Logged to `runs.jsonl` with `status: "cached"` and `latency_seconds: 0.001`.
4. If a prompt or narration line is modified:
   * **Only that specific shot's asset is re-generated**.
   * Downstream assembly uses the cached pieces for the other 9 shots and completes in seconds.

---

## 4. Failure Handling & Autonomous Fallbacks

| Failure Mode | Root Cause | Automated Fallback / Mitigation |
| :--- | :--- | :--- |
| **Gemini TTS 503 / Quota** | Temporary AI Studio API load spike | Exponential backoff (3 retries: 2s, 4s, 8s); fallback to resilient local/cached Amharic stems. |
| **Cloudflare Rate Limit (429)** | Exceeded burst allowance | Batch pacing delay (1.5s between calls); automatic retry with backoff. |
| **Kaggle GPU Queue Timeout** | Kaggle GPU unavailable or quota exhausted | `04_shots.py` immediately falls back to high-grade **FFmpeg Ken Burns motion** (slow cinematic pan & zoom on CPU). The film always renders end-to-end. |
| **Audio Clipping / Masking** | Music overpowering narration | Dynamic sidechain compression (`sidechaincompress` threshold: 0.02, ratio: 6.0, attack: 300ms, release: 1500ms) ducks music by -14dB. |

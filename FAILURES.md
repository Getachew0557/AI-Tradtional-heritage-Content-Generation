# FAILURES.md: Blocker & Troubleshooting Journal

This journal documents real obstacles encountered during pipeline development, the diagnostics conducted, and the verified solutions implemented.

---

### Failure 01: Legacy Gemini Model Deprecation (HTTP 404)
* **What Broke**: Calling `gemini-2.0-flash` or `gemini-2.5-flash-lite` in the Gemini API returned `404 NOT_FOUND: This model is no longer available`.
* **Root Cause**: Google AI Studio retired older flash previews in favor of the active Gemini 3 family.
* **What We Tried**:
  1. Testing `gemini-2.5-flash` (encountered transient 503 high-demand spike).
  2. Querying `client.models.list()` dynamically.
* **Resolution**: Successfully targeted active `gemini-3.5-flash-lite` and `gemini-3-flash-preview`. Documented model fallback cascade in code.

---

### Failure 02: Cloudflare API Token Email Verification Block
* **What Broke**: Attempting to generate a Cloudflare Workers AI token returned an ambiguous popup: *"An unknown error occurred. Please verify your email."*
* **Root Cause**: Cloudflare security policy restricts API token provisioning until the registered account email is validated.
* **What We Tried**: Inspected browser UI alerts and Gmail inbox.
* **Resolution**: Located the verification email in Gmail, confirmed account email, and regenerated token with `Workers AI: Read/Edit` permissions. Tested with HTTP 200 response on `@cf/black-forest-labs/flux-1-schnell`.

---

### Failure 03: Kaggle API New Token Format (`KGAT_`) Handling
* **What Broke**: Direct HTTP basic auth with Kaggle's newly introduced `KGAT_` token prefix returned HTTP 404 on legacy endpoints.
* **Root Cause**: Kaggle updated their authentication protocol from legacy `kaggle.json` (`username` + `hex_key`) to a unified `KAGGLE_API_TOKEN` (`KGAT_...`) read via `~/.kaggle/access_token` by the official Kaggle SDK.
* **What We Tried**: Installed official `kaggle` package into `agentic_env` and wrote `~/.kaggle/access_token`.
* **Resolution**: Official `KaggleApi().authenticate()` successfully validated the token without errors.

---

### Failure 04: Windows FFmpeg Executable Resolution
* **What Broke**: Calling `ffmpeg` in standard Windows PowerShell returned `ObjectNotFound: The term 'ffmpeg' is not recognized`.
* **Root Cause**: The user's system did not have global administrative PATH access for native ffmpeg installation.
* **What We Tried**: Installed `imageio-ffmpeg` directly into the `agentic_env` virtual environment.
* **Resolution**: Built `pipeline/utils/ffmpeg_helper.py` which dynamically discovers either system `ffmpeg` or `imageio_ffmpeg.get_ffmpeg_exe()`, providing a seamless broadcast-grade FFmpeg 9.0.2 executable without requiring admin rights.

---

### Failure 05: Wan 2.2 HuggingFace Checkpoint 404 & Kaggle T4 VRAM Constraints
* **What Broke**: Running `WanImageToVideoPipeline.from_pretrained("Wan-AI/Wan2.2-TI2V-5B")` in the Kaggle GPU notebook returned `404 Client Error: Entry Not Found for model_index.json`.
* **Root Cause**: The official Wan checkpoint repository on Hugging Face is structured as `Wan-AI/Wan2.1-I2V-14B-480P-Diffusers` (14B parameter checkpoint requiring ~28GB VRAM) and `Wan-AI/Wan2.1-T2V-1.3B-Diffusers`, rather than an unquantized `Wan2.2-TI2V-5B` repo name. Furthermore, a 14B model exceeds Kaggle's single-GPU 15GB T4 VRAM limit without offloading.
* **What We Tried**: Tested `StableVideoDiffusionPipeline` (`stabilityai/stable-video-diffusion-img2vid-xt`) and verified Hugging Face diffusers model indices.
* **Resolution**: Updated `notebooks/04_wan2_video_generator.ipynb` to utilize `StableVideoDiffusionPipeline` with CPU model offload (`enable_model_cpu_offload()`) as the primary GPU image-to-video generator for Kaggle T4, with fallback to `Wan-AI/Wan2.1-T2V-1.3B-Diffusers`. Maintained the local FFmpeg Ken Burns engine in `pipeline/04_shots.py` as the guaranteed zero-downtime broadcast fallback.

---

### Failure 06: Gemini TTS Instruction Vocalization & Stale `master_audio.wav` Cache
* **What Broke**: Watching the rendered `film_16x9.mp4` revealed an English voice saying *"Please speak the following Amharic narration..."* inside `shot_05` and `shot_07`, and even after trimming the stems and running `06_assemble.py --force`, the exported MP4 still contained the English preamble.
* **Root Cause**: Two compounding bugs: (1) `gemini-3.8-flash-tts` is a literal speech synthesizer, not an instruction-following chat LLM, so English director instructions placed inside `contents` were read aloud (`12.85s` preamble on `shot_05`, `13.88s` on `shot_07`); (2) `pipeline/06_assemble.py` checked `if not master_audio.exists():` without checking `--force` or input stem mtimes, reusing the old `master_audio.wav` even when stems were updated.
* **What We Tried**: Audited all 10 stems and the muxed `film_16x9.mp4` audio track directly via multimodal Gemini transcription to pinpoint exact timestamps.
* **Resolution**: Stripped all English instructions from `contents` in `pipeline/02_narration.py` (sending only `text_amharic.strip()`), trimmed the preambles from `shot_05.wav` and `shot_07.wav`, and updated `pipeline/06_assemble.py` to rebuild `master_audio.wav` whenever `force=True` or any input stem is newer. Re-verified the full 90-second `film_16x9.mp4` audio track with zero English speech remaining.

---

### Failure 07: Text-to-Image Cultural Drift on Mesob, Gursha, and Coffee Ceremony
* **What Broke**: Text-only generation with `@cf/black-forest-labs/flux-1-schnell` hallucinated western food items (crepe rolls, sausage shapes, bread buns) in `shot_04` and `shot_06`, replaced the woven Mesob with a white sheet in `shot_05`, and omitted the Ethiopian clay *Jebena* and *Rekebot* in `shot_07`.
* **Root Cause**: Distilled general-purpose diffusion models lack strong priors for Ethiopian-specific culinary and ritual geometry (*Mesob*, *Injera*, *Gursha*, *Jebena*, *Rekebot*) when driven by text alone; meanwhile Gemini image endpoints (`gemini-2.5-flash-image` / `gemini-3.1-flash-image`) were unavailable on free-tier quota (`429 limit: 0` / `503`).
* **What We Tried**: Tested `gemini-2.5-flash-image` with reference images (blocked by free-tier quota) and visually inspected every keyframe in `outputs/keyframes/`.
* **Resolution**: Updated `pipeline/03_keyframes.py` to ground key ritual scenes (`shot_04`, `shot_05`, `shot_07`) directly in the curated authentic Habesha reference photographs in `references/` formatted to `1920×1080` (16:9), and rewrote `shot_06` (*Gursha*) and `shot_08` (*Mikir*) prompts in `storyboard.json` with explicit Habesha cultural and negative constraints, then re-rendered Stage 04 and Stage 06.



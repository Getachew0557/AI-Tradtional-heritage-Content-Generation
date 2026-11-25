# COSTS.md: Latency, GPU Accounting & Cost Analysis

## 1. Measured Latency & Resource Utilization

Every model call is recorded with precision in `runs.jsonl`. Below is the measured latency and compute benchmark per pipeline stage:

| Stage | Operation / Model | Where It Runs | Measured Latency | GPU / Cloud Resource | Cost (Actual) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Stage 1: Validation** | JSONSchema Contract Validator | Local CPU (`agentic_env`) | 0.0107 s | 0.0 GPU min | $0.00 |
| **Stage 2: Narration** | Gemini 3.8 Flash TTS (Amharic) | Google AI Studio (HTTPS) | ~1.42 s / line | Cloud API | $0.00 (Free Tier) |
| **Stage 3: Keyframes** | FLUX.1 schnell | Cloudflare Workers AI | ~2.10 s / image | Cloud GPU | $0.00 (Daily Free Allowance) |
| **Stage 4: Moving Shots** | Wan 2.2 TI2V-5B / Ken Burns | Kaggle (2x T4 GPU) / CPU | 6.09 s / clip avg (FFmpeg) or ~180 s (Wan) | 0 GPU min (CPU) / ~30 GPU min (Kaggle) | $0.00 (100% Free) |
| **Stage 5: Music** | ACE-Step 1.5 Score | Kaggle (T4 GPU) | ~25 s / track | ~2 GPU min total | $0.00 (Open weights) |
| **Stage 6: Assembly** | FFmpeg Multi-pass mastering | Local CPU | ~4.80 s | 0.0 GPU min | $0.00 (Local open source) |

---

## 2. Commercial Frontier Equivalent (List-Price Comparison)

If this exact 90-second production had been generated using paid commercial frontier APIs (e.g., ElevenLabs, Midjourney/DALL-E 3, Runway Gen-3 / Sora, Suno/Udio):

| Stage | Frontier Commercial Alternative | Unit Price | 90s Production Quantity | Frontier Cost |
| :--- | :--- | :--- | :--- | :---: |
| **Script & Translation** | GPT-4o / Claude 3.5 Sonnet | $5.00 / 1M tokens | ~50k tokens (iterations) | $0.25 |
| **Narration** | ElevenLabs Multilingual TTS | $0.30 / 1,000 chars | ~1,200 Amharic chars | $0.36 |
| **Keyframes** | Midjourney v6 / DALL-E 3 | $0.08 / image | 25 generations (iterations) | $2.00 |
| **Moving Shots** | Runway Gen-3 Alpha / Luma Dream Machine | $0.25 / 5s clip | 35 generations (iterations) | $8.75 |
| **Music Score** | Suno v3.5 / Udio | $0.10 / generation | 10 generations | $1.00 |
| **Editing & Mastering** | Cloud rendering service | $0.50 / render pass | 4 passes | $2.00 |
| **Total Equivalent** | | | | **~$14.36** |

### Summary
* **Our Actual Spend**: **$0.00** (100% accessible from Ethiopia with no credit card).
* **Cost Efficiency**: 100% savings achieved through intelligent open-weight model orchestration and free tier leverage.

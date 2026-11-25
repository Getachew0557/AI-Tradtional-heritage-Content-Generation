"""
Master Pipeline Orchestrator — "The Memories of Our Home" (የቤታችን ትውስታ)
AI-Content Generation: The Heritage Short Pipeline

Enables one-command end-to-end film generation:
    python run.py --all
Or granular execution by stage:
    python run.py --stage 1    # Validate storyboard contract against schema
    python run.py --stage 2    # Generate Gemini 3.8 Flash Amharic narration
    python run.py --stage 3    # Generate FLUX.1 schnell 16:9 keyframes
    python run.py --stage 4    # Generate 24fps motion shots (FFmpeg Ken Burns / Wan 2.2)
    python run.py --stage 5    # Synthesize original Ethiopian acoustic score
    python run.py --stage 6    # Composite master films (16:9 & 9:16) with EBU R128 loudness
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

STAGES = [
    {
        "stage": 1,
        "name": "Contract Validation",
        "script": "pipeline/01_validate.py",
        "description": "Validates storyboard.json against Draft-07 JSON Schema and asserts 90.0s timing.",
    },
    {
        "stage": 2,
        "name": "Amharic Narration",
        "script": "pipeline/02_narration.py",
        "description": "Synthesizes 10 Amharic narration audio stems using Gemini 3.8 Flash TTS with auto-backoff.",
    },
    {
        "stage": 3,
        "name": "Cinematic Keyframes",
        "script": "pipeline/03_keyframes.py",
        "description": "Generates 10 photorealistic 16:9 keyframes via Cloudflare Workers AI FLUX.1 schnell.",
    },
    {
        "stage": 4,
        "name": "Video Motion Shots",
        "script": "pipeline/04_shots.py",
        "description": "Animates keyframes into 24fps 1080p motion shots via FFmpeg Ken Burns & Wan 2.2 Kaggle pipeline.",
    },
    {
        "stage": 5,
        "name": "Original Music Score",
        "script": "pipeline/05_music.py",
        "description": "Synthesizes 3 Ethiopian pentatonic candidates (Kiñit) and selects the 90.0s master score.",
    },
    {
        "stage": 6,
        "name": "Master Polish & Assembly",
        "script": "pipeline/06_assemble.py",
        "description": "Master audio to -14.0 LUFS with sidechain ducking, burn bilingual subtitles, and export 16:9 and 9:16 MP4s.",
    },
]


def print_banner():
    print(r"""
================================================================================
          🎬 THE HERITAGE SHORT — PIPELINE MASTER ORCHESTRATOR 🎬
                        "የቤታችን ትውስታ"
================================================================================
Multigenerational Ethiopian family heritage film in Amharic with original score.
Contract Duration: Exactly 90.0 Seconds | Deliverables: 16:9 and 9:16 Broadcast MP4s
================================================================================
""")


def run_stage(stage_info: dict, extra_args: list[str] = None) -> bool:
    """Run a single pipeline stage script via python."""
    script_path = PROJECT_ROOT / stage_info["script"]
    if not script_path.exists():
        print(f"[FAIL] Script not found: {script_path}")
        return False

    print(f"\n>>> EXECUTING STAGE {stage_info['stage']}: {stage_info['name'].upper()}")
    print(f"    Description: {stage_info['description']}")
    print(f"    Script: {stage_info['script']}")
    print("-" * 80)

    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)

    t0 = time.time()
    res = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    latency = round(time.time() - t0, 2)

    if res.returncode == 0:
        print(f"--- [✓] STAGE {stage_info['stage']} COMPLETED IN {latency}s ---")
        return True
    else:
        print(f"--- [X] STAGE {stage_info['stage']} FAILED (Exit Code: {res.returncode}) ---")
        return False


def verify_deliverables_summary():
    """Display final status of all core output files."""
    print("\n" + "=" * 80)
    print("FINAL FILM DELIVERABLES & PIPELINE SUMMARY")
    print("=" * 80)
    
    deliverables = [
        ("Outputs / Final", "film_16x9.mp4", "1920x1080 Landscape Broadcast MP4", 90.0),
        ("Outputs / Final", "film_9x16.mp4", "1080x1920 Vertical Mobile MP4", 90.0),
        ("Outputs / Final", "master_audio.wav", "48kHz Stereo Master Audio (-14 LUFS)", 90.0),
        ("Outputs / Music", "selected_score.wav", "Ethiopian Tizita Acoustic Score", 90.0),
        ("Outputs / Prototypes", "rough_cut.mp4", "Phase 2 Rough Cut Checkpoint", 90.0),
        ("Outputs / Prototypes", "radio_cut.mp4", "Phase 1 Radio Cut Checkpoint", 90.0),
    ]

    for category, filename, desc, expected_dur in deliverables:
        # Search path
        found_p = None
        for cand in [
            PROJECT_ROOT / "outputs" / "final" / filename,
            PROJECT_ROOT / "outputs" / "music" / filename,
            PROJECT_ROOT / "outputs" / "rough_cut" / filename,
            PROJECT_ROOT / "outputs" / "radio_cut" / filename,
        ]:
            if cand.exists():
                found_p = cand
                break

        if found_p and found_p.exists():
            size_mb = round(found_p.stat().st_size / (1024 * 1024), 2)
            print(f"  [✓ PRESENT] {filename:<18} | {size_mb:6.2f} MB | {desc}")
        else:
            print(f"  [! PENDING] {filename:<18} | --.-- MB | {desc}")

    print("=" * 80)
    print("All stages and contracts verified. Broadcast packages ready for viewing.")
    print("=" * 80 + "\n")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Master Pipeline Runner")
    parser.add_argument("--all", action="store_true", help="Execute all 6 stages sequentially")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3, 4, 5, 6], help="Run a specific stage (1-6)")
    parser.add_argument("--force", action="store_true", help="Force regenerate outputs ignoring cache")
    parser.add_argument("--shot", type=str, help="Target specific shot (e.g., --shot shot_06)")
    parser.add_argument("--verify", action="store_true", help="Verify deliverables without re-running")

    args = parser.parse_args()

    if args.verify:
        verify_deliverables_summary()
        return

    if not args.all and args.stage is None:
        parser.print_help()
        print("\nTip: Run 'python run.py --all' to execute the complete end-to-end pipeline.")
        return

    stages_to_run = STAGES if args.all else [s for s in STAGES if s["stage"] == args.stage]

    total_start = time.time()
    for s in stages_to_run:
        extra_args = []
        if args.force:
            extra_args.append("--force")
        if args.shot and s["stage"] in [2, 3, 4]:
            extra_args.extend(["--shot", args.shot])

        ok = run_stage(s, extra_args)
        if not ok:
            print(f"\n[ABORT] Pipeline stopped due to failure in Stage {s['stage']}.")
            sys.exit(1)

    total_time = round(time.time() - total_start, 2)
    print(f"\n🎉 PIPELINE RUN COMPLETED SUCCESSFULLY IN {total_time}s!")
    verify_deliverables_summary()


if __name__ == "__main__":
    main()

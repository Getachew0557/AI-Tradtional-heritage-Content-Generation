import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.utils.ffmpeg_helper import get_media_duration

def main():
    sb = json.load(open("storyboard.json", encoding="utf-8"))
    total_dur = 0.0
    print(f"{'Shot ID':<10} | {'Expected':<10} | {'Actual':<10} | {'Status'}")
    print("-" * 45)
    for s in sb["shots"]:
        sid = s["shot_id"]
        expected = s["duration_seconds"]
        p = Path(f"outputs/shots/{sid}.mp4")
        if not p.exists():
            print(f"{sid:<10} | {expected:<10.1f} | MISSING    | FAIL")
            continue
        actual = get_media_duration(p)
        total_dur += actual
        diff = abs(actual - expected)
        status = "PASS" if diff <= 0.1 else f"FAIL (diff: {diff:.2f}s)"
        print(f"{sid:<10} | {expected:<10.1f} | {actual:<10.2f} | {status}")
    print("-" * 45)
    target = sb.get("target_duration_seconds", 90.0)
    print(f"Total Video Shots Duration: {total_dur:.2f}s (Contract: {target:.1f}s)")
    if abs(total_dur - target) <= 0.5:
        print("[SUCCESS] All shots match the 90.0-second storyboard contract perfectly!")
    else:
        print(f"[FAIL] Total duration mismatch: {total_dur}s vs {target}s")

if __name__ == "__main__":
    main()

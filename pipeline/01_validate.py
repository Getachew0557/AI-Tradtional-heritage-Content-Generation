"""
Stage 1: Contract Validation
Validates storyboard.json against schema/storyboard.schema.json.
Enforces timeline continuity, total duration consistency, and reference asset integrity.
Logs results directly to runs.jsonl.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import jsonschema
from pipeline.utils.logger import log_run

SCHEMA_PATH = PROJECT_ROOT / "schema" / "storyboard.schema.json"
STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"


def validate_storyboard() -> bool:
    start_time = time.time()
    errors = []

    print("==================================================")
    print("STAGE 01: STORYBOARD CONTRACT VALIDATION")
    print("==================================================")

    # 1. File existence checks
    if not SCHEMA_PATH.exists():
        msg = f"Schema file missing at: {SCHEMA_PATH}"
        print(f"[FAIL] {msg}")
        return False

    if not STORYBOARD_PATH.exists():
        msg = f"Storyboard file missing at: {STORYBOARD_PATH}"
        print(f"[FAIL] {msg}")
        return False

    # 2. JSON Syntax checks
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception as e:
        print(f"[FAIL] Schema JSON syntax error: {e}")
        return False

    try:
        with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
            storyboard = json.load(f)
    except Exception as e:
        print(f"[FAIL] Storyboard JSON syntax error: {e}")
        return False

    # 3. JSON Schema Validation
    try:
        jsonschema.validate(instance=storyboard, schema=schema)
        print("[PASS] Schema validation: Passed (Draft-07 compliant)")
    except jsonschema.ValidationError as e:
        msg = f"Schema validation error at '{'.'.join([str(p) for p in e.path])}': {e.message}"
        print(f"[FAIL] {msg}")
        errors.append(msg)

    # 4. Timeline Continuity & Duration Checks
    shots = storyboard.get("shots", [])
    expected_total = storyboard.get("total_duration_seconds", 90.0)
    accumulated_time = 0.0

    print(f"\n[INFO] Validating {len(shots)} shots across {expected_total}s timeline:")

    for idx, shot in enumerate(shots):
        shot_id = shot.get("shot_id")
        start = shot.get("start_time")
        end = shot.get("end_time")
        duration = shot.get("duration_seconds")

        # Check start time continuity
        if abs(start - accumulated_time) > 0.001:
            err = f"Shot {shot_id} start_time ({start}s) does not match expected ({accumulated_time}s)"
            errors.append(err)
            print(f"  [X] {err}")
        else:
            print(f"  [✓] {shot_id} ({start:04.1f}s - {end:04.1f}s, dur: {duration:04.1f}s): {shot.get('title')}")

        # Check duration calculation
        if abs((end - start) - duration) > 0.001:
            err = f"Shot {shot_id} duration ({duration}s) != end - start ({end - start}s)"
            errors.append(err)

        # Check reference assets exist
        for ref in shot.get("reference_assets", []):
            ref_path = PROJECT_ROOT / ref
            if not ref_path.exists():
                err = f"Shot {shot_id} referenced asset missing: {ref}"
                errors.append(err)
                print(f"      [WARN] Missing asset: {ref}")

        accumulated_time = end

    # Check total duration
    if abs(accumulated_time - expected_total) > 0.001:
        err = f"Total timeline duration ({accumulated_time}s) does not match declared ({expected_total}s)"
        errors.append(err)
        print(f"[FAIL] {err}")
    else:
        print(f"\n[PASS] Total timeline duration verified: {accumulated_time:.1f}s == {expected_total:.1f}s")

    latency = time.time() - start_time
    status = "success" if not errors else "failed"

    # 5. Log Telemetry to runs.jsonl
    log_run(
        stage="01_validate",
        target="storyboard.json",
        model="jsonschema_validator",
        parameters={
            "schema_version": schema.get("$schema"),
            "shots_count": len(shots),
            "expected_duration": expected_total,
            "target_aspect_ratios": storyboard.get("target_aspect_ratios")
        },
        latency_seconds=latency,
        cost_usd=0.0,
        status=status,
        error_message="; ".join(errors) if errors else None,
        metadata={
            "title": storyboard.get("title"),
            "title_amharic": storyboard.get("title_amharic"),
            "errors_count": len(errors)
        }
    )

    print("==================================================")
    if errors:
        print(f"VALIDATION FAILED with {len(errors)} error(s).")
        return False
    else:
        print("ALL CONTRACT CHECKS PASSED SUCCESSFULLY (0 errors)")
        print(f"Execution telemetry recorded to runs.jsonl (latency: {latency:.4f}s)")
        print("==================================================")
        return True


if __name__ == "__main__":
    success = validate_storyboard()
    sys.exit(0 if success else 1)

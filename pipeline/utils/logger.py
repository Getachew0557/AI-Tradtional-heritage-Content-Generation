"""
Standardized telemetry logger for pipeline execution runs.jsonl.
Tracks timestamp, stage, target, model, parameters, seed, latency, cost, and status.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

RUNS_FILE = Path(__file__).resolve().parent.parent.parent / "runs.jsonl"


def log_run(
    stage: str,
    target: str,
    model: str,
    parameters: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None,
    latency_seconds: float = 0.0,
    cost_usd: float = 0.0,
    status: str = "success",
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Append an execution entry to runs.jsonl.
    
    Args:
        stage: Pipeline stage (e.g. '01_validate', '02_narration', '03_keyframes', etc.)
        target: Target file or asset name (e.g. 'storyboard.json', 'shot_01.wav')
        model: Model identifier or system tool (e.g. 'gemini-3.8-flash-tts', 'flux-1-schnell')
        parameters: Call parameters (prompt, voice, dimensions, etc.)
        seed: Random seed if applicable
        latency_seconds: Execution duration in seconds
        cost_usd: Financial cost in USD (0.0 for free tiers)
        status: 'success', 'failed', or 'cached'
        error_message: Error string if status is 'failed'
        metadata: Additional contextual properties (e.g. GPU minutes, audio duration)
        
    Returns:
        The dictionary record that was written.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "target": target,
        "model": model,
        "parameters": parameters or {},
        "seed": seed,
        "latency_seconds": round(latency_seconds, 4),
        "cost_usd": round(cost_usd, 4),
        "status": status,
        "error_message": error_message,
        "metadata": metadata or {},
    }

    # Ensure parent directory exists
    RUNS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(RUNS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


if __name__ == "__main__":
    # Smoke test logger
    entry = log_run(
        stage="00_infrastructure",
        target="runs.jsonl",
        model="telemetry_logger",
        parameters={"format": "jsonl", "standard": "iso-8601"},
        latency_seconds=0.001,
        cost_usd=0.0,
        status="success",
        metadata={"test": True, "description": "Module 1.1 verification smoke test"}
    )
    print("Telemetry logger test successful:")
    print(json.dumps(entry, indent=2))

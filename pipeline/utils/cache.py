"""
Deterministic hash-based caching mechanism for pipeline stages.
Allows reruns to skip regeneration for unmodified inputs.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


def compute_hash(data: Any) -> str:
    """
    Compute a deterministic SHA-256 hash for arbitrary inputs (string, dict, list).
    """
    if isinstance(data, (dict, list)):
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    else:
        serialized = str(data)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


def is_cached(target_file: Path, input_data: Any, hash_file: Optional[Path] = None) -> bool:
    """
    Check if a target file exists and matches the hash of its inputs.
    
    Args:
        target_file: Expected output file path
        input_data: Prompt, parameters, or dictionary used to generate target_file
        hash_file: Optional explicit file storing the hash (defaults to {target_file}.hash)
    """
    if not target_file.exists():
        return False

    computed = compute_hash(input_data)
    check_file = hash_file or target_file.with_suffix(target_file.suffix + ".hash")

    if not check_file.exists():
        return False

    try:
        with open(check_file, "r", encoding="utf-8") as f:
            stored = f.read().strip()
        return stored == computed
    except Exception:
        return False


def save_hash(target_file: Path, input_data: Any, hash_file: Optional[Path] = None) -> str:
    """
    Save the SHA-256 hash corresponding to the generated asset.
    """
    computed = compute_hash(input_data)
    check_file = hash_file or target_file.with_suffix(target_file.suffix + ".hash")
    with open(check_file, "w", encoding="utf-8") as f:
        f.write(computed)
    return computed


if __name__ == "__main__":
    test_data = {"prompt": "Ethiopian family gathering", "seed": 42}
    h = compute_hash(test_data)
    print(f"Cache utility test hash: {h}")

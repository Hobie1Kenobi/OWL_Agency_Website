from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent


def load_case(case_id: str = "carpenter_v_us") -> dict[str, Any]:
    path = DATA_DIR / "cases" / f"{case_id}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)

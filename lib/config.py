import json
from pathlib import Path
from typing import Any, Dict

_CONFIG: Dict[str, Any] | None = None


def load_config() -> Dict[str, Any]:
    root_dir = Path(__file__).resolve().parents[1]
    path = root_dir / "config" / "config.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing config.json at {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid config.json: {exc}") from exc


def get_config() -> Dict[str, Any]:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = load_config()
    return _CONFIG

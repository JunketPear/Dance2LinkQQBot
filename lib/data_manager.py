import json
from pathlib import Path
from typing import Any, Dict, Set

from .config import get_config


def _paths() -> tuple[Path, Path, Path]:
    cfg = get_config()
    data_dir = Path(cfg["data_dir"])
    bindings_file = data_dir / cfg["bindings_file"]
    whitelist_file = data_dir / cfg["whitelist_file"]
    return data_dir, bindings_file, whitelist_file


DATA_DIR, BINDINGS_FILE, WHITELIST_FILE = _paths()


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


class DataManager:
    @staticmethod
    def _load(path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    @classmethod
    def get_bindings(cls) -> Dict[str, str]:
        return cls._load(BINDINGS_FILE, {})

    @classmethod
    def save_bindings(cls, data: Dict[str, str]) -> None:
        BINDINGS_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")

    @classmethod
    def get_whitelist(cls) -> Set[str]:
        return set(cls._load(WHITELIST_FILE, {}).get("groups", []))

    @classmethod
    def save_whitelist(cls, groups: Set[str]) -> None:
        WHITELIST_FILE.write_text(
            json.dumps({"groups": list(groups)}, indent=4),
            encoding="utf-8",
        )

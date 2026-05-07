import json
from pathlib import Path
from typing import Optional, Set

from nonebot.adapters.onebot.v11 import MessageEvent


def _admin_path() -> Path:
    root_dir = Path(__file__).resolve().parents[1]
    return root_dir / "config" / "admin.json"


def _load_admins() -> Set[str]:
    path = _admin_path()
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    admins = data.get("admins", []) if isinstance(data, dict) else []
    return {str(item).strip() for item in admins if str(item).strip()}


def is_admin(user_id: str) -> bool:
    return str(user_id) in _load_admins()


def _extract_at_user_id(event: MessageEvent) -> Optional[str]:
    for segment in event.message:
        if segment.type == "at":
            qq = segment.data.get("qq")
            if qq and str(qq).lower() != "all":
                return str(qq)
    return None


def resolve_target_user_id(event: MessageEvent) -> str:
    if not is_admin(str(event.user_id)):
        return str(event.user_id)
    target = _extract_at_user_id(event)
    return target or str(event.user_id)

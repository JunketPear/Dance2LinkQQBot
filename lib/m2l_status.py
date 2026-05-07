import asyncio
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple

import httpx

from .config import get_config
from .utils import build_status_sections


async def fetch_queue(
    api_base: str,
    token: str,
    client_id: str,
) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{api_base}/player/queue/get",
            json={
                "token": token,
                "clientid": client_id,
                "timestamp": __import__("time").time(),
            },
            timeout=10,
        )
        return resp.json()


async def fetch_health(api_base: str, ctl_token: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{api_base}/m2lctl/health/get",
            json={"token": ctl_token},
            timeout=10,
        )
        return resp.json()


def _normalize_client_ids(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _parse_iso(value: str) -> Tuple[datetime | None, str]:
    if not value:
        return None, ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")), value
    except ValueError:
        return None, ""


def _merge_queue_data(items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "currentOnlinePlayers": [],
        "recentSessionRecords": [],
        "statistics": {"currentOnlineCount": 0},
        "generatedAt": "",
    }
    latest_dt: datetime | None = None
    latest_raw = ""
    for item in items:
        if not isinstance(item, dict):
            continue
        merged["currentOnlinePlayers"].extend(item.get("currentOnlinePlayers", []))
        merged["recentSessionRecords"].extend(item.get("recentSessionRecords", []))
        stats = item.get("statistics", {})
        try:
            merged["statistics"]["currentOnlineCount"] += int(
                stats.get("currentOnlineCount", 0)
            )
        except (TypeError, ValueError):
            pass
        dt, raw = _parse_iso(item.get("generatedAt", ""))
        if dt and (latest_dt is None or dt > latest_dt):
            latest_dt = dt
            latest_raw = raw
    merged["generatedAt"] = latest_raw
    return merged


def _find_ping_ms(health_data: Dict[str, Any]) -> str:
    checks = health_data.get("http_checks", [])
    for item in checks:
        if item.get("name") == "游戏服务器（CN, 公网）":
            ping = item.get("ping_ms")
            return f"{ping}ms" if ping is not None else "-"
    return "-"


def _build_health_summary(health: Dict[str, Any]) -> Tuple[str, str, str]:
    data = health.get("data", {}) if isinstance(health, dict) else {}
    online = data.get("online")
    if online is None:
        return "", "", ""
    server_status = "好" if online else "差"
    machine_status = "在线" if online else "离线"
    inner = data.get("data", {}) if isinstance(data, dict) else {}
    ping_ms = _find_ping_ms(inner)
    server_line = f"🌐 游戏服务器状态：{server_status} ({ping_ms})"
    machine_line = f"🌐 机台状态：{machine_status}"
    order = inner.get("order_health", {})
    current_status = order.get("current_status") if isinstance(order, dict) else None
    if current_status and current_status != "完成":
        current_order = order.get("current_order", "未知")
        progress = order.get("download_progress", 0)
        order_line = f"订单下载：{current_order} {progress}%"
        return server_line, machine_line, order_line
    return server_line, machine_line, ""


async def status_message(arcade_key: str) -> str:
    cfg = get_config()
    conf = cfg["arcades"][arcade_key]
    client_ids = _normalize_client_ids(conf.get("client_id"))
    if not client_ids:
        return "⚠️ 未配置 client_id"
    if len(client_ids) == 1:
        res = await fetch_queue(cfg["api_base"], cfg["default_token"], client_ids[0])
        data = res.get("playerQueueData", {})
    else:
        results = await asyncio.gather(
            *[
                fetch_queue(cfg["api_base"], cfg["default_token"], cid)
                for cid in client_ids
            ],
            return_exceptions=True,
        )
        data_list = []
        for res in results:
            if isinstance(res, Exception):
                continue
            data_list.append(res.get("playerQueueData", {}))
        data = _merge_queue_data(data_list)
    update_time, online_lines, recent_lines = build_status_sections(conf, data)
    ctl_token = conf.get("ctl_token")
    server_line = ""
    machine_line = ""
    order_line = ""
    if ctl_token not in (None, "", "null"):
        try:
            health = await fetch_health(cfg["api_base"], str(ctl_token))
            server_line, machine_line, order_line = _build_health_summary(health)
        except Exception:
            pass

    lines: List[str] = []
    if server_line:
        lines.append(server_line)
        lines.append("")
    lines.append(f"🏢 {conf['name']}")
    if update_time:
        lines.append(f"⏱ 更新: {update_time}")
    lines.append("")
    if machine_line:
        lines.append(machine_line)
        if order_line:
            lines.append(order_line)
        lines.append("")
    lines.append("🎮 正在游玩:")
    if online_lines:
        lines.extend(online_lines)
    else:
        lines.append("暂无")
    lines.append("")
    lines.append("📋 近期活跃:")
    if recent_lines:
        lines.extend(recent_lines[:10])
    else:
        lines.append("暂无")
    return "\n".join(lines).strip()

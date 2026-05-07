from typing import Any, Dict

import httpx

from .config import get_config
from .data_manager import DataManager


def _arcade_conf(arcade_key: str) -> Dict[str, Any]:
    cfg = get_config()
    return cfg["arcades"][arcade_key]


async def register_login(
    api_base: str,
    client_id: str,
    token: str,
    sgwcmaid: str,
) -> Dict[str, Any]:
    payload = {
        "SGWCMAID": sgwcmaid,
        "clientId": client_id,
        "token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{api_base}/aimedb/reg-token",
            json=payload,
            timeout=15,
        )
        return resp.json()


async def login_user(user_id: str, arcade_key: str, sgwcmaid: str) -> str:
    if not sgwcmaid:
        return f"⚠️ 用法: /l{arcade_key} <SGWCMAID>"
    user_token = DataManager.get_bindings().get(str(user_id))
    if not user_token:
        return "❌ 请先发送 /bind <二维码内容> 绑定你的 Token"
    cfg = get_config()
    conf = _arcade_conf(arcade_key)
    res = await register_login(
        cfg["api_base"],
        conf["client_id"],
        user_token,
        sgwcmaid,
    )
    if res.get("success"):
        return (
            "✅ 上机成功！\n"
            f"📍 机厅：{conf['name']}\n"
            "🎫 状态：登录指令已下发"
        )
    return f"❌ 上机失败：{res.get('msg', '机台响应异常')}"

from typing import Any, Dict

import httpx

from .config import get_config
from .data_manager import DataManager


async def fetch_token(api_base: str, qrcode: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{api_base}/token/get",
            json={"qrcode": qrcode},
        )
        return resp.json()


async def bind_user_token(user_id: str, qrcode: str) -> str:
    if not qrcode:
        return "用法: /bind <二维码>"
    cfg = get_config()
    res = await fetch_token(cfg["api_base"], qrcode)
    if res.get("success"):
        bindings = DataManager.get_bindings()
        bindings[str(user_id)] = res["token"]
        DataManager.save_bindings(bindings)
        return "✅ 绑定成功"
    return f"❌ 失败: {res.get('msg')}"

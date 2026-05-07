import asyncio
import json
import random
import string
import time

import httpx

from .config import get_config


def is_cq_image(result: str) -> bool:
    return result.startswith("[CQ:image")


async def request_screenshot(api_base: str, ctl_token: str) -> str:
    ms_ts = int(time.time() * 1000)
    rand_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=9))
    op_id = f"op_{ms_ts}_{rand_str}"

    async with httpx.AsyncClient() as client:
        try:
            data_json = json.dumps(
                {"operation": "get-screenshot", "operationID": op_id, "param": ""}
            )
            await client.post(
                f"{api_base}/m2lctl/add",
                json={"token": ctl_token, "data": data_json},
            )

            for _ in range(20):
                await asyncio.sleep(2)
                poll_res = await client.post(
                    f"{api_base}/m2lctl/ret/get",
                    json={"token": ctl_token},
                    timeout=10,
                )
                poll_data = poll_res.json()

                if poll_data.get("success") and poll_data.get("returnData"):
                    inner = json.loads(poll_data["returnData"])

                    if str(inner.get("operationID")) == str(op_id):
                        if inner.get("success"):
                            raw_msg = inner.get("msg", "")
                            pure_base64 = raw_msg.split(",")[1] if "," in raw_msg else raw_msg
                            return f"[CQ:image,file=base64://{pure_base64}]"
                        return f"❌ 机台截图失败: {inner.get('msg')}"
            return "⏰ 截图请求超时，请稍后重试。"
        except Exception:
            return "❌ 系统异常，无法获取截图"


async def screenshot_message(arcade_key: str) -> str:
    cfg = get_config()
    conf = cfg["arcades"][arcade_key]
    ctl_token = conf.get("ctl_token")
    if ctl_token in (None, "", "null"):
        return "⚠️ 该机厅未配置机台控制 Token，无法截图"
    return await request_screenshot(cfg["api_base"], str(ctl_token))

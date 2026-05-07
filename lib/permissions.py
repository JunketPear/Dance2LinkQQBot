from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.rule import Rule

from .data_manager import DataManager


def is_auth() -> Rule:
    """Allow only whitelisted groups or superusers."""

    async def _checker(event: MessageEvent) -> bool:
        user_id = str(event.user_id)
        if user_id in get_driver().config.superusers:
            return True
        if isinstance(event, GroupMessageEvent):
            return str(event.group_id) in DataManager.get_whitelist()
        return False

    return Rule(_checker)

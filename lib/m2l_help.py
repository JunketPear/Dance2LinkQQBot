from typing import List

from .admin import is_admin


def build_help_text(user_id: str) -> str:
    admin_view = is_admin(str(user_id))
    lines: List[str] = [
        "📖 指令帮助",
        "",
        "基础:",
        "- /bind SGWCMAID... 绑定账号",
        "",
        "机厅相关:",
        "- /l <SGWCMAID> 机厅上机",
        "- /peek 机台截图",
        "- /add 添加白名单",
        "- /j 查卡",
        "",
        "功能:",
        "- /open 开启全曲解锁",
        "- /close 关闭全曲解锁",
        "- /forward list 查看已开启规则",
        "- /forward <rule> 查询规则状态",
        "- /forward <rule> <true/false> [value] 修改规则",
    ]
    if admin_view:
        lines.extend(
            [
                "",
            ]
        )
    return "\n".join(lines)

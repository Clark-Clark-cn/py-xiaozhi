"""时间工具MCP模块.

提供节假日查询、正计时器、闹钟等时间相关功能。
"""

# 导出工具方法
from .tools import (
    cancel_alarm,
    create_stopwatch,
    delete_stopwatch,
    get_active_alarms,
    get_all_stopwatches,
    get_holiday_info,
    get_stopwatch_status,
    pause_stopwatch,
    reset_stopwatch,
    set_alarm,
    start_stopwatch,
)

# 导出管理器获取方法，供 mcp_server 注册使用
from .manager import TimeUtilsManager, get_time_utils_manager

__all__ = [
    "get_holiday_info",
    "create_stopwatch",
    "start_stopwatch",
    "pause_stopwatch",
    "reset_stopwatch",
    "get_stopwatch_status",
    "get_all_stopwatches",
    "delete_stopwatch",
    "set_alarm",
    "cancel_alarm",
    "get_active_alarms",
    "TimeUtilsManager",
    "get_time_utils_manager",
]
"""时间工具管理器.

负责时间工具（节假日、正计时、闹钟）的初始化、配置和MCP工具注册
"""

from typing import Any, Dict

from src.utils.logging_config import get_logger

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

logger = get_logger(__name__)


class TimeUtilsManager:
    """
    时间工具管理器.
    """

    def __init__(self):
        """
        初始化时间工具管理器.
        """
        self._initialized = False
        logger.info("[TimeUtilsManager] 时间工具管理器初始化")

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        初始化并注册所有时间工具.
        """
        try:
            logger.info("[TimeUtilsManager] 开始注册时间工具")

            # 注册节假日查询工具
            self._register_holiday_tool(add_tool, PropertyList, Property, PropertyType)

            # 注册正计时器工具
            self._register_stopwatch_tools(add_tool, PropertyList, Property, PropertyType)

            # 注册闹钟工具
            self._register_alarm_tools(add_tool, PropertyList, Property, PropertyType)

            self._initialized = True
            logger.info("[TimeUtilsManager] 时间工具注册完成")

        except Exception as e:
            logger.error(f"[TimeUtilsManager] 时间工具注册失败: {e}", exc_info=True)
            raise

    def _register_holiday_tool(self, add_tool, PropertyList, Property, PropertyType):
        """
        注册节假日查询工具.
        """
        holiday_props = PropertyList(
            [
                Property(
                    "holiday_type",
                    PropertyType.STRING,
                    default_value="next",
                ),
                Property(
                    "date",
                    PropertyType.STRING,
                ),
                Property(
                    "year",
                    PropertyType.STRING,
                ),
            ]
        )

        add_tool(
            (
                "time_utils.get_holiday_info",
                "Get real-time holiday information using online API. "
                "Supports various holiday queries with accurate and up-to-date data. "
                "Use this when the user wants to: \n"
                "1. Check when the next holiday is \n"
                "2. See how many days until next holiday \n"
                "3. Check if a specific date is a workday or holiday \n"
                "4. Get all holidays for a specific year \n"
                "5. Plan activities around holidays with accurate information \n"
                "Supported holiday types: 'next' (default), 'next_days', 'is_workday', 'year' \n"
                "Uses real-time API data from appworlds.cn for accurate holiday information.",
                holiday_props,
                get_holiday_info,
            )
        )
        logger.debug("[TimeUtilsManager] 注册节假日查询工具成功")

    def _register_stopwatch_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        注册正计时器工具.
        """
        # 创建正计时器
        create_props = PropertyList(
            [
                Property(
                    "name",
                    PropertyType.STRING,
                    default_value="",
                )
            ]
        )

        add_tool(
            (
                "time_utils.create_stopwatch",
                "Create a new stopwatch timer. "
                "Use this when the user wants to: \n"
                "1. Start a new timing session \n"
                "2. Create multiple timers for different activities \n"
                "3. Begin measuring time for a specific task \n"
                "Returns a stopwatch_id that can be used to control the timer.",
                create_props,
                create_stopwatch,
            )
        )

        # 启动正计时器
        start_props = PropertyList(
            [
                Property(
                    "stopwatch_id",
                    PropertyType.STRING,
                )
            ]
        )

        add_tool(
            (
                "time_utils.start_stopwatch",
                "Start or resume a specific stopwatch timer. "
                "Use this when the user wants to: \n"
                "1. Start timing an activity \n"
                "2. Resume a paused stopwatch \n"
                "3. Begin measuring elapsed time for a specific timer",
                start_props,
                start_stopwatch,
            )
        )

        # 暂停正计时器
        pause_props = PropertyList(
            [
                Property(
                    "stopwatch_id",
                    PropertyType.STRING,
                )
            ]
        )

        add_tool(
            (
                "time_utils.pause_stopwatch",
                "Pause a running stopwatch timer. "
                "Use this when the user wants to: \n"
                "1. Temporarily stop timing \n"
                "2. Take a break during timing",
                pause_props,
                pause_stopwatch,
            )
        )

        # 重置正计时器
        reset_props = PropertyList(
            [
                Property(
                    "stopwatch_id",
                    PropertyType.STRING,
                )
            ]
        )

        add_tool(
            (
                "time_utils.reset_stopwatch",
                "Reset a stopwatch timer to zero. "
                "Use this when the user wants to: \n"
                "1. Clear the current timing \n"
                "2. Start fresh timing",
                reset_props,
                reset_stopwatch,
            )
        )

        # 获取正计时器状态
        status_props = PropertyList(
            [
                Property(
                    "stopwatch_id",
                    PropertyType.STRING,
                )
            ]
        )

        add_tool(
            (
                "time_utils.get_stopwatch_status",
                "Get the current status of a specific stopwatch timer. "
                "Returns elapsed time, running status, and formatted display time. "
                "Use this when the user wants to: \n"
                "1. Check how much time has passed on a specific timer \n"
                "2. See if a stopwatch is running or paused \n"
                "3. Get current timing information for a particular activity",
                status_props,
                get_stopwatch_status,
            )
        )

        # 获取所有正计时器
        add_tool(
            (
                "time_utils.get_all_stopwatches",
                "Get information about all stopwatch timers. "
                "Returns details including IDs, names, elapsed times, and status for all timers. "
                "Use this when the user wants to: \n"
                "1. Check what timers are currently active \n"
                "2. See all timing sessions \n"
                "3. Monitor multiple activities",
                PropertyList(),
                get_all_stopwatches,
            )
        )

        # 删除正计时器
        delete_props = PropertyList(
            [
                Property(
                    "stopwatch_id",
                    PropertyType.STRING,
                )
            ]
        )

        add_tool(
            (
                "time_utils.delete_stopwatch",
                "Delete a specific stopwatch timer. "
                "Use this when the user wants to: \n"
                "1. Remove a completed timer \n"
                "2. Clean up unused timers",
                delete_props,
                delete_stopwatch,
            )
        )
        logger.debug("[TimeUtilsManager] 注册正计时器工具成功")

    def _register_alarm_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        注册闹钟工具.
        """
        # 设置闹钟
        alarm_props = PropertyList(
            [
                Property(
                    "alarm_time",
                    PropertyType.STRING,
                ),
                Property(
                    "message",
                    PropertyType.STRING,
                    default_value="",
                ),
            ]
        )

        add_tool(
            (
                "time_utils.set_alarm",
                "Set an alarm for a specific time. "
                "The alarm_time should be in ISO format (e.g., '2025-01-01T08:00:00'). "
                "Use this when the user wants to: \n"
                "1. Set a wake-up alarm \n"
                "2. Schedule a reminder at a specific time \n"
                "3. Create time-based notifications \n"
                "Returns an alarm_id that can be used to cancel the alarm.",
                alarm_props,
                set_alarm,
            )
        )

        # 取消闹钟
        cancel_props = PropertyList(
            [
                Property(
                    "alarm_id",
                    PropertyType.STRING,
                )
            ]
        )

        add_tool(
            (
                "time_utils.cancel_alarm",
                "Cancel a previously set alarm by its ID. "
                "Use this when the user wants to: \n"
                "1. Cancel an existing alarm \n"
                "2. Remove a scheduled reminder",
                cancel_props,
                cancel_alarm,
            )
        )

        # 获取活动闹钟
        add_tool(
            (
                "time_utils.get_active_alarms",
                "Get information about all currently active alarms. "
                "Returns details including alarm IDs, scheduled times, messages, "
                "and time remaining for each active alarm. "
                "Use this when the user wants to: \n"
                "1. Check what alarms are currently set \n"
                "2. See upcoming alarm times \n"
                "3. Get alarm IDs for cancellation",
                PropertyList(),
                get_active_alarms,
            )
        )
        logger.debug("[TimeUtilsManager] 注册闹钟工具成功")

    def is_initialized(self) -> bool:
        """
        检查管理器是否已初始化.
        """
        return self._initialized

    def get_status(self) -> Dict[str, Any]:
        """
        获取管理器状态.
        """
        return {
            "initialized": self._initialized,
            "tools_count": 11,  # 当前注册的工具数量
            "available_tools": [
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
            ],
        }


# 全局管理器实例
_time_utils_manager = None


def get_time_utils_manager() -> TimeUtilsManager:
    """
    获取时间工具管理器单例.
    """
    global _time_utils_manager
    if _time_utils_manager is None:
        _time_utils_manager = TimeUtilsManager()
        logger.debug("[TimeUtilsManager] 创建时间工具管理器实例")
    return _time_utils_manager
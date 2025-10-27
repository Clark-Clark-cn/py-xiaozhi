"""时间工具MCP工具函数.

提供节假日查询、正计时器、闹钟等时间相关功能
"""

import json
import aiohttp
from typing import Any, Dict

from src.utils.logging_config import get_logger

from .alarm_service import get_alarm_service
from .stopwatch_service import get_stopwatch_service

logger = get_logger(__name__)

# 节假日API配置
HOLIDAY_API_BASE = "https://date.appworlds.cn"
HOLIDAY_API_WORK = f"{HOLIDAY_API_BASE}/work"  # 判断是否工作日
HOLIDAY_API_NEXT = f"{HOLIDAY_API_BASE}/next"  # 下一个节假日
HOLIDAY_API_NEXT_DAYS = f"{HOLIDAY_API_BASE}/next/days"  # 距离下一个节假日天数
HOLIDAY_API_YEAR = f"{HOLIDAY_API_BASE}/year"  # 获取一年节假日


async def get_holiday_info(args: Dict[str, Any]) -> str:
    """获取节假日信息，包括距离下个节假日的剩余时间。

    使用在线API获取实时准确的节假日信息。

    Args:
        args: 包含以下参数的字典
            - holiday_type: 节假日类型，可选 ("upcoming", "next", "is_workday", "year")
            - date: 特定日期 (YYYY-MM-DD格式)，可选
            - year: 年份 (YYYY格式)，当holiday_type为"year"时需要

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        holiday_type = args.get("holiday_type", "upcoming")

        async with aiohttp.ClientSession() as session:
            if holiday_type == "upcoming" or holiday_type == "next":
                # 获取下一个节假日信息
                date_param = f"?date={args['date']}" if args.get("date") else ""
                url = f"{HOLIDAY_API_NEXT}{date_param}"

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 200:
                            holiday_data = data["data"]
                            if holiday_data is None:
                                # 没有下一个节假日，可能已经到年底
                                return json.dumps({
                                    "success": False,
                                    "message": "当前没有更多的节假日信息"
                                }, ensure_ascii=False)
                            return json.dumps({
                                "success": True,
                                "holiday_type": "next",
                                "next_holiday": {
                                    "date": holiday_data["date"],
                                    "name": holiday_data["name"],
                                    "days": holiday_data["days"],
                                    "is_holiday": holiday_data["holiday"]
                                }
                            }, ensure_ascii=False, indent=2)
                        else:
                            return json.dumps({
                                "success": False,
                                "message": data.get("msg", "API请求失败")
                            }, ensure_ascii=False)
                    else:
                        return json.dumps({
                            "success": False,
                            "message": f"API请求失败: HTTP {response.status}"
                        }, ensure_ascii=False)

            elif holiday_type == "next_days":
                # 获取距离下一个节假日的天数
                date_param = f"?date={args['date']}" if args.get("date") else ""
                url = f"{HOLIDAY_API_NEXT_DAYS}{date_param}"

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 200:
                            days = data["data"]
                            if days is None:
                                return json.dumps({
                                    "success": False,
                                    "message": "当前没有更多的节假日信息"
                                }, ensure_ascii=False)
                            return json.dumps({
                                "success": True,
                                "holiday_type": "next_days",
                                "days_until_next_holiday": days
                            }, ensure_ascii=False, indent=2)
                        else:
                            return json.dumps({
                                "success": False,
                                "message": data.get("msg", "API请求失败")
                            }, ensure_ascii=False)
                    else:
                        return json.dumps({
                            "success": False,
                            "message": f"API请求失败: HTTP {response.status}"
                        }, ensure_ascii=False)

            elif holiday_type == "is_workday":
                # 判断指定日期是否为工作日
                date_param = f"?date={args['date']}" if args.get("date") else ""
                url = f"{HOLIDAY_API_WORK}{date_param}"

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 200:
                            workday_data = data["data"]
                            return json.dumps({
                                "success": True,
                                "holiday_type": "is_workday",
                                "date": workday_data["date"],
                                "is_workday": workday_data["work"],
                                "is_holiday": not workday_data["work"]
                            }, ensure_ascii=False, indent=2)
                        else:
                            return json.dumps({
                                "success": False,
                                "message": data.get("msg", "API请求失败")
                            }, ensure_ascii=False)
                    else:
                        return json.dumps({
                            "success": False,
                            "message": f"API请求失败: HTTP {response.status}"
                        }, ensure_ascii=False)

            elif holiday_type == "year":
                # 获取一整年的节假日信息
                year = args.get("year")
                if not year:
                    from datetime import datetime
                    year = datetime.now().year

                url = f"{HOLIDAY_API_YEAR}/{year}"

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 200:
                            return json.dumps({
                                "success": True,
                                "holiday_type": "year",
                                "year": year,
                                "holidays": data["data"]
                            }, ensure_ascii=False, indent=2)
                        else:
                            return json.dumps({
                                "success": False,
                                "message": data.get("msg", "API请求失败")
                            }, ensure_ascii=False)
                    else:
                        return json.dumps({
                            "success": False,
                            "message": f"API请求失败: HTTP {response.status}"
                        }, ensure_ascii=False)

            else:
                return json.dumps({
                    "success": False,
                    "message": f"不支持的节假日类型: {holiday_type}. 支持的类型: upcoming, next, next_days, is_workday, year"
                }, ensure_ascii=False)

    except aiohttp.ClientError as e:
        logger.error(f"网络请求错误: {e}")
        return json.dumps({
            "success": False,
            "message": f"网络请求错误: {str(e)}"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"获取节假日信息失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"获取节假日信息失败: {str(e)}"
        }, ensure_ascii=False)


async def start_stopwatch(args: Dict[str, Any]) -> str:
    """启动正计时器。

    Args:
        args: 包含以下参数的字典
            - stopwatch_id: 正计时器ID，可选（如果不提供则操作默认计时器）

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        stopwatch_id = args.get("stopwatch_id")
        if not stopwatch_id:
            return json.dumps({
                "success": False,
                "message": "请提供stopwatch_id参数"
            }, ensure_ascii=False)

        stopwatch_service = get_stopwatch_service()
        result = await stopwatch_service.start_stopwatch(stopwatch_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"启动正计时器失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"启动正计时器失败: {str(e)}"
        }, ensure_ascii=False)


async def pause_stopwatch(args: Dict[str, Any]) -> str:
    """暂停正计时器。

    Args:
        args: 包含以下参数的字典
            - stopwatch_id: 正计时器ID

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        stopwatch_id = args.get("stopwatch_id")
        if not stopwatch_id:
            return json.dumps({
                "success": False,
                "message": "请提供stopwatch_id参数"
            }, ensure_ascii=False)

        stopwatch_service = get_stopwatch_service()
        result = await stopwatch_service.pause_stopwatch(stopwatch_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"暂停正计时器失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"暂停正计时器失败: {str(e)}"
        }, ensure_ascii=False)


async def reset_stopwatch(args: Dict[str, Any]) -> str:
    """重置正计时器。

    Args:
        args: 包含以下参数的字典
            - stopwatch_id: 正计时器ID

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        stopwatch_id = args.get("stopwatch_id")
        if not stopwatch_id:
            return json.dumps({
                "success": False,
                "message": "请提供stopwatch_id参数"
            }, ensure_ascii=False)

        stopwatch_service = get_stopwatch_service()
        result = await stopwatch_service.reset_stopwatch(stopwatch_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"重置正计时器失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"重置正计时器失败: {str(e)}"
        }, ensure_ascii=False)


async def get_stopwatch_status(args: Dict[str, Any]) -> str:
    """获取正计时器当前状态。

    Args:
        args: 包含以下参数的字典
            - stopwatch_id: 正计时器ID

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        stopwatch_id = args.get("stopwatch_id")
        if not stopwatch_id:
            return json.dumps({
                "success": False,
                "message": "请提供stopwatch_id参数"
            }, ensure_ascii=False)

        stopwatch_service = get_stopwatch_service()
        result = await stopwatch_service.get_stopwatch_status(stopwatch_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"获取正计时器状态失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"获取正计时器状态失败: {str(e)}"
        }, ensure_ascii=False)


async def create_stopwatch(args: Dict[str, Any]) -> str:
    """创建一个新的正计时器。

    Args:
        args: 包含以下参数的字典
            - name: 计时器名称，可选

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        name = args.get("name", "")
        stopwatch_service = get_stopwatch_service()
        result = await stopwatch_service.create_stopwatch(name)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"创建正计时器失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"创建正计时器失败: {str(e)}"
        }, ensure_ascii=False)


async def get_all_stopwatches(args: Dict[str, Any]) -> str:
    """获取所有正计时器状态。

    Args:
        args: 空字典（此函数无需参数）

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        stopwatch_service = get_stopwatch_service()
        result = await stopwatch_service.get_all_stopwatches()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"获取所有正计时器失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"获取所有正计时器失败: {str(e)}"
        }, ensure_ascii=False)


async def delete_stopwatch(args: Dict[str, Any]) -> str:
    """删除指定的正计时器。

    Args:
        args: 包含以下参数的字典
            - stopwatch_id: 正计时器ID

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        stopwatch_id = args.get("stopwatch_id")
        if not stopwatch_id:
            return json.dumps({
                "success": False,
                "message": "请提供stopwatch_id参数"
            }, ensure_ascii=False)

        stopwatch_service = get_stopwatch_service()
        result = await stopwatch_service.delete_stopwatch(stopwatch_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"删除正计时器失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"删除正计时器失败: {str(e)}"
        }, ensure_ascii=False)


async def set_alarm(args: Dict[str, Any]) -> str:
    """设置闹钟。

    Args:
        args: 包含以下参数的字典
            - alarm_time: 闹钟时间 (ISO格式字符串，如 "2025-01-01T08:00:00")
            - message: 闹钟消息，可选

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        alarm_time = args["alarm_time"]
        message = args.get("message", "")

        alarm_service = get_alarm_service()
        result = await alarm_service.set_alarm(alarm_time, message)
        return json.dumps(result, ensure_ascii=False, indent=2)

    except KeyError as e:
        return json.dumps({
            "success": False,
            "message": f"缺少必需参数: {e}"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"设置闹钟失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"设置闹钟失败: {str(e)}"
        }, ensure_ascii=False)


async def cancel_alarm(args: Dict[str, Any]) -> str:
    """取消闹钟。

    Args:
        args: 包含以下参数的字典
            - alarm_id: 要取消的闹钟ID

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        alarm_id = args["alarm_id"]

        alarm_service = get_alarm_service()
        result = await alarm_service.cancel_alarm(alarm_id)
        return json.dumps(result, ensure_ascii=False, indent=2)

    except KeyError as e:
        return json.dumps({
            "success": False,
            "message": f"缺少必需参数: {e}"
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"取消闹钟失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"取消闹钟失败: {str(e)}"
        }, ensure_ascii=False)


async def get_active_alarms(args: Dict[str, Any]) -> str:
    """获取所有活动闹钟。

    Args:
        args: 空字典（此函数无需参数）

    Returns:
        str: JSON格式的结果字符串
    """
    try:
        alarm_service = get_alarm_service()
        result = await alarm_service.get_active_alarms()
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"获取活动闹钟失败: {e}")
        return json.dumps({
            "success": False,
            "message": f"获取活动闹钟失败: {str(e)}"
        }, ensure_ascii=False)
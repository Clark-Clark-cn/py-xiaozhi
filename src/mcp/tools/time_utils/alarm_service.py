"""闹钟服务.

管理闹钟任务的创建、执行、取消和状态查询
"""

import asyncio
import json
from asyncio import Task
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AlarmService:
    """
    闹钟服务，管理所有闹钟任务.
    """

    def __init__(self):
        # 使用字典存储活动的闹钟，键是 alarm_id，值是 AlarmTask 对象
        self._alarms: Dict[str, "AlarmTask"] = {}
        # 使用锁来保护对 _alarms 的访问，确保线程安全
        self._lock = asyncio.Lock()

    async def set_alarm(
        self, alarm_time: str, message: str = ""
    ) -> Dict[str, Any]:
        """设置一个闹钟.

        Args:
            alarm_time: 闹钟时间 (ISO格式字符串)
            message: 闹钟消息

        Returns:
            Dict[str, Any]: 包含闹钟信息的字典
        """
        try:
            # 验证时间格式
            alarm_datetime = datetime.fromisoformat(alarm_time)
            now = datetime.now()

            if alarm_datetime <= now:
                return {
                    "success": False,
                    "message": "闹钟时间不能早于当前时间"
                }

            # 生成唯一ID
            alarm_id = f"alarm_{int(asyncio.get_event_loop().time() * 1000)}"

            # 获取当前事件循环
            loop = asyncio.get_running_loop()

            async with self._lock:
                # 创建闹钟任务
                alarm_task = AlarmTask(
                    alarm_id=alarm_id,
                    alarm_time=alarm_datetime,
                    message=message,
                    service=self,
                )

                # 创建异步任务
                task = loop.create_task(alarm_task.run())
                alarm_task.task = task

                self._alarms[alarm_id] = alarm_task

            # 计算剩余时间
            time_until = alarm_datetime - now
            hours_until = int(time_until.total_seconds() // 3600)
            minutes_until = int((time_until.total_seconds() % 3600) // 60)

            logger.info(f"设置闹钟 {alarm_id}，将在 {alarm_datetime} 触发: {message}")

            return {
                "success": True,
                "message": f"闹钟 {alarm_id} 已设置，将在 {hours_until}小时{minutes_until}分钟后触发",
                "alarm_id": alarm_id,
                "alarm_time": alarm_time,
                "time_until_seconds": int(time_until.total_seconds()),
                "message": message,
            }

        except ValueError as e:
            logger.error(f"设置闹钟失败：时间格式错误: {e}")
            return {
                "success": False,
                "message": f"时间格式错误: {str(e)}"
            }
        except Exception as e:
            logger.error(f"设置闹钟失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"设置闹钟失败: {str(e)}"
            }

    async def cancel_alarm(self, alarm_id: str) -> Dict[str, Any]:
        """取消指定的闹钟.

        Args:
            alarm_id: 要取消的闹钟ID

        Returns:
            Dict[str, Any]: 取消结果
        """
        try:
            async with self._lock:
                if alarm_id in self._alarms:
                    alarm_task = self._alarms.pop(alarm_id)
                    if alarm_task.task:
                        alarm_task.task.cancel()

                    logger.info(f"闹钟 {alarm_id} 已成功取消")
                    return {
                        "success": True,
                        "message": f"闹钟 {alarm_id} 已取消",
                        "alarm_id": alarm_id,
                        "cancelled_at": datetime.now().isoformat(),
                    }
                else:
                    logger.warning(f"尝试取消不存在的闹钟 {alarm_id}")
                    return {
                        "success": False,
                        "message": f"找不到ID为 {alarm_id} 的活动闹钟",
                        "alarm_id": alarm_id,
                    }

        except Exception as e:
            logger.error(f"取消闹钟失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"取消闹钟失败: {str(e)}"
            }

    async def get_active_alarms(self) -> Dict[str, Any]:
        """获取所有活动的闹钟状态.

        Returns:
            Dict[str, Any]: 活动闹钟列表
        """
        async with self._lock:
            active_alarms = []
            now = datetime.now()

            for alarm_id, alarm_task in self._alarms.items():
                time_until = alarm_task.alarm_time - now
                if time_until.total_seconds() > 0:
                    hours_until = int(time_until.total_seconds() // 3600)
                    minutes_until = int((time_until.total_seconds() % 3600) // 60)
                    active_alarms.append({
                        "alarm_id": alarm_id,
                        "alarm_time": alarm_task.alarm_time.isoformat(),
                        "message": alarm_task.message,
                        "time_until": f"{hours_until}小时{minutes_until}分钟后",
                        "time_until_seconds": int(time_until.total_seconds()),
                        "set_time": alarm_task.set_time.isoformat(),
                    })

            return {
                "success": True,
                "total_active_alarms": len(active_alarms),
                "alarms": active_alarms,
            }

    async def cleanup_alarm(self, alarm_id: str):
        """清理已完成的闹钟任务.

        Args:
            alarm_id: 要清理的闹钟ID
        """
        async with self._lock:
            if alarm_id in self._alarms:
                del self._alarms[alarm_id]
                logger.debug(f"清理闹钟 {alarm_id}")


class AlarmTask:
    """
    单个闹钟任务.
    """

    def __init__(
        self,
        alarm_id: str,
        alarm_time: datetime,
        message: str,
        service: AlarmService,
    ):
        self.alarm_id = alarm_id
        self.alarm_time = alarm_time
        self.message = message
        self.service = service
        self.set_time = datetime.now()
        self.task: Optional[Task] = None

    async def run(self):
        """
        执行闹钟任务.
        """
        try:
            # 计算等待时间
            now = datetime.now()
            if self.alarm_time > now:
                wait_seconds = (self.alarm_time - now).total_seconds()
                await asyncio.sleep(wait_seconds)

            # 触发闹钟
            await self._trigger_alarm()

        except asyncio.CancelledError:
            logger.info(f"闹钟 {self.alarm_id} 被取消")
        except Exception as e:
            logger.error(f"闹钟 {self.alarm_id} 执行过程中出错: {e}", exc_info=True)
        finally:
            # 清理自己
            await self.service.cleanup_alarm(self.alarm_id)

    async def _trigger_alarm(self):
        """
        触发闹钟.
        """
        logger.info(f"闹钟 {self.alarm_id} 触发: {self.message}")

        try:
            # 通过TTS播报闹钟消息
            from src.application import Application

            app = Application.get_instance()
            alarm_message = self.message or f"闹钟时间到"

            print(f"闹钟：{alarm_message}")
            await app._send_text_tts(alarm_message)

            # 这里可以添加更多触发逻辑，如播放提示音等

        except Exception as e:
            logger.warning(f"闹钟 {self.alarm_id} 触发通知失败: {e}")


# 全局服务实例
_alarm_service = None


def get_alarm_service() -> AlarmService:
    """
    获取闹钟服务单例.
    """
    global _alarm_service
    if _alarm_service is None:
        _alarm_service = AlarmService()
        logger.debug("[AlarmService] 创建闹钟服务实例")
    return _alarm_service

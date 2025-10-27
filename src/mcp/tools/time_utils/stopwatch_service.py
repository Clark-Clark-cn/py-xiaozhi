"""正计时器服务.

管理正计时器任务的创建、控制和状态查询
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class StopwatchService:
    """
    正计时器服务，管理所有正计时器任务.
    """

    def __init__(self):
        # 使用字典存储活动的正计时器，键是 stopwatch_id，值是 StopwatchTask 对象
        self._stopwatches: Dict[str, "StopwatchTask"] = {}
        # 使用锁来保护对 _stopwatches 的访问，确保线程安全
        self._lock = asyncio.Lock()

    async def create_stopwatch(self, name: str = "") -> Dict[str, Any]:
        """创建一个新的正计时器.

        Args:
            name: 计时器名称，可选

        Returns:
            Dict[str, Any]: 包含计时器信息的字典
        """
        try:
            # 生成唯一ID
            stopwatch_id = f"stopwatch_{int(asyncio.get_event_loop().time() * 1000)}"

            async with self._lock:
                # 创建正计时器任务
                stopwatch_task = StopwatchTask(
                    stopwatch_id=stopwatch_id,
                    name=name or f"计时器 {stopwatch_id}",
                    service=self,
                )

                self._stopwatches[stopwatch_id] = stopwatch_task

            logger.info(f"创建正计时器 {stopwatch_id}: {stopwatch_task.name}")

            return {
                "success": True,
                "message": f"正计时器 {stopwatch_task.name} 已创建",
                "stopwatch_id": stopwatch_id,
                "name": stopwatch_task.name,
                "status": stopwatch_task.get_status(),
            }

        except Exception as e:
            logger.error(f"创建正计时器失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"创建正计时器失败: {str(e)}"
            }

    async def start_stopwatch(self, stopwatch_id: str) -> Dict[str, Any]:
        """启动指定的正计时器.

        Args:
            stopwatch_id: 正计时器ID

        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            async with self._lock:
                if stopwatch_id in self._stopwatches:
                    stopwatch_task = self._stopwatches[stopwatch_id]
                    stopwatch_task.start()
                    logger.info(f"启动正计时器 {stopwatch_id}")
                    return {
                        "success": True,
                        "message": f"正计时器 {stopwatch_task.name} 已启动",
                        "stopwatch_id": stopwatch_id,
                        "status": stopwatch_task.get_status(),
                    }
                else:
                    return {
                        "success": False,
                        "message": f"找不到ID为 {stopwatch_id} 的正计时器",
                        "stopwatch_id": stopwatch_id,
                    }

        except Exception as e:
            logger.error(f"启动正计时器失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"启动正计时器失败: {str(e)}"
            }

    async def pause_stopwatch(self, stopwatch_id: str) -> Dict[str, Any]:
        """暂停指定的正计时器.

        Args:
            stopwatch_id: 正计时器ID

        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            async with self._lock:
                if stopwatch_id in self._stopwatches:
                    stopwatch_task = self._stopwatches[stopwatch_id]
                    stopwatch_task.pause()
                    logger.info(f"暂停正计时器 {stopwatch_id}")
                    return {
                        "success": True,
                        "message": f"正计时器 {stopwatch_task.name} 已暂停",
                        "stopwatch_id": stopwatch_id,
                        "status": stopwatch_task.get_status(),
                    }
                else:
                    return {
                        "success": False,
                        "message": f"找不到ID为 {stopwatch_id} 的正计时器",
                        "stopwatch_id": stopwatch_id,
                    }

        except Exception as e:
            logger.error(f"暂停正计时器失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"暂停正计时器失败: {str(e)}"
            }

    async def reset_stopwatch(self, stopwatch_id: str) -> Dict[str, Any]:
        """重置指定的正计时器.

        Args:
            stopwatch_id: 正计时器ID

        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            async with self._lock:
                if stopwatch_id in self._stopwatches:
                    stopwatch_task = self._stopwatches[stopwatch_id]
                    stopwatch_task.reset()
                    logger.info(f"重置正计时器 {stopwatch_id}")
                    return {
                        "success": True,
                        "message": f"正计时器 {stopwatch_task.name} 已重置",
                        "stopwatch_id": stopwatch_id,
                        "status": stopwatch_task.get_status(),
                    }
                else:
                    return {
                        "success": False,
                        "message": f"找不到ID为 {stopwatch_id} 的正计时器",
                        "stopwatch_id": stopwatch_id,
                    }

        except Exception as e:
            logger.error(f"重置正计时器失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"重置正计时器失败: {str(e)}"
            }

    async def get_stopwatch_status(self, stopwatch_id: str) -> Dict[str, Any]:
        """获取指定正计时器的状态.

        Args:
            stopwatch_id: 正计时器ID

        Returns:
            Dict[str, Any]: 计时器状态
        """
        try:
            async with self._lock:
                if stopwatch_id in self._stopwatches:
                    stopwatch_task = self._stopwatches[stopwatch_id]
                    return {
                        "success": True,
                        "stopwatch_id": stopwatch_id,
                        "name": stopwatch_task.name,
                        "status": stopwatch_task.get_status(),
                    }
                else:
                    return {
                        "success": False,
                        "message": f"找不到ID为 {stopwatch_id} 的正计时器",
                        "stopwatch_id": stopwatch_id,
                    }

        except Exception as e:
            logger.error(f"获取正计时器状态失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"获取正计时器状态失败: {str(e)}"
            }

    async def get_all_stopwatches(self) -> Dict[str, Any]:
        """获取所有正计时器的状态.

        Returns:
            Dict[str, Any]: 所有计时器状态列表
        """
        try:
            async with self._lock:
                stopwatches_info = []
                for stopwatch_id, stopwatch_task in self._stopwatches.items():
                    stopwatches_info.append({
                        "stopwatch_id": stopwatch_id,
                        "name": stopwatch_task.name,
                        "status": stopwatch_task.get_status(),
                    })

                return {
                    "success": True,
                    "total_stopwatches": len(stopwatches_info),
                    "stopwatches": stopwatches_info,
                }

        except Exception as e:
            logger.error(f"获取所有正计时器失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"获取所有正计时器失败: {str(e)}"
            }

    async def delete_stopwatch(self, stopwatch_id: str) -> Dict[str, Any]:
        """删除指定的正计时器.

        Args:
            stopwatch_id: 正计时器ID

        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            async with self._lock:
                if stopwatch_id in self._stopwatches:
                    stopwatch_task = self._stopwatches.pop(stopwatch_id)
                    logger.info(f"删除正计时器 {stopwatch_id}: {stopwatch_task.name}")
                    return {
                        "success": True,
                        "message": f"正计时器 {stopwatch_task.name} 已删除",
                        "stopwatch_id": stopwatch_id,
                    }
                else:
                    return {
                        "success": False,
                        "message": f"找不到ID为 {stopwatch_id} 的正计时器",
                        "stopwatch_id": stopwatch_id,
                    }

        except Exception as e:
            logger.error(f"删除正计时器失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"删除正计时器失败: {str(e)}"
            }


class StopwatchTask:
    """
    单个正计时器任务.
    """

    def __init__(
        self,
        stopwatch_id: str,
        name: str,
        service: StopwatchService,
    ):
        self.stopwatch_id = stopwatch_id
        self.name = name
        self.service = service

        # 计时器状态
        self.start_time: Optional[float] = None
        self.paused_time: float = 0
        self.is_running = False
        self.is_paused = False
        self.create_time = datetime.now()

    def start(self):
        """启动计时器"""
        if not self.is_running:
            if self.is_paused:
                # 从暂停状态恢复
                self.start_time = asyncio.get_event_loop().time() - self.paused_time
                self.is_paused = False
            else:
                # 新启动
                self.start_time = asyncio.get_event_loop().time()
            self.is_running = True

    def pause(self):
        """暂停计时器"""
        if self.is_running and not self.is_paused:
            self.paused_time = asyncio.get_event_loop().time() - self.start_time
            self.is_paused = True

    def reset(self):
        """重置计时器"""
        self.start_time = None
        self.paused_time = 0
        self.is_running = False
        self.is_paused = False

    def get_elapsed_time(self) -> float:
        """获取经过的时间（秒）"""
        if not self.is_running:
            return self.paused_time if self.is_paused else 0

        if self.is_paused:
            return self.paused_time

        return asyncio.get_event_loop().time() - self.start_time

    def get_status(self) -> Dict[str, Any]:
        """获取计时器状态"""
        elapsed = self.get_elapsed_time()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed % 1) * 1000)

        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "elapsed_seconds": elapsed,
            "display_time": "02d",
            "total_seconds": int(elapsed),
            "create_time": self.create_time.isoformat(),
        }


# 全局服务实例
_stopwatch_service = None


def get_stopwatch_service() -> StopwatchService:
    """
    获取正计时器服务单例.
    """
    global _stopwatch_service
    if _stopwatch_service is None:
        _stopwatch_service = StopwatchService()
        logger.debug("[StopwatchService] 创建正计时器服务实例")
    return _stopwatch_service

"""Linux系统应用程序启动器.

提供Linux平台下的应用程序启动功能
"""

import os
import subprocess
from pathlib import Path

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def launch_application(app_name: str) -> bool:
    """在Linux上启动应用程序.

    Args:
        app_name: 应用程序名称

    Returns:
        bool: 启动是否成功
    """
    try:
        logger.info(f"[LinuxLauncher] 启动应用程序: {app_name}")

        # 方法1: 直接使用应用程序名称
        try:
            subprocess.Popen([app_name])
            logger.info(f"[LinuxLauncher] 直接启动成功: {app_name}")
            return True
        except (OSError, subprocess.SubprocessError):
            logger.debug(f"[LinuxLauncher] 直接启动失败: {app_name}")

        # 方法2: 使用which查找应用程序路径
        try:
            result = subprocess.run(["which", app_name], capture_output=True, text=True)
            if result.returncode == 0:
                app_path = result.stdout.strip()
                subprocess.Popen([app_path])
                logger.info(f"[LinuxLauncher] 通过which启动成功: {app_name}")
                return True
        except (OSError, subprocess.SubprocessError):
            logger.debug(f"[LinuxLauncher] which启动失败: {app_name}")

        # 方法3: 尝试通过 .desktop 桌面文件启动（优先于 xdg-open，避免把名称当作文件路径）
        desktop_id = _find_matching_desktop_id(app_name)
        if desktop_id:
            try:
                subprocess.Popen(["gtk-launch", desktop_id])
                logger.info(
                    f"[LinuxLauncher] 通过gtk-launch启动成功: {app_name} ({desktop_id})"
                )
                return True
            except (OSError, subprocess.SubprocessError):
                logger.debug(
                    f"[LinuxLauncher] gtk-launch 启动失败: {app_name} ({desktop_id})"
                )

        # 方法4: 尝试常见的应用程序路径
        common_paths = [
            f"/usr/bin/{app_name}",
            f"/usr/local/bin/{app_name}",
            f"/opt/{app_name}/{app_name}",
            f"/snap/bin/{app_name}",
        ]

        for path in common_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                logger.info(
                    f"[LinuxLauncher] 通过常见路径启动成功: {app_name} ({path})"
                )
                return True

        # 方法4: 如果看起来像文件/URL，再使用 xdg-open（避免把纯应用名当文件）
        if _looks_like_path_or_url(app_name):
            try:
                subprocess.Popen(["xdg-open", app_name])
                logger.info(f"[LinuxLauncher] 使用xdg-open启动成功: {app_name}")
                return True
            except (OSError, subprocess.SubprocessError):
                logger.debug(f"[LinuxLauncher] xdg-open启动失败: {app_name}")

        logger.warning(f"[LinuxLauncher] 所有Linux启动方法都失败了: {app_name}")
        return False

    except Exception as e:
        logger.error(f"[LinuxLauncher] Linux启动失败: {e}")
        return False


def _looks_like_path_or_url(target: str) -> bool:
    """判断字符串是否像路径或URL，避免将纯名称传给 xdg-open。

    - 包含路径分隔符 / 或以 .desktop/.AppImage 结尾
    - 以常见协议开头如 http(s):// file:// ftp:// 等
    """
    t = target.strip()
    if not t:
        return False

    if "/" in t:
        return True
    if t.endswith((".desktop", ".AppImage")):
        return True
    lower = t.lower()
    if any(lower.startswith(p) for p in ("http://", "https://", "file://", "ftp://")):
        return True
    return False


def _find_matching_desktop_id(app_name: str) -> str | None:
    """在常见目录中查找与应用名匹配的 .desktop 文件并返回 desktop-id。

    匹配策略：
    - 文件名等于/包含 app_name（不区分大小写）
    - Desktop 文件中的 Name 或 Exec 含有 app_name
    返回 desktop-id（文件名去掉 .desktop 后的部分），找不到返回 None。
    """
    try:
        candidates: list[Path] = []
        desktop_dirs = [
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
            Path.home() / ".local/share/applications",
        ]

        name_l = app_name.lower()

        for d in desktop_dirs:
            if not d.exists():
                continue
            for f in d.glob("*.desktop"):
                fname = f.name.lower()
                if name_l == fname[:-8] or name_l in fname:
                    candidates.append(f)

        # 次优：解析内容匹配 Name/Exec
        if not candidates:
            for d in desktop_dirs:
                if not d.exists():
                    continue
                for f in d.glob("*.desktop"):
                    try:
                        txt = f.read_text(encoding="utf-8", errors="ignore")
                        tl = txt.lower()
                        if f"name={name_l}" in tl or f"exec={name_l}" in tl or name_l in tl:
                            candidates.append(f)
                    except Exception:
                        pass

        if not candidates:
            return None

        # 取第一个候选作为 desktop-id
        desktop_file = candidates[0]
        return desktop_file.stem
    except Exception:
        return None

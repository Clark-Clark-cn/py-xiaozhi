"""红外控制工具模块入口."""

from .manager import IRControlToolsManager


def get_ir_manager():
    """
    获取红外控制工具管理器实例.
    """
    return IRControlToolsManager()

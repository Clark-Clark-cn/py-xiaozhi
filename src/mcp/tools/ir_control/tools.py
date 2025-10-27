"""红外学习/控制 工具实现.

包装 mcps/ir_control/ir_control.py 的能力，作为 MCP 工具对外提供。
"""

import json
import sys
from types import SimpleNamespace
from typing import Any, Dict

from src.utils.logging_config import get_logger

# 添加 mcps 路径以便导入现有硬件控制脚本
mcps_path = "/home/orangepi/super-orangepi/mcps"
if mcps_path not in sys.path:
    sys.path.insert(0, mcps_path)

# 导入现有 IR 控制脚本
from ir_control.ir_control import execute_command  # type: ignore
import serial  # pyserial

logger = get_logger(__name__)


def _run_ir_command(ns: SimpleNamespace) -> str:
    """
    执行一次 IR 命令并返回文本结果。统一打开/关闭串口与异常处理。
    """
    try:
        ser = serial.Serial(ns.port, ns.baud, timeout=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"无法打开串口 {ns.port}: {e}"
        }, ensure_ascii=False)

    try:
        result = execute_command(ser, ns)
        return json.dumps({
            "success": True,
            "message": result
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"[IRTools] 执行命令失败: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)
    finally:
        try:
            ser.close()
        except Exception:
            pass


def _make_ns(port: str, baud: int, **kwargs) -> SimpleNamespace:
    """构造与 ir_control.execute_command 兼容的参数对象。"""
    # 所有支持的参数，默认 None/False
    base = dict(
        port=port,
        baud=baud,
        learn_internal=None,
        send_internal=None,
        learn_external=False,
        send_external_hex=None,
        send_external_file=None,
        set_baud=None,
        get_baud=False,
        set_address=None,
        get_address=False,
        reset=False,
        format=False,
        set_power_send=None,
        get_power_send=None,
        set_power_delay=None,
        get_power_delay=False,
        write_internal=None,
        read_internal=None,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


# 下面是 MCP 工具回调封装
async def ir_learn_internal_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), learn_internal=int(args["index"]))
    return _run_ir_command(ns)


async def ir_send_internal_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), send_internal=int(args["index"]))
    return _run_ir_command(ns)


async def ir_read_internal_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), read_internal=int(args["index"]))
    return _run_ir_command(ns)


async def ir_write_internal_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(
        args["port"],
        int(args["baud"]),
        write_internal=[str(int(args["index"])), str(args["hex_data"])],
    )
    return _run_ir_command(ns)


async def ir_learn_external_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), learn_external=True)
    return _run_ir_command(ns)


async def ir_send_external_hex_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), send_external_hex=str(args["hex_data"]))
    return _run_ir_command(ns)


async def ir_send_external_file_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), send_external_file=str(args["filename"]))
    return _run_ir_command(ns)


async def ir_get_baud_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), get_baud=True)
    return _run_ir_command(ns)


async def ir_set_baud_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), set_baud=int(args["baud_index"]))
    return _run_ir_command(ns)


async def ir_get_address_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), get_address=True)
    return _run_ir_command(ns)


async def ir_set_address_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), set_address=str(args["addr_hex"]))
    return _run_ir_command(ns)


async def ir_reset_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), reset=True)
    return _run_ir_command(ns)


async def ir_format_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), format=True)
    return _run_ir_command(ns)


async def ir_set_power_send_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(
        args["port"],
        int(args["baud"]),
        set_power_send=[str(int(args["index"])), str(int(args["flag"]))],
    )
    return _run_ir_command(ns)


async def ir_get_power_send_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), get_power_send=int(args["index"]))
    return _run_ir_command(ns)


async def ir_set_power_delay_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), set_power_delay=int(args["seconds"]))
    return _run_ir_command(ns)


async def ir_get_power_delay_wrapper(args: Dict[str, Any]) -> str:
    ns = _make_ns(args["port"], int(args["baud"]), get_power_delay=True)
    return _run_ir_command(ns)

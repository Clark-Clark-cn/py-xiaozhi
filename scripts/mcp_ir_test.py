#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP IR 工具测试脚本

功能：
- 启动内嵌 MCP 服务器（非网络进程），注册全部工具
- 发送 initialize 和 tools/list
- 调用指定 IR 工具（默认：ir.get_baud）并打印响应

使用示例：
  python scripts/mcp_ir_test.py                 # 默认调用 ir.get_baud
  python scripts/mcp_ir_test.py --tool ir.get_baud
  python scripts/mcp_ir_test.py --tool ir.send_internal --args '{"index":0}'
  python scripts/mcp_ir_test.py --tool ir.write_internal --args '{"index":1,"hex_data":"85 01 1F"}'
  python scripts/mcp_ir_test.py --tool ir.get_baud --args '{"port":"/dev/ttyS1","baud":115200}'

注意：需要硬件已连接且串口权限正确。
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# 将项目根目录加入 sys.path，确保可导入 src.*
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.mcp.mcp_server import McpServer  # noqa: E402
from src.utils.logging_config import setup_logging, get_logger  # noqa: E402

logger = get_logger(__name__)


class Collector:
    """收集 MCP 响应的简单回调。"""

    def __init__(self) -> None:
        self.messages: List[Dict[str, Any]] = []

    async def on_send(self, payload: str):
        try:
            obj = json.loads(payload)
        except Exception:
            obj = {"raw": payload}
        self.messages.append(obj)
        print("\n==== MCP Response ====")
        print(json.dumps(obj, ensure_ascii=False, indent=2))
        print("======================\n")


async def main():
    parser = argparse.ArgumentParser(description="MCP IR 工具测试")
    parser.add_argument(
        "--tool",
        default="ir.get_baud",
        help="要调用的工具名称（默认 ir.get_baud）",
    )
    parser.add_argument(
        "--args",
        default="{}",
        help='传递给工具的JSON参数字符串，例如 {"index":0}',
    )
    args = parser.parse_args()

    # 初始化日志
    setup_logging()

    # 构建 MCP Server
    server = McpServer.get_instance()

    # 收集响应的回调
    collector = Collector()
    server.set_send_callback(collector.on_send)

    # 注册通用工具（包含我们新增的 IR 工具）
    server.add_common_tools()

    # 发送 initialize
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "capabilities": {}
        },
    }
    print("\n>>>> MCP Request: initialize")
    print(json.dumps(init_req, ensure_ascii=False, indent=2))
    await server.parse_message(init_req)

    # 列出工具
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    print("\n>>>> MCP Request: tools/list")
    print(json.dumps(list_req, ensure_ascii=False, indent=2))
    await server.parse_message(list_req)

    # 调用指定工具
    try:
        tool_args = json.loads(args.args)
        if not isinstance(tool_args, dict):
            raise ValueError("--args 必须是JSON对象字符串")
    except Exception as e:
        print(f"参数解析失败: {e}")
        return 2

    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": args.tool,
            "arguments": tool_args,
        },
    }
    print(f"\n>>>> MCP Request: tools/call -> {args.tool}")
    print(json.dumps(call_req, ensure_ascii=False, indent=2))
    await server.parse_message(call_req)

    # 简要判定
    # 在收到的第三条响应中检查是否包含 result 或 error
    results = [m for m in collector.messages if m.get("id") == 3]
    if not results:
        print("未收到 tools/call 的响应")
        return 1

    resp = results[-1]
    if "error" in resp:
        print("工具调用失败")
        return 1
    else:
        print("工具调用成功")
        return 0


if __name__ == "__main__":
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("用户中断")
        exit(130)

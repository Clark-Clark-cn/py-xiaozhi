"""红外学习/控制 工具管理器.

负责 IR 工具的初始化、配置和 MCP 工具注册
"""

from src.utils.logging_config import get_logger

from .tools import (
    ir_learn_internal_wrapper,
    ir_send_internal_wrapper,
    ir_learn_external_wrapper,
    ir_send_external_hex_wrapper,
    ir_send_external_file_wrapper,
    ir_read_internal_wrapper,
    ir_write_internal_wrapper,
    ir_get_baud_wrapper,
    ir_set_baud_wrapper,
    ir_get_address_wrapper,
    ir_set_address_wrapper,
    ir_reset_wrapper,
    ir_format_wrapper,
    ir_set_power_send_wrapper,
    ir_get_power_send_wrapper,
    ir_set_power_delay_wrapper,
    ir_get_power_delay_wrapper,
)

logger = get_logger(__name__)


class IRControlToolsManager:
    """
    红外控制工具管理器.
    """

    def __init__(self):
        self._initialized = False
        logger.info("[IRManager] 红外控制工具管理器初始化")

    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        初始化并注册所有 IR 工具.
        """
        try:
            logger.info("[IRManager] 开始注册红外控制工具")

            # 通用参数定义：串口与波特率
            def common_props(PropertyList, Property, PropertyType):
                return PropertyList(
                    [
                        Property("port", PropertyType.STRING, default_value="/dev/ttyS1"),
                        Property("baud", PropertyType.INTEGER, default_value=115200, min_value=9600, max_value=1152000),
                    ]
                )

            # 1) 内部学习/发送/读写
            add_tool(
                (
                    "ir.learn_internal",
                    "进入内部学习模式并将学习到的编码保存到模块内部存储。参数：index(0-6)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("index", PropertyType.INTEGER, min_value=0, max_value=6),
                        ]
                    ),
                    ir_learn_internal_wrapper,
                )
            )

            add_tool(
                (
                    "ir.send_internal",
                    "发送模块内部存储的红外编码。参数：index(0-6)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("index", PropertyType.INTEGER, min_value=0, max_value=6),
                        ]
                    ),
                    ir_send_internal_wrapper,
                )
            )

            add_tool(
                (
                    "ir.read_internal",
                    "读取模块内部存储的红外编码并返回十六进制字符串。参数：index(0-6)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("index", PropertyType.INTEGER, min_value=0, max_value=6),
                        ]
                    ),
                    ir_read_internal_wrapper,
                )
            )

            add_tool(
                (
                    "ir.write_internal",
                    "将十六进制红外编码写入模块内部存储。参数：index(0-6), hex_data(字符串)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("index", PropertyType.INTEGER, min_value=0, max_value=6),
                            Property("hex_data", PropertyType.STRING),
                        ]
                    ),
                    ir_write_internal_wrapper,
                )
            )

            # 2) 外部学习/发送
            add_tool(
                (
                    "ir.learn_external",
                    "进入外部学习模式，学习完成后将编码保存为文件，返回保存结果信息。",
                    common_props(PropertyList, Property, PropertyType),
                    ir_learn_external_wrapper,
                )
            )

            add_tool(
                (
                    "ir.send_external_hex",
                    "发送外部十六进制红外编码。参数：hex_data(字符串)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("hex_data", PropertyType.STRING),
                        ]
                    ),
                    ir_send_external_hex_wrapper,
                )
            )

            add_tool(
                (
                    "ir.send_external_file",
                    "从文件读取十六进制红外编码并发送。参数：filename(字符串)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("filename", PropertyType.STRING),
                        ]
                    ),
                    ir_send_external_file_wrapper,
                )
            )

            # 3) 系统设置
            add_tool(
                (
                    "ir.get_baud",
                    "获取模块当前波特率。",
                    common_props(PropertyList, Property, PropertyType),
                    ir_get_baud_wrapper,
                )
            )
            add_tool(
                (
                    "ir.set_baud",
                    "设置模块波特率。参数：baud_index(0=9600,1=19200,2=38400,3=57600,4=115200)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("baud_index", PropertyType.INTEGER, min_value=0, max_value=4),
                        ]
                    ),
                    ir_set_baud_wrapper,
                )
            )

            add_tool(
                (
                    "ir.get_address",
                    "获取模块地址。",
                    common_props(PropertyList, Property, PropertyType),
                    ir_get_address_wrapper,
                )
            )
            add_tool(
                (
                    "ir.set_address",
                    "设置模块地址(00-FE)。参数：addr_hex(两位十六进制字符串)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("addr_hex", PropertyType.STRING),
                        ]
                    ),
                    ir_set_address_wrapper,
                )
            )

            add_tool(
                (
                    "ir.reset",
                    "复位模块。",
                    common_props(PropertyList, Property, PropertyType),
                    ir_reset_wrapper,
                )
            )
            add_tool(
                (
                    "ir.format",
                    "格式化模块。",
                    common_props(PropertyList, Property, PropertyType),
                    ir_format_wrapper,
                )
            )

            # 4) 上电行为
            add_tool(
                (
                    "ir.set_power_send",
                    "设置上电发送状态。参数：index(0-6), flag(0或1)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("index", PropertyType.INTEGER, min_value=0, max_value=6),
                            Property("flag", PropertyType.INTEGER, min_value=0, max_value=1),
                        ]
                    ),
                    ir_set_power_send_wrapper,
                )
            )
            add_tool(
                (
                    "ir.get_power_send",
                    "获取上电发送状态。参数：index(0-6)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("index", PropertyType.INTEGER, min_value=0, max_value=6),
                        ]
                    ),
                    ir_get_power_send_wrapper,
                )
            )

            add_tool(
                (
                    "ir.set_power_delay",
                    "设置上电发送延时(秒, 0-65536)",
                    PropertyList(
                        [
                            *common_props(PropertyList, Property, PropertyType).properties,
                            Property("seconds", PropertyType.INTEGER, min_value=0, max_value=65536),
                        ]
                    ),
                    ir_set_power_delay_wrapper,
                )
            )

            add_tool(
                (
                    "ir.get_power_delay",
                    "获取上电发送延时(秒)",
                    common_props(PropertyList, Property, PropertyType),
                    ir_get_power_delay_wrapper,
                )
            )

            self._initialized = True
            logger.info("[IRManager] 红外控制工具注册完成")

        except Exception as e:
            logger.error(f"[IRManager] 红外控制工具注册失败: {e}", exc_info=True)
            raise

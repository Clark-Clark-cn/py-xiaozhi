from typing import List, Optional, Sequence, Tuple

import sounddevice as sd


def list_devices() -> List[Tuple[int, str, int, int, str]]:
    """列出可用音频设备。

    Returns:
        列表项: (index, name, max_output_channels, max_input_channels, hostapi_name)
    """
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    items: List[Tuple[int, str, int, int, str]] = []
    for i, d in enumerate(devices):
        host_name = hostapis[d["hostapi"]]["name"] if 0 <= d["hostapi"] < len(hostapis) else "?"
        items.append(
            (
                i,
                d.get("name", f"device-{i}"),
                int(d.get("max_output_channels", 0)),
                int(d.get("max_input_channels", 0)),
                host_name,
            )
        )
    return items


def _name_match(name: str, keywords: Sequence[str]) -> bool:
    n = name or ""
    return any(k.lower() in n.lower() for k in keywords)


def find_device_index_by_name(
    keywords: Sequence[str], require_output: bool = True, require_input: bool = False
) -> Optional[int]:
    """按名称关键词匹配设备索引。

    Args:
        keywords: 名称关键词列表（任一匹配即可）。
        require_output: 仅选择支持输出的设备。
        require_input: 仅选择支持输入的设备。

    Returns:
        设备索引或 None。
    """
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        name = d.get("name", "")
        if not _name_match(name, keywords):
            continue
        out_ok = int(d.get("max_output_channels", 0)) > 0
        in_ok = int(d.get("max_input_channels", 0)) > 0
        if require_output and not out_ok:
            continue
        if require_input and not in_ok:
            continue
        return i
    return None


def choose_output_device(
    preferred_index: Optional[int] = None,
    name_keywords: Sequence[str] = ("ES8388", "hw:3", "rockchip,es8388"),
) -> Optional[int]:
    """选择输出设备：优先使用配置索引 -> 名称匹配 -> 系统默认 -> 第一个可输出。

    Returns:
        设备索引或 None（None 代表使用系统默认）。
    """
    try:
        devices = sd.query_devices()
        # 1) 配置索引可用则用之
        if isinstance(preferred_index, int) and 0 <= preferred_index < len(devices):
            d = devices[preferred_index]
            if int(d.get("max_output_channels", 0)) > 0:
                return preferred_index
        # 2) 名称匹配（如 ES8388）
        idx = find_device_index_by_name(name_keywords, require_output=True)
        if idx is not None:
            return idx
        # 3) 系统默认（None）——让 sounddevice 选择
        # 注意：None 由调用方传给 stream 的 device 参数即可
        # 4) 最后：第一个可输出设备
        for i, d in enumerate(devices):
            if int(d.get("max_output_channels", 0)) > 0:
                return i
    except Exception:
        pass
    return None


def choose_input_device(
    preferred_index: Optional[int] = None,
    name_keywords: Sequence[str] = ("ES8388", "hw:3", "rockchip,es8388"),
) -> Optional[int]:
    """选择输入设备：优先使用配置索引 -> 名称匹配 -> 系统默认 -> 第一个可输入。

    Returns:
        设备索引或 None（None 代表使用系统默认）。
    """
    try:
        devices = sd.query_devices()
        if isinstance(preferred_index, int) and 0 <= preferred_index < len(devices):
            d = devices[preferred_index]
            if int(d.get("max_input_channels", 0)) > 0:
                return preferred_index
        idx = find_device_index_by_name(name_keywords, require_output=False, require_input=True)
        if idx is not None:
            return idx
        for i, d in enumerate(devices):
            if int(d.get("max_input_channels", 0)) > 0:
                return i
    except Exception:
        pass
    return None

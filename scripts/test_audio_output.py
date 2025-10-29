#!/usr/bin/env python3
import json
import os
import sys
import math
import struct
import argparse
import time

import pyaudio

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "config.json"
)

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        audio = cfg.get("AUDIO_DEVICES", {})
        return {
            "device_index": int(audio.get("output_device_id", 2)),
            "sample_rate": int(audio.get("output_sample_rate", 48000)),
        }
    except Exception as e:
        print(f"[WARN] 读取配置失败，使用默认值: {e}")
        return {"device_index": 2, "sample_rate": 48000}

def list_devices(p):
    print("可用音频设备列表：")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        host = p.get_host_api_info_by_index(info["hostApi"])["name"]
        print(f"  [{i}] {info.get('name')} | out:{info.get('maxOutputChannels')} in:{info.get('maxInputChannels')} | host:{host}")

def find_device_index_by_name(p, keywords=("ES8388", "es8388", "hw:3,0")):
    for i in range(p.get_device_count()):
        name = p.get_device_info_by_index(i).get("name", "")
        if any(k in name for k in keywords):
            if p.get_device_info_by_index(i).get("maxOutputChannels", 0) > 0:
                return i
    return None

def gen_sine_chunk(freq, rate, frames, amplitude=0.25, phase0=0.0, channels=2):
    phase = phase0
    inc = 2.0 * math.pi * freq / rate
    pack = struct.pack
    buf = bytearray()
    for _ in range(frames):
        s = int(amplitude * 32767 * math.sin(phase))
        if channels == 2:
            buf += pack("<hh", s, s)
        else:
            buf += pack("<h", s)
        phase += inc
        if phase > 2.0 * math.pi:
            phase -= 2.0 * math.pi
    return bytes(buf), phase

def open_stream_with_fallback(p, device_index, rate, channels, frames_per_buffer=1024):
    import pyaudio
    # 尝试 (rate, channels) -> (44100, same channels) -> (rate, 1ch) -> (44100, 1ch)
    attempts = [
        (rate, channels),
        (44100, channels) if rate != 44100 else None,
        (rate, 1) if channels != 1 else None,
        (44100, 1) if rate != 44100 or channels != 1 else None,
    ]
    attempts = [a for a in attempts if a is not None]
    last_err = None
    for r, ch in attempts:
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=ch,
                rate=r,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=frames_per_buffer,
            )
            return stream, r, ch
        except Exception as e:
            last_err = e
    raise last_err

def main():
    cfg = load_config()

    parser = argparse.ArgumentParser(description="最小扬声器测试（PyAudio）")
    parser.add_argument("--device", type=int, default=cfg["device_index"], help="输出设备索引，-1=自动匹配ES8388")
    parser.add_argument("--rate", type=int, default=cfg["sample_rate"], help="采样率")
    parser.add_argument("--freq", type=float, default=440.0, help="测试音频频率(Hz)")
    parser.add_argument("--duration", type=float, default=2.0, help="播放时长(秒)")
    parser.add_argument("--list", action="store_true", help="仅列出设备，不播放")
    args = parser.parse_args()

    p = pyaudio.PyAudio()

    if args.list:
        list_devices(p)
        p.terminate()
        return

    # 自动寻找 ES8388
    if args.device < 0:
        idx = find_device_index_by_name(p)
        if idx is None:
            print("[ERROR] 未找到 ES8388 输出设备，使用 --list 查看设备并手动指定 --device")
            list_devices(p)
            p.terminate()
            sys.exit(1)
        args.device = idx

    try:
        info = p.get_device_info_by_index(args.device)
    except Exception as e:
        print(f"[ERROR] 获取设备索引 {args.device} 信息失败: {e}")
        list_devices(p)
        p.terminate()
        sys.exit(1)

    host = p.get_host_api_info_by_index(info["hostApi"])["name"]
    out_ch = int(info.get("maxOutputChannels", 0))
    in_ch = int(info.get("maxInputChannels", 0))
    print(f"将使用输出设备 [{args.device}] {info.get('name')} | out:{out_ch} in:{in_ch}, rate:{args.rate}, host:{host}")

    if out_ch <= 0:
        print("[ERROR] 该设备不支持输出，请换一个索引。可用设备如下：")
        list_devices(p)
        p.terminate()
        sys.exit(2)

    channels = 2 if out_ch >= 2 else 1
    frames_per_buffer = 1024

    try:
        stream, used_rate, used_ch = open_stream_with_fallback(
            p, args.device, args.rate, channels, frames_per_buffer
        )
    except Exception as e:
        print(f"[ERROR] 打开输出流失败: {e}")
        print("提示：若看到 ALSA 插件缺失日志，安装 libasound2-plugins；或试 --device 5/8（sysdefault/pulse）。")
        list_devices(p)
        p.terminate()
        sys.exit(3)

    print(f"实际使用 rate={used_rate}, channels={used_ch} 播放 {args.freq}Hz 正弦波 {args.duration} 秒...")
    remaining = args.duration
    phase = 0.0
    try:
        while remaining > 0:
            frames = min(frames_per_buffer, int(remaining * used_rate))
            data, phase = gen_sine_chunk(args.freq, used_rate, frames, amplitude=0.4, phase0=phase, channels=used_ch)
            stream.write(data)
            remaining -= frames / float(used_rate)

        # 再播放一个“滴”声（短促方波），便于确认
        for _ in range(10):
            # 40ms on, 60ms off
            on_frames = int(0.04 * used_rate)
            off_frames = int(0.06 * used_rate)
            tone, _ = gen_sine_chunk(1000, used_rate, on_frames, amplitude=0.5, phase0=0.0, channels=used_ch)
            silence = b"\x00\x00" * (on_frames if used_ch == 1 else on_frames * 2)
            stream.write(tone)
            stream.write(silence)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    print("完成。")

if __name__ == "__main__":
    main()
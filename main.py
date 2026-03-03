#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
批量视频转 AV1 编码脚本 (智选参数版)
使用 QSVEncC64 + Intel Arc 770 GPU 硬件加速
特性：自动识别分辨率并调整 ICQ、Tile 与参考帧
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import timedelta

# ──────────────────────────────────────────────
# 配置区
# ──────────────────────────────────────────────

QSVENC = "QSVEncC64"
FFPROBE = "ffprobe"  # 用于探测视频信息

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".ts", ".m2ts", ".wmv", ".flv", ".webm"}

# ──────────────────────────────────────────────
# 核心逻辑：动态参数生成
# ──────────────────────────────────────────────

def get_video_info(input_file: Path) -> dict | None:
    """使用 ffprobe 获取视频宽度、高度及色深"""
    cmd = [
        FFPROBE, "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,pix_fmt",
        "-of", "json", str(input_file)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout)
        if not data.get("streams"): return None
        
        stream = data["streams"][0]
        return {
            "width": int(stream.get("width", 0)),
            "height": int(stream.get("height", 0)),
            "is_10bit": "10p" in stream.get("pix_fmt", "")
        }
    except Exception as e:
        print(f"  [!] 探测元数据失败: {e}")
        return None

def select_params(info: dict | None) -> list[str]:
    """根据分辨率动态调整 ICQ、Tile 和参考帧"""
    # 基础通用参数
    params = [
        "--avhw", "-c", "av1", "-u", "best",
        "--la-depth", "60", "--b-pyramid", "--bframes", "8",
        "--audio-copy", "--sub-copy", "--chapter-copy", "--data-copy",
        "--video-metadata", "copy", "--audio-metadata", "copy"
    ]

    # 默认值 (1080p 级别)
    icq, t_row, t_col, ref = "26", "1", "2", "4"
    width = info["width"] if info else 1920

    # 逻辑分级
    if width >= 3840:    # 4K 级别
        icq, t_row, t_col, ref = "32", "2", "4", "6"
    elif width >= 1920:  # 1080p 级别
        icq, t_row, t_col, ref = "26", "1", "2", "4"
    else:                # 720p 及以下
        icq, t_row, t_col, ref = "23", "1", "1", "3"

    params.extend(["--icq", icq, "--tile-row", t_row, "--tile-col", t_col, "--ref", ref])
    
    # 色深适配
    if info and info["is_10bit"]:
        params.extend(["--output-depth", "10", "--dhdr10-info", "copy"])
    else:
        params.extend(["--output-depth", "8"])

    return params

# ──────────────────────────────────────────────
# 执行逻辑
# ──────────────────────────────────────────────

def encode_video(input_file: Path, output_file: Path) -> tuple[bool, str]:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. 动态获取信息并选择参数
    info = get_video_info(input_file)
    dynamic_params = select_params(info)
    
    res_str = f"{info['width']}x{info['height']}" if info else "Unknown"

    cmd = [QSVENC, "-i", str(input_file), "-o", str(output_file), *dynamic_params]

    start = time.monotonic()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        elapsed = time.monotonic() - start
        
        if result.returncode != 0:
            return False, f"Error: {result.stderr.strip()[-200:]}"

        in_mb, out_mb = input_file.stat().st_size / 1e6, output_file.stat().st_size / 1e6
        ratio = out_mb / in_mb * 100 if in_mb > 0 else 0
        return True, f"{res_str} | {elapsed:.1f}s | {in_mb:.1f}MB -> {out_mb:.1f}MB ({ratio:.1f}%)"
    except Exception as e:
        return False, str(e)

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <input_dir> <output_dir>")
        sys.exit(1)

    in_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    videos = [p for p in in_dir.rglob("*") if p.suffix.lower() in VIDEO_EXTENSIONS]
    
    print(f"🚀 开始处理 {len(videos)} 个视频...\n" + "─"*50)

    for idx, video in enumerate(videos, 1):
        rel_path = video.relative_to(in_dir)
        target = out_dir / rel_path.with_suffix(".mkv")
        
        print(f"[{idx}/{len(videos)}] Processing: {rel_path.name}")
        
        if target.exists():
            print("  - Skip: File exists.")
            continue

        ok, msg = encode_video(video, target)
        print(f"  {'✓ Success' if ok else '✗ Failed'}: {msg}")

if __name__ == "__main__":
    main()
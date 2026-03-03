# Arc AV1 Transcoder

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Hardware](https://img.shields.io/badge/Hardware-Intel%20Arc%20A770-orange.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个基于 **QSVEncC** 和 **Intel Arc 770** 硬件加速的批量视频转码脚本。该工具能够自动探测源视频的分辨率、色深等元数据，动态调整编码参数（ICQ, Tiles, Ref Frames），实现画质与体积的最佳平衡。

## 核心特性

- **智能参数调节**：针对 4K、1080p 及以下分辨率自动匹配最优 ICQ 和并行 Tile 数。
- **HDR 适配**：自动识别 10-bit 源文件，完整保留 HDR10/Metadata 信息。
- ⚡ **极速转码**：充分压榨 Intel Arc GPU 的 AV1 硬件编码单元。
- 📦 **现代工具链**：集成 `uv` 管理依赖，实现秒级环境搭建。

---

## 快速开始

### 1. 环境准备

确保你的系统已安装以下组件：
- **Intel 图显驱动**：建议更新至最新版以获得最佳 AV1 支持。
- **QSVEncC**：[Rigaya/QSVEnc](https://github.com/rigaya/QSVEnc/releases) (请将其路径加入系统 PATH)。
- **FFmpeg/ffprobe**：用于视频元数据探测。

### 2. 安装 Python 环境管理器 `uv`

我们推荐使用 [uv](https://github.com/astral-sh/uv) 来运行脚本，它比传统 pip 快 10-100 倍。

```powershell
# Windows (PowerShell)
powershell -c "irm [https://astral-sh.uv.io/install.ps1](https://astral-sh.uv.io/install.ps1) | iex"

# macOS/Linux
curl -LsSf [https://astral-sh.uv.io/install.sh](https://astral-sh.uv.io/install.sh) | sh

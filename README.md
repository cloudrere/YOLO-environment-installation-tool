# YOLO 环境安装工具

这是一个面向 Windows 用户的 YOLO 环境安装工具，用来帮助用户自动检测本机环境，并创建可用于 Ultralytics YOLO 的 Conda 环境。软件提供中文图形界面，适合不熟悉命令行的用户快速完成环境安装、检查和卸载。

## 主要功能

- 自动检测 Windows 系统、Conda、显卡、CUDA 和磁盘信息。
- 支持一键安装 Miniconda。
- 支持创建 YOLO Conda 环境。
- 支持 Python 版本选择，可选 `3.10`、`3.11`、`3.12`，也可以手动输入版本号。
- 支持安装 PyTorch、Ultralytics 和 Jupyter。
- 支持跳过 PyTorch 或 Ultralytics 安装，并在跳过前检测当前环境是否已安装。
- 支持安装、卸载、检测等操作的进度显示。
- 支持取消长时间运行的安装任务。
- 支持自定义删除 Conda 环境。
- 支持安装过程日志查看。
- 支持 Windows 可执行文件打包发布。

## 适用环境

- Windows 10 / Windows 11
- 64 位 Windows 系统
- Anaconda 或 Miniconda
- NVIDIA GPU 可选，没有 NVIDIA GPU 时可安装 CPU 版本环境

如果电脑还没有 Conda，可以在软件检测页使用“一键安装 Miniconda”功能。

## 软件下载与运行

打包后的软件位于：

```text
dist\YoloInstaller.exe
```

双击 `YoloInstaller.exe` 即可运行。该程序本身不需要安装到系统中。

如果你是从源码运行，可以使用：

```powershell
python main.py
```

或显式启动图形界面：

```powershell
python main.py --gui
```

## 基本使用流程

1. 打开 `YoloInstaller.exe`。
2. 在检测页查看系统、Conda、显卡、CUDA 和磁盘信息。
3. 如果没有检测到 Conda，可点击“一键安装 Miniconda”。
4. 进入安装配置页。
5. 设置环境名称，例如 `yolo-env`。
6. 选择 Python 版本，推荐优先使用 `3.10`。
7. 确认 Conda 安装目录。
8. 按需选择是否安装 PyTorch、Ultralytics、Jupyter。
9. 点击开始安装，等待进度条完成。
10. 安装完成后，可在 Conda 中激活环境并使用 YOLO。

激活环境示例：

```powershell
conda activate yolo-env
```

验证 Ultralytics：

```powershell
yolo version
```

或：

```powershell
python -c "import ultralytics; print(ultralytics.__version__)"
```

## Conda 安装目录说明

界面中的“Conda 安装目录”指的是 Anaconda 或 Miniconda 的根目录，不是 YOLO 项目目录，也不是软件本体目录。

例如检测到 Conda 程序位于：

```text
E:\software\ADeepLearning\Anaconda\Scripts\conda.exe
```

那么 Conda 安装目录就是：

```text
E:\software\ADeepLearning\Anaconda
```

创建的 YOLO 环境通常会位于：

```text
E:\software\ADeepLearning\Anaconda\envs\yolo-env
```

## 安装目录建议

不建议把 Conda 或 YOLO 环境安装到 C 盘，尤其是系统盘空间较小或权限限制较多时。推荐使用 D 盘、E 盘等非系统盘，并尽量使用英文路径，例如：

```text
D:\Miniconda3
E:\ADeepLearning\Anaconda
```

不推荐使用中文路径、空格路径或特殊符号路径，以减少第三方包安装失败的概率。

## 关于 PyTorch 和 CUDA

软件会检测 NVIDIA 显卡和 CUDA 信息，并根据内置规则选择合适的 PyTorch 安装方案。

如果没有检测到 NVIDIA GPU，或 CUDA 条件不满足，软件可能会选择 CPU 版本 PyTorch。这是正常行为，CPU 版本也可以运行 YOLO，只是训练和推理速度通常会慢一些。

如果你已经提前安装了 PyTorch，可以勾选跳过 PyTorch 安装。软件会先检测当前环境中是否存在 PyTorch；如果没有检测到，会在界面中给出提示。

## 关于 Ultralytics

Ultralytics 可通过 pip 安装：

```powershell
pip install -U ultralytics
```

软件会自动在目标 Conda 环境中执行安装。也可以选择跳过 Ultralytics 安装；跳过前软件会检测当前环境中是否已经安装 Ultralytics。

## 卸载环境

软件提供环境卸载功能，可以删除指定 Conda 环境。卸载前请确认环境名称正确，避免误删正在使用的环境。

命令行等价操作示例：

```powershell
conda env remove -n yolo-env
```

## 开发环境

安装依赖：

```powershell
pip install -r requirements.txt
```

运行测试：

```powershell
pytest -q
```

代码检查：

```powershell
ruff check .
```

安全试运行：

```powershell
python main.py --dry-run
```

## 打包发布

使用 PowerShell 执行：

```powershell
powershell -ExecutionPolicy Bypass -File build\make_release.ps1
```

生成文件：

```text
dist\YoloInstaller.exe
dist\YoloInstaller.exe.sha256
```

`.sha256` 文件用于校验 exe 是否完整。

## 常见问题

### 为什么显示 CPU 版本？

通常是因为没有检测到可用 NVIDIA GPU，或当前 CUDA / 驱动条件不适合安装 GPU 版本 PyTorch。CPU 版本可以正常使用 YOLO，但速度会慢一些。

### 为什么软件提示不建议安装到 C 盘？

C 盘容易遇到权限、空间和系统保护问题。安装到 D 盘或 E 盘更稳妥。

### 为什么 Conda 已经装了，但软件没检测到？

可能是 Conda 没有加入环境变量，或安装路径比较特殊。可以在软件中手动选择 Conda 安装目录。

### 安装卡住怎么办？

先查看日志区域最后几行。如果网络下载长时间无响应，可以取消任务后重新安装。也可以更换网络或代理后重试。

### Python 版本选哪个？

推荐优先选择 `3.10`。如果你明确知道依赖支持，也可以选择 `3.11`、`3.12` 或手动输入其他版本。

## 当前状态

当前版本已经移除所有模型权重相关功能，软件只专注于 YOLO 运行环境的安装、检测和卸载。

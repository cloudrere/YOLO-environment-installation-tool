# YOLO 环境安装工具实施方案

## 目标

本工具面向 Windows 用户，提供一个可双击运行的 YOLO Python 环境安装器。软件专注于环境检测、Conda 准备、环境创建、依赖安装、取消、清理和日志展示。

## 当前范围

- 检测 Windows、Conda、NVIDIA GPU、CUDA、磁盘空间和当前 Conda 环境。
- 可一键安装 Miniconda。
- 可选择 Conda 安装目录、环境名称和 Python 版本。
- 可安装 PyTorch、Ultralytics、Jupyter。
- 可跳过 PyTorch 或 Ultralytics；两个同时跳过时允许继续。
- 跳过安装前先检测目标环境是否已经安装对应包。
- 支持取消长时间命令。
- 支持删除指定 Conda 环境。
- 支持中文界面、日志、进度条和打包发布。

## 不包含内容

本工具不管理模型权重、示例推理资源或外部模型下载内容。软件只负责安装和维护 YOLO 运行环境。

## 模块结构

```text
app/
  core/
    conda_manager.py
    cuda_matcher.py
    detector.py
    jupyter_installer.py
    pip_installer.py
    pipeline.py
    resume.py
    state.py
    ultralytics_setup.py
    validation.py
  data/
    cuda_torch_map.json
    mirrors.json
  ui/
    main_window.py
    pages/
      detect_page.py
      select_page.py
      install_page.py
    widgets/
      log_view.py
      status_card.py
    style.qss
    text.py
```

## 安装流程

1. 环境检测
2. Conda 准备
3. 创建目标环境
4. 安装 PyTorch
5. 安装 Ultralytics
6. 可选安装 Jupyter
7. 可选创建快捷方式

## 发布验证

发布前建议运行：

```powershell
python -m pytest -q
python -m ruff check .
```

并通过：

```powershell
powershell -ExecutionPolicy Bypass -File build\make_release.ps1
```

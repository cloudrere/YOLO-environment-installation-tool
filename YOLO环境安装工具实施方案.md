# YOLO 环境自动安装工具 —— Windows .exe 开发执行计划 v2

> 本文件是**可直接派给开发执行**的版本：每个任务都有输入、输出、函数签名、验收标准与工时估算。
> 仓库根目录约定为 `yolo-installer/`，文件路径均以此为根。

---

## 0. Context（背景与目标）

深度学习用户在 Windows 上配置 YOLO 训练/推理环境时常因 CUDA、PyTorch、Conda、镜像源、依赖冲突反复踩坑。本工具目标：**双击 .exe，5–15 分钟得到可直接训练 / 推理、覆盖 YOLOv3–v12 与 SAM/RT-DETR 全系列模型的桌面环境**。

成功定义：
1. 干净 Win10 / Win11（无 Python、无 Conda）上双击 exe，全程无终端弹窗；
2. 安装结束后 GUI 内嵌「试一下」按钮可成功推理 `bus.jpg` 并显示带框结果图；
3. 全程国内镜像，宽带 100Mbps 下 GPU 版预计 ≤ 12 分钟，CPU 版 ≤ 6 分钟；
4. 用户目录 100% 可清理（无 `Program Files`、无系统 PATH、无注册表残留）。

---

## 1. 技术栈与版本钉死

`requirements.txt`：

```
PyQt6==6.7.1
PyQt6-Qt6==6.7.2
requests==2.32.3
packaging==24.1
pywin32==306          ; sys_platform == 'win32'
```

`build/requirements-dev.txt`：

```
pyinstaller==6.10.0
pytest==8.3.2
pytest-qt==4.4.0
ruff==0.6.5
```

Python 解释器：**3.11.x**（开发与打包统一，避免 wheel 不一致）。

---

## 2. 仓库目录与文件清单（最终态）

```
yolo-installer/
├── main.py
├── requirements.txt
├── build/
│   ├── requirements-dev.txt
│   ├── build.spec                  # PyInstaller
│   └── make_release.ps1            # 一键打包脚本
├── app/
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── pages/
│   │   │   ├── detect_page.py      # ① 环境检测
│   │   │   ├── select_page.py      # ② 模型选择
│   │   │   └── install_page.py     # ③ 安装进度
│   │   ├── widgets/
│   │   │   ├── status_card.py
│   │   │   ├── model_card.py
│   │   │   └── log_view.py
│   │   ├── workers.py              # QThread 包装 pipeline
│   │   └── style.qss
│   ├── core/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── conda_manager.py
│   │   ├── cuda_matcher.py
│   │   ├── pip_installer.py
│   │   ├── ultralytics_setup.py
│   │   ├── jupyter_installer.py
│   │   ├── pipeline.py
│   │   └── state.py                # 断点续装
│   ├── data/
│   │   ├── cuda_torch_map.json
│   │   ├── yolo_models.json
│   │   └── mirrors.json
│   └── utils/
│       ├── __init__.py
│       ├── runner.py
│       ├── downloader.py
│       ├── logger.py
│       └── paths.py
├── assets/
│   ├── icon.ico
│   ├── splash.png
│   ├── bus.jpg                     # 自检图
│   └── README_screenshots/
├── tests/
│   ├── test_cuda_matcher.py
│   ├── test_detector_parse.py
│   ├── test_state.py
│   ├── test_pipeline_mock.py
│   └── fixtures/
│       ├── nvidia_smi_550.txt
│       ├── nvidia_smi_legacy.txt
│       └── conda_env_list.txt
└── README.md
```

---

## 3. 数据契约（直接落盘的 JSON 全文）

### 3.1 `app/data/cuda_torch_map.json`

```json
{
  "schema_version": 1,
  "gpu": [
    {
      "cuda_max": "12.6",
      "torch_index": "https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu124",
      "spec": ["torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1"]
    },
    {
      "cuda_max": "12.1",
      "torch_index": "https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu121",
      "spec": ["torch==2.4.1", "torchvision==0.19.1", "torchaudio==2.4.1"]
    },
    {
      "cuda_max": "11.8",
      "torch_index": "https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu118",
      "spec": ["torch==2.4.1", "torchvision==0.19.1", "torchaudio==2.4.1"]
    }
  ],
  "cpu": {
    "torch_index": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "spec": ["torch==2.4.1+cpu", "torchvision==0.19.1+cpu", "torchaudio==2.4.1+cpu"],
    "extra_index": "https://download.pytorch.org/whl/cpu"
  }
}
```

> **维护责任**：发版前由负责人对照 https://pytorch.org/get-started/previous-versions 校对一次；条目按 `cuda_max` 降序排列。

### 3.2 `app/data/yolo_models.json`

```json
{
  "schema_version": 1,
  "groups": [
    {
      "key": "detect", "title": "目标检测",
      "items": [
        {"id": "yolov3",   "label": "YOLOv3",   "scales": ["", "-tiny", "-spp"]},
        {"id": "yolov5",   "label": "YOLOv5",   "scales": ["n", "s", "m", "l", "x"]},
        {"id": "yolov6",   "label": "YOLOv6",   "scales": ["n", "s", "m", "l"]},
        {"id": "yolov8",   "label": "YOLOv8",   "scales": ["n", "s", "m", "l", "x"]},
        {"id": "yolov9",   "label": "YOLOv9",   "scales": ["t", "s", "m", "c", "e"]},
        {"id": "yolov10",  "label": "YOLOv10",  "scales": ["n", "s", "m", "b", "l", "x"]},
        {"id": "yolo11",   "label": "YOLO11",   "scales": ["n", "s", "m", "l", "x"]},
        {"id": "yolov12",  "label": "YOLOv12",  "scales": ["n", "s", "m", "l", "x"]}
      ]
    },
    {"key": "segment",  "title": "实例分割", "items": [
      {"id": "yolov5",  "label": "YOLOv5-seg",  "suffix": "-seg", "scales": ["n", "s", "m", "l", "x"]},
      {"id": "yolov8",  "label": "YOLOv8-seg",  "suffix": "-seg", "scales": ["n", "s", "m", "l", "x"]},
      {"id": "yolo11",  "label": "YOLO11-seg",  "suffix": "-seg", "scales": ["n", "s", "m", "l", "x"]}
    ]},
    {"key": "classify", "title": "图像分类", "items": [
      {"id": "yolov5", "label": "YOLOv5-cls", "suffix": "-cls", "scales": ["n", "s", "m", "l", "x"]},
      {"id": "yolov8", "label": "YOLOv8-cls", "suffix": "-cls", "scales": ["n", "s", "m", "l", "x"]},
      {"id": "yolo11", "label": "YOLO11-cls", "suffix": "-cls", "scales": ["n", "s", "m", "l", "x"]}
    ]},
    {"key": "pose", "title": "关键点", "items": [
      {"id": "yolov8", "label": "YOLOv8-pose", "suffix": "-pose", "scales": ["n", "s", "m", "l", "x"]},
      {"id": "yolo11", "label": "YOLO11-pose", "suffix": "-pose", "scales": ["n", "s", "m", "l", "x"]}
    ]},
    {"key": "obb", "title": "旋转框", "items": [
      {"id": "yolov8", "label": "YOLOv8-obb", "suffix": "-obb", "scales": ["n", "s", "m", "l", "x"]},
      {"id": "yolo11", "label": "YOLO11-obb", "suffix": "-obb", "scales": ["n", "s", "m", "l", "x"]}
    ]},
    {"key": "extra", "title": "其他模型", "items": [
      {"id": "yolo_nas", "label": "YOLO-NAS", "weights": ["yolo_nas_s.pt", "yolo_nas_m.pt", "yolo_nas_l.pt"]},
      {"id": "rtdetr",   "label": "RT-DETR",  "weights": ["rtdetr-l.pt", "rtdetr-x.pt"]},
      {"id": "sam",      "label": "SAM",      "weights": ["sam_b.pt", "sam_l.pt"]},
      {"id": "sam2",     "label": "SAM 2",    "weights": ["sam2_b.pt", "sam2_l.pt"]},
      {"id": "mobile_sam", "label": "MobileSAM", "weights": ["mobile_sam.pt"]},
      {"id": "fastsam",  "label": "FastSAM",  "weights": ["FastSAM-s.pt", "FastSAM-x.pt"]},
      {"id": "yolow",    "label": "YOLO-World", "weights": ["yolov8s-world.pt", "yolov8s-worldv2.pt"]}
    ]}
  ]
}
```

权重文件名构造规则：`{id}{scale}{suffix}.pt`（无 scale 时省略），例：`yolov8n.pt`、`yolo11s-seg.pt`、`yolov3-tiny.pt`、`yolo_nas_s.pt`（extra 组直接读 `weights` 字段）。

### 3.3 `app/data/mirrors.json`

```json
{
  "pip": [
    {"name": "清华", "url": "https://pypi.tuna.tsinghua.edu.cn/simple"},
    {"name": "阿里", "url": "https://mirrors.aliyun.com/pypi/simple"},
    {"name": "中科大", "url": "https://pypi.mirrors.ustc.edu.cn/simple"}
  ],
  "conda_channels": [
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main",
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free",
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge"
  ],
  "miniconda_installer": "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe",
  "github_proxies": [
    "https://ghproxy.com/",
    "https://gh-proxy.com/",
    "https://hub.gitmirror.com/"
  ]
}
```

---

## 4. 模块接口（函数签名 + Docstring + 返回类型）

### 4.1 `app/utils/runner.py`

```python
from dataclasses import dataclass
from typing import Callable, Sequence

@dataclass
class CommandResult:
    returncode: int
    stdout: str           # 合并 stderr 的完整输出
    duration_sec: float

def run(
    cmd: Sequence[str],
    *,
    cwd: str | None = None,
    env: dict | None = None,
    on_line: Callable[[str], None] | None = None,
    timeout: float | None = None,
) -> CommandResult:
    """统一子进程入口。
    - cmd 必须是 list，禁止字符串拼接
    - Windows 自动加 creationflags=CREATE_NO_WINDOW
    - 默认 env 注入 PYTHONIOENCODING=utf-8
    - on_line 用于把每行实时回传 UI（Qt signal.emit）
    """
```

### 4.2 `app/core/detector.py`

```python
from dataclasses import dataclass

@dataclass
class GpuInfo:
    name: str
    driver: str
    memory_mib: int
    cuda_runtime_max: str    # e.g. "12.4"

@dataclass
class CondaInfo:
    path: str | None         # 绝对路径或 None
    version: str | None
    envs: list[str]          # 已有环境名

@dataclass
class EnvSnapshot:
    os: str
    is_windows_supported: bool
    conda: CondaInfo
    gpu: GpuInfo | None
    free_disk_gb: float
    mirror_reachable: bool

def detect_all() -> EnvSnapshot: ...
def parse_nvidia_smi(text: str) -> GpuInfo | None: ...      # 纯函数，方便单测
def parse_conda_env_list(text: str) -> list[str]: ...       # 纯函数
```

### 4.3 `app/core/cuda_matcher.py`

```python
from dataclasses import dataclass

@dataclass
class TorchPlan:
    mode: str                 # "gpu" | "cpu"
    cuda_tag: str | None      # "cu124" / "cu121" / None
    spec: list[str]           # ["torch==2.5.1", ...]
    index_url: str
    extra_index_url: str | None = None

def choose(gpu: "GpuInfo | None", table_path: str) -> TorchPlan:
    """无 GPU → cpu 分支；否则按 cuda_max 降序取第一条 ≤ 驱动上限。"""
```

### 4.4 `app/core/conda_manager.py`

```python
def find_existing_conda() -> str | None: ...
def install_miniconda(target_dir: str, on_line=None) -> str:
    """下载并静默安装 Miniconda 到 target_dir，返回 conda.exe 绝对路径。"""

def write_condarc(channels: list[str], backup_dir: str) -> None: ...
def create_env(conda_exe: str, env_name: str, python_version: str = "3.10", on_line=None) -> str:
    """返回该 env 内 python.exe 绝对路径。"""
def env_python(conda_exe: str, env_name: str) -> str: ...
def remove_env(conda_exe: str, env_name: str) -> None: ...
```

### 4.5 `app/core/pip_installer.py`

```python
def pip_install(
    python_exe: str,
    specs: list[str],
    *,
    index_url: str,
    extra_index_url: str | None = None,
    retries: int = 3,
    on_line=None,
) -> None:
    """失败按 mirrors.json 顺序切换 index_url；3 次仍失败 raise InstallError。"""
```

### 4.6 `app/core/ultralytics_setup.py`

```python
def install_ultralytics(python_exe: str, on_line=None) -> None: ...

def predownload_weights(
    python_exe: str,
    weights: list[str],     # ["yolov8n.pt", "yolo11n-seg.pt", ...]
    weight_dir: str,
    on_line=None,
) -> dict[str, str]:        # {weight_name: local_path}
    """逐个调用 `python -c "from ultralytics import YOLO; YOLO('xxx.pt')"`，
    YOLO 内部会自动下载到 weight_dir。失败用 ghproxy 重试。"""

def smoke_test(python_exe: str, weight: str, image_path: str, out_path: str) -> bool:
    """跑一次 model(image_path)，保存可视化结果到 out_path。返回是否成功。"""
```

### 4.7 `app/core/state.py`

```python
@dataclass
class InstallState:
    started_at: str
    finished_steps: list[str]      # ["detect", "conda", "env", ...]
    config: dict                    # 用户选择的全量配置
    last_error: str | None = None

def load() -> InstallState | None: ...
def save(s: InstallState) -> None: ...
def clear() -> None: ...
```

### 4.8 `app/core/pipeline.py`（编排器，UI 线程从这里驱动）

```python
class Pipeline:
    STEPS = ["detect", "conda", "env", "torch", "ultralytics",
             "weights", "jupyter", "smoke", "shortcut"]

    def __init__(self, config: dict, on_line, on_step, on_done): ...
    def run(self) -> None: ...      # 同步执行；UI 在 QThread 里 .run()
    def cancel(self) -> None: ...   # 在子进程间隙安全退出
```

`config` 形状：

```python
{
    "env_name": "yolo-env",
    "python_version": "3.10",
    "install_dir": "C:/Users/xxx/miniconda3",
    "workspace": "C:/Users/xxx/yolo_workspace",
    "weights": ["yolov8n.pt", "yolo11n.pt"],
    "install_jupyter": True,
    "make_shortcut": True,
    "pip_mirror": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "torch_plan": {...},   # 由 cuda_matcher.choose() 给出
}
```

---

## 5. UI 规范

### 5.1 三页签字段表

| 页签 | 区块 | 控件 | 字段 / 行为 |
|---|---|---|---|
| ① 环境检测 | 顶部 | 4 张 `StatusCard` | OS / Conda / GPU / 磁盘空间，每张点击「详情」展开 |
| | 按钮区 | 「重新检测」「下一步」 | 检测中禁用「下一步」 |
| ② 模型选择 | 任务 Tab | `QTabWidget` × 6 | detect / segment / classify / pose / obb / extra |
| | 每行 | `ModelCard`：复选框 + 规模下拉 + 大小提示 | 勾选后实时累加下载量显示在底栏 |
| | 高级面板 | 折叠 | env 名、workspace、镜像源、是否装 Jupyter、是否建桌面快捷方式 |
| ③ 安装进度 | 步骤条 | 9 步圆点 | 当前步高亮，失败步红色 |
| | 日志 | `LogView`（基于 `QPlainTextEdit`，autoscroll） | 行长 2k 截断，最多保留 5k 行内存 |
| | 底栏 | 「取消」「打开日志目录」「试一下」 | 完成后「试一下」高亮 |

### 5.2 线程模型

- UI 线程持有 `Pipeline`；
- `InstallWorker(QThread)` 包装 `pipeline.run()`；
- 三个 Qt signal：`line_emitted(str)`、`step_changed(str, str)`（step, status）、`finished(bool, str)`；
- `cancel` 按钮触发 `pipeline.cancel()`，子进程已启动的会等其结束再退出（不强杀）。

---

## 6. 关键代码骨架（开发可直接落地）

### 6.1 `utils/runner.py`

```python
import os, subprocess, time
from .. import CREATE_NO_WINDOW  # 在 utils/__init__.py 定义

def run(cmd, *, cwd=None, env=None, on_line=None, timeout=None):
    full_env = os.environ.copy()
    full_env["PYTHONIOENCODING"] = "utf-8"
    if env: full_env.update(env)
    t0 = time.monotonic()
    proc = subprocess.Popen(
        list(cmd), cwd=cwd, env=full_env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
        creationflags=CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    chunks = []
    try:
        for line in proc.stdout:
            line = line.rstrip("\r\n")
            chunks.append(line)
            if on_line: on_line(line)
            if timeout and time.monotonic() - t0 > timeout:
                proc.kill(); raise TimeoutError(cmd)
        proc.wait()
    finally:
        if proc.poll() is None:
            proc.kill()
    return CommandResult(proc.returncode, "\n".join(chunks), time.monotonic() - t0)
```

### 6.2 `core/detector.py` 关键正则

```python
_RE_CUDA = re.compile(r"CUDA Version:\s+(\d+\.\d+)")

def parse_nvidia_smi(text: str):
    m = _RE_CUDA.search(text)
    if not m: return None
    cuda = m.group(1)
    # 第二条命令的输出: "NVIDIA GeForce RTX 4070, 550.78, 12282 MiB"
    # 调用方需把两份输出拼起来传进来
    lines = [l for l in text.splitlines() if "MiB" in l and "," in l]
    if not lines: return None
    name, driver, mem = [s.strip() for s in lines[0].split(",")[:3]]
    return GpuInfo(name=name, driver=driver,
                   memory_mib=int(mem.split()[0]), cuda_runtime_max=cuda)
```

### 6.3 `core/conda_manager.py` 安装命令

```python
INSTALLER_ARGS = ["/InstallationType=JustMe", "/AddToPath=0",
                  "/RegisterPython=0", "/S", f"/D={target_dir}"]
# Popen([installer_path, *INSTALLER_ARGS]) —— /D 必须放最后且不能加引号
```

### 6.4 `core/ultralytics_setup.py` 预下载脚本

```python
_PREDOWNLOAD = """
import os, sys
from ultralytics import YOLO, NAS, RTDETR, SAM, FastSAM
name = sys.argv[1]
cls = YOLO
low = name.lower()
if low.startswith('yolo_nas'): cls = NAS
elif low.startswith('rtdetr'): cls = RTDETR
elif low.startswith('sam'):    cls = SAM
elif low.startswith('fastsam'): cls = FastSAM
cls(name)        # 触发自动下载
print('OK', name)
"""

def predownload_weights(python_exe, weights, weight_dir, on_line=None):
    env = {"YOLO_CONFIG_DIR": weight_dir}
    out = {}
    for w in weights:
        r = run([python_exe, "-c", _PREDOWNLOAD, w], env=env, on_line=on_line)
        if r.returncode != 0:
            raise InstallError(f"weight download failed: {w}")
        out[w] = os.path.join(weight_dir, w)
    return out
```

### 6.5 `core/pipeline.py` 主循环

```python
def run(self):
    try:
        for step in self.STEPS:
            if self._cancelled: return self.on_done(False, "canceled")
            self.on_step(step, "running")
            getattr(self, f"_do_{step}")()
            self.on_step(step, "ok")
            state.save(self._snapshot(step))
        self.on_done(True, "")
    except Exception as e:
        log.exception("pipeline failed")
        self.on_step(self._current, "fail")
        self.on_done(False, str(e))
```

---

## 7. 任务拆分（可直接派活）

> 工时按一名熟练 Python+Qt 工程师计。

### M1 核心链路（CLI）— 合计 2 人天

| # | 任务 | 文件 | 验收 | 工时 |
|---|---|---|---|---|
| 1.1 | `utils/runner.py` + 单测 | `utils/runner.py`、`tests/test_runner.py` | echo 命令能拿到输出；超时被 raise | 0.25d |
| 1.2 | `detector.parse_*` 纯函数 + 单测 | `core/detector.py`、`tests/test_detector_parse.py` | 三份 fixture（驱动 550 / 470 / 无 GPU）解析通过 | 0.25d |
| 1.3 | `detector.detect_all()` 集成 | 同上 | 本机 / 无 GPU 机器输出合法 `EnvSnapshot` | 0.25d |
| 1.4 | `cuda_matcher.choose()` + 单测 | `core/cuda_matcher.py`、`tests/test_cuda_matcher.py` | 驱动 12.4 → cu124；驱动 11.7 → cu118；无 GPU → cpu | 0.25d |
| 1.5 | `conda_manager` 全部接口 | `core/conda_manager.py` | 干净机能装 Miniconda 并 `conda --version` 输出版本 | 0.5d |
| 1.6 | `pip_installer` + 镜像切换 | `core/pip_installer.py` | 故意把首选镜像设错，能自动切到次选成功 | 0.25d |
| 1.7 | `ultralytics_setup` + smoke_test | `core/ultralytics_setup.py` | 装完后 `bus.jpg` 推理产出非空 `result.jpg` | 0.25d |
| 1.8 | `pipeline.py` 编排 + `state` | `core/pipeline.py`、`core/state.py` | CLI `python -m app.core.pipeline --models yolov8n` 全流程跑通 | 0.5d |

### M2 PyQt6 GUI — 2 人天

| # | 任务 | 验收 | 工时 |
|---|---|---|---|
| 2.1 | `main_window.py` + 三页签骨架 + QSS | 切换页签流畅，深浅自适应 | 0.5d |
| 2.2 | `detect_page` + `StatusCard` | 检测结果四卡片正确显示 | 0.5d |
| 2.3 | `select_page` + `ModelCard` + 大小累加 | 勾选权重底栏总量正确 | 0.5d |
| 2.4 | `install_page` + `LogView` + 步骤条 + `InstallWorker` | 完整安装全程不卡 UI，可取消 | 0.5d |

### M3 异常路径 — 1.5 人天

| # | 任务 | 验收 | 工时 |
|---|---|---|---|
| 3.1 | 断点续装 / 启动时询问 | 杀进程后重启可继续 | 0.25d |
| 3.2 | 网络重试 + 镜像切换全链路 | 拔网线 → 切镜像 → 友好弹窗 | 0.5d |
| 3.3 | 中文路径校验 + 警告 | 用户名带中文时强制把 conda 装到英文目录 | 0.25d |
| 3.4 | 「试一下」推理预览 | 主窗口内嵌 QLabel 显示 `result.jpg` | 0.25d |
| 3.5 | 卸载环境按钮 | 调 `conda env remove -n xxx` 干净 | 0.25d |

### M4 打包发布 — 0.5 人天

| # | 任务 | 验收 |
|---|---|---|
| 4.1 | `build/build.spec` + 一键脚本 | `pwsh build/make_release.ps1` 产出 `dist/YoloInstaller.exe` |
| 4.2 | 干净 Win10 / Win11 虚机实测 | 双击 → 完整流程 → 推理 OK |
| 4.3 | README + 加白指引 | 文档含截图与 Defender 误报指引 |

**总计 ≈ 6 人天**，单人节奏 1.5 周可发版 v1.0。

---

## 8. 测试矩阵

### 8.1 单元测试（pytest，CI 必跑）

| 文件 | 用例数 | 关键覆盖 |
|---|---|---|
| `test_cuda_matcher.py` | ≥ 6 | 驱动 12.6 / 12.4 / 12.1 / 11.8 / 10.2 / 无 GPU |
| `test_detector_parse.py` | ≥ 4 | 三份 nvidia-smi fixture + `conda env list` |
| `test_state.py` | ≥ 3 | save / load / 损坏文件容错 |
| `test_pipeline_mock.py` | ≥ 2 | 用 monkeypatch 把所有 runner.run 桩掉，验证 STEPS 顺序 |

### 8.2 端到端（手测，发版前必跑）

| ID | 场景 | 预期 |
|---|---|---|
| E2E-1 | 全新 Win10 + RTX 4070 | 装 Miniconda → cu124 torch → ultralytics → 推理 OK，`torch.cuda.is_available()` 为 True |
| E2E-2 | 全新 Win11 无 N 卡 | 走 CPU，`torch.__version__` 含 `+cpu` |
| E2E-3 | 已有 Anaconda | 跳过 Miniconda，复用已有 conda |
| E2E-4 | 安装中途拔网线 | 弹错误对话框 + 「重试 / 切镜像 / 取消」三按钮 |
| E2E-5 | 多模型勾选（v8-seg + 11-pose + sam_b） | 权重逐个下完，最终四个 import 全部成功 |
| E2E-6 | Jupyter 勾选 | `jupyter notebook` 启动，内核列表含新 env |
| E2E-7 | 中文用户名（如 `用户`） | conda 强制装到 `C:\YoloInstaller` 等英文目录 |
| E2E-8 | Defender 启用 | 至少能按 README 指引加白后正常运行 |

---

## 9. 风险与缓解（开发者侧关注点）

| 风险 | 触发条件 | 缓解 |
|---|---|---|
| ultralytics 大版本破坏接口 | 升 v9 之后 NAS / SAM 入口改名 | requirements 锁 `ultralytics>=8.3,<9`；版本固化在 `requirements.txt` |
| 清华 PyTorch 镜像缺某 cu 版本 | 矩阵未及时同步 | 镜像 404 自动回退 `download.pytorch.org/whl/cuXXX` |
| PyInstaller exe 被 Defender 删 | 用户机器启用实时保护 | README 含「Defender 加白」配图；预算允许后买代码签名证书 |
| onefile 解压慢冷启动 | 第一次双击 2–3 秒无响应 | `--splash` 显示加载图，避免用户重复点击 |
| GBK 编码 → 子进程乱码 | 中文路径 / 中文输出 | 全链路 `PYTHONIOENCODING=utf-8`，runner 用 `errors='replace'` |
| `nvidia-smi` 不存在但有 N 卡 | 驱动未装 | 提示「先装显卡驱动」并附 NVIDIA 官网链接，不强行走 GPU 分支 |

---

## 10. 交付物清单（v1.0 发版必备）

- [ ] `dist/YoloInstaller.exe`（单文件，~80MB）
- [ ] `dist/YoloInstaller.exe.sha256`
- [ ] `README.md`：用法 / FAQ / Defender 加白 / 卸载方法
- [ ] `CHANGELOG.md`
- [ ] 至少 5 张主流程截图放 `assets/README_screenshots/`
- [ ] 单测在 CI 全绿
- [ ] E2E-1 / E2E-2 在两台干净虚机过完整流程录屏

---

## 11. 启动检查（开发动手前 10 分钟）

1. `python -V` 确认 3.11.x；`pip install -r requirements.txt -r build/requirements-dev.txt`；
2. 拉一份 `nvidia-smi` 输出粘到 `tests/fixtures/nvidia_smi_550.txt` 作真实样本；
3. 把 `app/data/*.json` 三个文件先落盘并跑一次 `pytest`，确认 import 链路通；
4. 跑 `python main.py` 看 PyQt 空窗口能起；
5. 进入 M1.1，按任务表逐项推进，每完成一项推一个 commit（`feat(detector): parse nvidia-smi v550`）。

---

附：本文件是开发执行版；产品视角与决策记录见 `C:\Users\15864\.claude\plans\windows-exe-yolo-squishy-blanket.md`。

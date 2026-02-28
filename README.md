# 9-Slice Cutter

A desktop GUI tool for game developers to visually configure 9-slice (9-patch) borders on UI images. It removes the redundant center cross and exports a memory-optimized, stitched image compatible with Unity and other game engines.

## 功能介绍

- 可视化拖拽调整四条切割参考线（上/下/左/右边距）
- 实时预览 9-slice 裁切结果
- 导出符合 Unity 等引擎标准的 "Type B" 格式图片
  - 保留 4 个角 + 4 条 1px 拉伸边带 + 1px 中心像素
  - 去除冗余的中心十字区域，节省显存
- 支持 PNG / JPG 拖拽导入
- 支持覆盖保存 / 另存为

## 算法说明

**输入：** 源图像 + 四个边距（像素）

**输出：** 尺寸为 `(left + 1 + right, top + 1 + bottom)` 的拼合图像

输出图像由以下区域拼合而成：
- 4 个角（原尺寸保留）
- 4 条边带（宽度裁为 1px）
- 1 个中心像素

## 环境依赖

- **Python** 3.10+
- **PySide6** — Qt GUI 框架
- **Pillow** — 图像处理
- **pytest** — 测试框架（仅开发需要）
- **PyInstaller** — 打包工具（仅构建需要）

安装依赖：

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 测试

```bash
# 运行全部测试（113 个）
pytest

# 运行单个测试文件
pytest tests/test_image_processor.py -v
```

## 构建可执行文件

**跨平台（Python 脚本）：**

```bash
python build.py
```

**Windows（含图标）：**

```bat
build_windows_app.bat
```

构建产物位于 `dist/9SliceCutter.exe`（约 56MB，无控制台窗口）。

## 项目结构

```
main.py                      # 程序入口（含 Windows 任务栏图标集成）
requirements.txt             # 依赖列表
build.py                     # 跨平台构建脚本
build_windows_app.bat        # Windows 构建脚本
core/
  image_processor.py         # 9-slice 核心算法
ui/
  main_window.py             # PySide6 主界面
tests/                       # 113 个自动化测试
icon/
  icon.png                   # 原始图标（256×256）
  icon.ico                   # Windows 多分辨率图标
dist/
  9SliceCutter.exe           # 生产可执行文件
```

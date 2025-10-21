# 资产负债表可视化系统

## 📋 功能说明

这是一个标准化的资产负债表数据可视化系统，可以快速将财报数据转换为专业的柱状图。

### 核心功能
1. **CSV数据模板化** - 固定字段格式，只需填入数字
2. **一键生成图表** - 传入CSV路径即可自动生成图表
3. **批量处理** - 支持批量处理多个公司的财报数据
4. **数据分析** - 自动计算资产负债率、最大项等指标

---

## 📁 文件结构

```
finance/
├── balance_sheet_plotter.py    # 核心绘图模块(封装好的函数)
├── data/
│   ├── 空白模板.csv             # 空白CSV模板
│   ├── balance_sheet_template.csv  # 比亚迪示例数据
│   └── balance_sheet_data.csv      # 贵州茅台示例数据
└── README.md                    # 本文件
```

---

## 🚀 快速开始

### 步骤1: 准备数据

复制 `data/空白模板.csv`，按格式填入财报数据：

```csv
公司名称,比亚迪
报告日期,2024-12-31
资产类别,金额,类型
现金,1432.85,资产
应收款,777.76,资产
...
应付款,2440.27,负债
...
```

**重要规则：**
- 前2行为元数据（公司名称、报告日期）
- 第3行为表头（不要修改）
- 第4行开始为数据行
- `类型` 列只能填 `资产` 或 `负债`
- `资产类别` 可以自定义名称

### 步骤2: 生成图表

**方法1: 使用封装好的函数**

```python
from balance_sheet_plotter import plot_balance_sheet_from_csv

# 只需一行代码！
plot_balance_sheet_from_csv('data/你的数据.csv')
```

**方法2: 指定输出路径**

```python
from balance_sheet_plotter import plot_balance_sheet_from_csv

# 自定义输出路径
plot_balance_sheet_from_csv(
    csv_path='data/byd_2024.csv',
    output_path='output/byd_chart.png',
    show_plot=True
)
```

**方法3: 批量处理**

```python
from balance_sheet_plotter import batch_plot_balance_sheets

# 批量处理多个文件
csv_files = [
    'data/byd_2024.csv',
    'data/moutai_2024.csv',
    'data/tesla_2024.csv'
]

batch_plot_balance_sheets(csv_files, output_dir='output/')
```

---

## 📊 函数API文档

### `plot_balance_sheet_from_csv()`

**核心绘图函数** - 从CSV生成资产负债表图表

```python
plot_balance_sheet_from_csv(
    csv_path,           # 必需: CSV文件路径
    output_path=None,   # 可选: 输出图片路径(默认同CSV目录)
    figsize=(16, 8),    # 可选: 图表尺寸
    dpi=300,            # 可选: 图片分辨率
    show_plot=True      # 可选: 是否显示图表
)
```

**返回值**: 生成的图片路径

**示例**:
```python
# 最简单的用法
plot_balance_sheet_from_csv('data/byd.csv')

# 高级用法
plot_balance_sheet_from_csv(
    'data/byd.csv',
    output_path='charts/byd_balance.png',
    figsize=(20, 10),
    dpi=600,
    show_plot=False
)
```

---

### `analyze_balance_sheet_from_csv()`

**数据分析函数** - 分析资产负债表数据

```python
analyze_balance_sheet_from_csv(csv_path)
```

**输出**:
- 资产总计
- 负债总计
- 资产负债率
- 最大资产项
- 最大负债项

**示例**:
```python
from balance_sheet_plotter import analyze_balance_sheet_from_csv

results = analyze_balance_sheet_from_csv('data/byd.csv')
print(f"资产负债率: {results['资产负债率']:.2f}%")
```

---

### `batch_plot_balance_sheets()`

**批量处理函数** - 一次性处理多个CSV文件

```python
batch_plot_balance_sheets(
    csv_paths,          # 必需: CSV文件路径列表
    output_dir=None,    # 可选: 统一输出目录
    show_plot=False     # 可选: 是否显示图表
)
```

**示例**:
```python
from balance_sheet_plotter import batch_plot_balance_sheets

files = ['data/byd.csv', 'data/moutai.csv']
batch_plot_balance_sheets(files, output_dir='output/')
```

---

## 💡 使用示例

### 示例1: 单个公司分析

```python
from balance_sheet_plotter import (
    plot_balance_sheet_from_csv,
    analyze_balance_sheet_from_csv
)

csv_file = 'data/byd_2024.csv'

# 1. 数据分析
print("=== 数据分析 ===")
results = analyze_balance_sheet_from_csv(csv_file)

# 2. 生成图表
print("\n=== 生成图表 ===")
chart_path = plot_balance_sheet_from_csv(csv_file)
print(f"图表已生成: {chart_path}")
```

### 示例2: 多公司对比

```python
from balance_sheet_plotter import plot_balance_sheet_from_csv

companies = ['比亚迪', '贵州茅台', '特斯拉']
csv_files = [f'data/{company}_2024.csv' for company in companies]

for csv_file in csv_files:
    plot_balance_sheet_from_csv(
        csv_file,
        output_path=f'output/{csv_file.split("/")[-1].replace(".csv", ".png")}',
        show_plot=False
    )

print("所有图表已生成完成!")
```

### 示例3: 自定义样式

```python
from balance_sheet_plotter import plot_balance_sheet_from_csv

# 生成高分辨率、大尺寸图表
plot_balance_sheet_from_csv(
    'data/byd.csv',
    figsize=(24, 12),  # 更大的图表
    dpi=600,           # 超高清
    show_plot=True
)
```

---

## 📝 CSV模板字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| 公司名称 | 公司名称(元数据) | 比亚迪 |
| 报告日期 | 财报日期(元数据) | 2024-12-31 |
| 资产类别 | 资产或负债项目名称 | 现金、应付款 |
| 金额 | 数值(单位自定义) | 1432.85 |
| 类型 | 只能是"资产"或"负债" | 资产 |

**注意事项**:
- 前2行为元数据，第3行为表头，第4行开始为数据
- 金额可以是任意数值，支持小数
- 资产类别名称可以自定义
- 类型必须是"资产"或"负债"

---

## 🎨 图表说明

生成的图表包含以下元素：
- **蓝色柱** - 资产项
- **红色柱** - 负债项
- **数值标签** - 每个柱子上方显示具体数值
- **标题** - 包含公司名称和报告日期
- **图例** - 区分资产和负债
- **网格线** - 便于读取数值

---

## 🔧 依赖安装

```bash
pip install pandas matplotlib numpy
```

或使用项目根目录的 requirements.txt:

```bash
pip install -r requirements.txt
```

---

## ❓ 常见问题

**Q: 如何添加新的资产/负债项？**

A: 直接在CSV中添加新行即可，格式为：`资产类别,金额,类型`

**Q: 可以修改资产类别的名称吗？**

A: 可以，资产类别名称完全自定义。

**Q: 图表上的中文显示乱码怎么办？**

A: 代码已自动配置常见中文字体。如果仍有问题，请安装系统中文字体。

**Q: 如何生成多期对比图？**

A: 准备多个CSV文件（每期一个），使用批量处理功能。

**Q: 支持哪些图片格式？**

A: 默认PNG格式，可以修改output_path的扩展名来指定其他格式（如.jpg, .pdf）。

---

## 📞 联系方式

如有问题或建议，欢迎反馈！

---

**版本**: v1.0  
**更新日期**: 2024-12-31


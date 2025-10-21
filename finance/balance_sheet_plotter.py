"""
资产负债表数据可视化模板
通用的绘图函数封装
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False


def load_balance_sheet_data(csv_path):
    """
    从CSV文件加载资产负债表数据
    
    CSV文件格式:
        第1行: 公司名称,公司名
        第2行: 报告日期,日期
        第3行: 资产类别,金额,类型  (表头)
        第4行开始: 具体数据
    
    参数:
        csv_path: CSV文件路径
        
    返回:
        tuple: (公司名称, 报告日期, DataFrame)
    """
    # 读取前两行的元数据
    with open(csv_path, 'r', encoding='utf-8') as f:
        company_line = f.readline().strip().split(',')
        date_line = f.readline().strip().split(',')
        
    company_name = company_line[1] if len(company_line) > 1 else "公司"
    report_date = date_line[1] if len(date_line) > 1 else ""
    
    # 读取数据部分(从第3行开始)
    df = pd.read_csv(csv_path, encoding='utf-8', skiprows=2)
    
    return company_name, report_date, df


def plot_balance_sheet_from_csv(csv_path, output_path=None, figsize=(16, 8), 
                                 dpi=300, show_plot=True):
    """
    从CSV文件绘制资产负债表柱状图
    
    这是一个完全封装的函数,只需传入CSV文件路径即可生成标准化的资产负债表图表。
    
    参数:
        csv_path (str): CSV数据文件路径
        output_path (str, optional): 输出图片路径。如果不指定,则保存在CSV同目录下
        figsize (tuple): 图形大小,默认(16, 8)
        dpi (int): 图片分辨率,默认300
        show_plot (bool): 是否显示图表,默认True
        
    返回:
        str: 保存的图片路径
        
    示例:
        >>> plot_balance_sheet_from_csv('data/byd_balance_sheet.csv')
        >>> plot_balance_sheet_from_csv('data/moutai_balance_sheet.csv', 
        ...                             output_path='output/moutai.png',
        ...                             show_plot=False)
    """
    # 1. 加载数据
    company_name, report_date, df = load_balance_sheet_data(csv_path)
    
    # 2. 准备数据
    categories = df['资产类别'].values
    values = df['金额'].values
    types = df['类型'].values
    
    # 3. 创建图形
    fig, ax = plt.subplots(figsize=figsize)
    
    # 4. 设置柱子的位置和颜色
    x_pos = range(len(categories))
    colors = ['#4A90E2' if t == '资产' else '#E24A4A' for t in types]
    
    # 5. 绘制柱状图
    bars = ax.bar(x_pos, values, color=colors, width=0.6, alpha=0.85)
    
    # 6. 在柱子上方显示数值
    for bar, value in zip(bars, values):
        height = bar.get_height()
        if height > 0:  # 只显示非零值
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 7. 设置x轴
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=0, ha='center', fontsize=11)
    
    # 8. 设置y轴
    max_value = max(values)
    ax.set_ylim(0, max_value * 1.15)
    ax.set_ylabel('金额', fontsize=12, fontweight='bold')
    
    # 9. 设置网格
    ax.yaxis.grid(True, linestyle='-', alpha=0.2, color='gray')
    ax.set_axisbelow(True)
    
    # 10. 设置标题
    title = f'{company_name}资产负债表'
    if report_date:
        title += f'\n{report_date}'
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # 11. 添加图例
    legend_elements = [
        Patch(facecolor='#4A90E2', label='资产', alpha=0.85),
        Patch(facecolor='#E24A4A', label='负债', alpha=0.85)
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=11)
    
    # 12. 调整布局
    plt.tight_layout()
    
    # 13. 保存图片
    if output_path is None:
        # 默认保存在CSV同目录下
        csv_dir = os.path.dirname(csv_path)
        csv_filename = os.path.splitext(os.path.basename(csv_path))[0]
        output_path = os.path.join(csv_dir, f'{csv_filename}_chart.png')
    
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    print(f"✓ 图表已保存至: {output_path}")
    
    # 14. 显示图形
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def analyze_balance_sheet_from_csv(csv_path):
    """
    从CSV文件分析资产负债表数据
    
    参数:
        csv_path (str): CSV数据文件路径
        
    返回:
        dict: 分析结果字典
    """
    # 加载数据
    company_name, report_date, df = load_balance_sheet_data(csv_path)
    
    print("\n" + "="*60)
    print(f"{company_name}资产负债表数据分析")
    if report_date:
        print(f"报告期: {report_date}")
    print("="*60)
    
    # 按类型分组统计
    grouped = df.groupby('类型')['金额'].sum()
    
    print("\n【汇总统计】")
    results = {}
    for type_name, total in grouped.items():
        print(f"{type_name}总计: {total:.2f}")
        results[f'{type_name}总计'] = total
    
    # 资产负债率
    if '资产' in grouped.index and '负债' in grouped.index:
        ratio = (grouped['负债'] / grouped['资产']) * 100
        print(f"资产负债率: {ratio:.2f}%")
        results['资产负债率'] = ratio
    
    print("\n【详细数据】")
    print(df.to_string(index=False))
    
    # 找出最大的资产和负债项
    assets = df[df['类型'] == '资产']
    liabilities = df[df['类型'] == '负债']
    
    if not assets.empty:
        max_asset = assets.loc[assets['金额'].idxmax()]
        print(f"\n最大资产项: {max_asset['资产类别']} = {max_asset['金额']:.2f}")
        results['最大资产项'] = (max_asset['资产类别'], max_asset['金额'])
    
    if not liabilities.empty:
        max_liability = liabilities.loc[liabilities['金额'].idxmax()]
        print(f"最大负债项: {max_liability['资产类别']} = {max_liability['金额']:.2f}")
        results['最大负债项'] = (max_liability['资产类别'], max_liability['金额'])
    
    print("\n" + "="*60)
    
    return results


def batch_plot_balance_sheets(csv_paths, output_dir=None, show_plot=False):
    """
    批量绘制多个资产负债表
    
    参数:
        csv_paths (list): CSV文件路径列表
        output_dir (str): 输出目录,如果不指定则保存在各CSV同目录
        show_plot (bool): 是否显示图表,默认False(批量处理时建议关闭)
        
    返回:
        list: 生成的图片路径列表
    """
    result_paths = []
    
    for i, csv_path in enumerate(csv_paths, 1):
        print(f"\n[{i}/{len(csv_paths)}] 正在处理: {csv_path}")
        
        if output_dir:
            csv_filename = os.path.splitext(os.path.basename(csv_path))[0]
            output_path = os.path.join(output_dir, f'{csv_filename}_chart.png')
        else:
            output_path = None
        
        try:
            result_path = plot_balance_sheet_from_csv(
                csv_path, 
                output_path=output_path, 
                show_plot=show_plot
            )
            result_paths.append(result_path)
        except Exception as e:
            print(f"✗ 处理失败: {e}")
    
    print(f"\n批量处理完成! 共生成 {len(result_paths)} 个图表")
    return result_paths


if __name__ == '__main__':
    # 示例用法
    print("="*60)
    print("资产负债表绘图工具 - 使用示例")
    print("="*60)
    
    # 方式1: 单个文件绘图
    csv_file = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/balance_sheet_template.csv'
    
    if os.path.exists(csv_file):
        print("\n【示例1】单个文件绘图:")
        plot_balance_sheet_from_csv(csv_file)
        
        print("\n【示例2】数据分析:")
        analyze_balance_sheet_from_csv(csv_file)
    else:
        print(f"\n提示: 请先准备CSV数据文件: {csv_file}")
        print("\nCSV文件格式示例:")
        print("公司名称,比亚迪")
        print("报告日期,2024-12-31")
        print("资产类别,金额,类型")
        print("现金,1432.85,资产")
        print("存货,1160.36,资产")
        print("应付款,2440.27,负债")
        print("...")


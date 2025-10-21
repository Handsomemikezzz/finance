"""
资产负债表可视化 - 使用示例
以实际的例子演示了如何使用模板化的绘图函数
"""

from balance_sheet_plotter import (
    plot_balance_sheet_from_csv,
    analyze_balance_sheet_from_csv,
    batch_plot_balance_sheets
)
import os

def example1_simple_plot():
    """
    示例1: 最简单的用法 - 只传入CSV路径
    """
    print("\n" + "="*60)
    print("示例1: 简单绘图 - 只需一行代码")
    print("="*60)
    
    csv_file = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/balance_sheet_template.csv'
    
    if os.path.exists(csv_file):
        # 只需要这一行代码！
        plot_balance_sheet_from_csv(csv_file)
    else:
        print(f"文件不存在: {csv_file}")


def example2_custom_output():
    """
    示例2: 自定义输出路径
    """
    print("\n" + "="*60)
    print("示例2: 自定义输出路径")
    print("="*60)
    
    csv_file = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/balance_sheet_template.csv'
    output_file = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/output/byd_balance_sheet.png'
    
    if os.path.exists(csv_file):
        # 创建输出目录
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 指定输出路径
        chart_path = plot_balance_sheet_from_csv(
            csv_path=csv_file,
            output_path=output_file,
            show_plot=True
        )
        print(f"\n✓ 图表已保存至: {chart_path}")
    else:
        print(f"文件不存在: {csv_file}")


def example3_analyze_data():
    """
    示例3: 数据分析
    """
    print("\n" + "="*60)
    print("示例3: 数据分析")
    print("="*60)
    
    csv_file = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/balance_sheet_template.csv'
    
    if os.path.exists(csv_file):
        # 分析数据
        results = analyze_balance_sheet_from_csv(csv_file)
        
        # 使用分析结果
        if '资产负债率' in results:
            ratio = results['资产负债率']
            print(f"\n财务健康度评估:")
            if ratio < 40:
                print(f"  资产负债率 {ratio:.2f}% - 优秀")
            elif ratio < 60:
                print(f"  资产负债率 {ratio:.2f}% - 良好")
            elif ratio < 80:
                print(f"  资产负债率 {ratio:.2f}% - 一般")
            else:
                print(f"  资产负债率 {ratio:.2f}% - 需要关注")
    else:
        print(f"文件不存在: {csv_file}")


def example4_batch_process():
    """
    示例4: 批量处理多个公司的数据
    """
    print("\n" + "="*60)
    print("示例4: 批量处理")
    print("="*60)
    
    # 数据文件列表
    csv_files = [
        '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/balance_sheet_template.csv',
        '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/balance_sheet_data.csv',
    ]
    
    # 过滤存在的文件
    existing_files = [f for f in csv_files if os.path.exists(f)]
    
    if existing_files:
        output_dir = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/output'
        os.makedirs(output_dir, exist_ok=True)
        
        # 批量处理
        result_paths = batch_plot_balance_sheets(
            csv_paths=existing_files,
            output_dir=output_dir,
            show_plot=False  # 批量处理时不显示图表
        )
        
        print(f"\n✓ 成功生成 {len(result_paths)} 个图表:")
        for path in result_paths:
            print(f"  - {path}")
    else:
        print("没有找到可处理的CSV文件")


def example5_high_quality():
    """
    示例5: 生成高质量图表
    """
    print("\n" + "="*60)
    print("示例5: 生成高质量图表")
    print("="*60)
    
    csv_file = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/balance_sheet_template.csv'
    
    if os.path.exists(csv_file):
        # 生成超高清、大尺寸图表
        plot_balance_sheet_from_csv(
            csv_path=csv_file,
            figsize=(20, 10),  # 更大的图表
            dpi=600,           # 超高分辨率
            show_plot=False    # 不显示，只保存
        )
        print("\n✓ 已生成600 DPI超高清图表，适合印刷和演示")
    else:
        print(f"文件不存在: {csv_file}")


def main():
    """
    主函数 - 运行所有示例
    """
    print("\n" + "="*70)
    print("资产负债表可视化系统 - 使用示例演示")
    print("="*70)
    
    # 提示用户选择示例
    print("\n请选择要运行的示例:")
    print("  1 - 简单绘图（最常用）")
    print("  2 - 自定义输出路径")
    print("  3 - 数据分析")
    print("  4 - 批量处理")
    print("  5 - 生成高质量图表")
    print("  0 - 运行所有示例")
    
    choice = input("\n请输入选项 (0-5): ").strip()
    
    if choice == '1':
        example1_simple_plot()
    elif choice == '2':
        example2_custom_output()
    elif choice == '3':
        example3_analyze_data()
    elif choice == '4':
        example4_batch_process()
    elif choice == '5':
        example5_high_quality()
    elif choice == '0':
        example1_simple_plot()
        example2_custom_output()
        example3_analyze_data()
        example4_batch_process()
        example5_high_quality()
    else:
        print("\n无效选项，运行默认示例:")
        example1_simple_plot()
    
    print("\n" + "="*70)
    print("示例演示完成！")
    print("="*70)


if __name__ == '__main__':
    main()


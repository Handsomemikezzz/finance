"""
快速开始脚本
最简单的使用方式 - 只需修改CSV文件路径即可
"""

from balance_sheet_plotter import plot_balance_sheet_from_csv
import os

# ============================================
# 配置区域 - 只需修改这里
# ============================================

# 方式1: 填写你的CSV文件路径（完整路径）
CSV_FILE = '/Users/chuhaonan/Desktop/code/pyProject/myproject/finance/data/思源电气_002028_2025q3.csv'

# 方式2: 如果你的CSV文件在data目录下，只需填写相对路径
# CSV_FILE = 'data/你的文件名.csv'

# 可选：自定义输出路径（不填则自动保存在CSV同目录）
OUTPUT_FILE = None  # 例如: 'output/我的图表.png'

# 可选：是否显示图表（True=显示，False=只保存不显示）
SHOW_PLOT = True

# 可选：图表尺寸（宽, 高）
FIGURE_SIZE = (16, 8)

# 可选：图片分辨率（DPI）
DPI = 300

# ============================================
# 运行区域 - 无需修改
# ============================================

if __name__ == '__main__':
    print("="*60)
    print("资产负债表可视化 - 快速启动")
    print("="*60)
    
    # 检查文件是否存在
    if not os.path.exists(CSV_FILE):
        print(f"\n❌ 错误: CSV文件不存在")
        print(f"   文件路径: {CSV_FILE}")
        print(f"\n💡 提示:")
        print(f"   1. 检查文件路径是否正确")
        print(f"   2. 使用 data/company_code_time.csv 作为模板创建新文件")
        print(f"   3. 参考 data/ 目录下的示例文件")
        print(f"\n可用的示例文件:")
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            for csv_file in csv_files:
                print(f"   - data/{csv_file}")
    else:
        print(f"\n📁 数据文件: {CSV_FILE}")
        print(f"📊 图表尺寸: {FIGURE_SIZE}")
        print(f"🎨 分辨率: {DPI} DPI")
        print(f"👁️  显示图表: {'是' if SHOW_PLOT else '否'}")
        print(f"\n🚀 开始生成资产负债表图表...\n")
        
        try:
            # 调用封装好的函数 - 只需这一行！
            result_path = plot_balance_sheet_from_csv(
                csv_path=CSV_FILE,
                output_path=OUTPUT_FILE,
                figsize=FIGURE_SIZE,
                dpi=DPI,
                show_plot=SHOW_PLOT
            )
            
            print(f"\n✅ 成功! 图表已生成")
            print(f"📊 图表位置: {result_path}")
            print(f"\n{'='*60}")
            
        except Exception as e:
            print(f"\n❌ 生成失败: {e}")
            print(f"\n💡 请检查:")
            print(f"   1. CSV文件格式是否正确")
            print(f"   2. 文件是否包含正确的表头（公司名称、报告日期）")
            print(f"   3. 数据列是否完整（资产类别、金额、类型）")
            print(f"\nCSV文件格式示例:")
            print(f"   公司名称,比亚迪")
            print(f"   报告日期,2024-12-31")
            print(f"   资产类别,金额,类型")
            print(f"   现金,1432.85,资产")
            print(f"   ...")


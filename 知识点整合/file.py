import os
import pandas as pd
import warnings

# 抑制 openpyxl 的样式警告和 pandas 的 PerformanceWarning
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

def integrate_knowledge_base(folder_path, output_file=r'C:\Users\pt5156\Desktop\手机及配件整理.csv'):
    """
    整合文件夹中的所有 Excel 知识库模板为一个统一的 CSV 文件。
    
    参数:
    - folder_path: str, 包含 Excel 文件的文件夹路径
    - output_file: str, 输出 CSV 文件路径（默认保存到桌面）

    返回:
    - None, 生成一个整合后的 CSV 文件
    """
    all_dfs = []  # 存储所有 DataFrame 的列表
    successful_files = []
    failed_files = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx') and not filename.startswith('~$'):  # 跳过临时文件
            file_path = os.path.join(folder_path, filename)
            try:
                excel_file = pd.ExcelFile(file_path)
                sheet_name = next((s for s in excel_file.sheet_names if '知识导出表' in s), excel_file.sheet_names[0])
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
                
                # 清理数据：替换 NaN 为空字符串并转换为字符串
                df = df.fillna('').astype(str)
                df['source_file'] = filename
                
                all_dfs.append(df)
                successful_files.append(filename)
                print(f"成功加载文件: {filename} (Sheet: {sheet_name}, 行数: {len(df)})")
            except Exception as e:
                failed_files.append(filename)
                print(f"加载文件 {filename} 时出错: {e}")

    if all_dfs:
        try:
            integrated_df = pd.concat(all_dfs, ignore_index=True)
            integrated_df = integrated_df.copy()  # 消除内存碎片

            # 保存为 CSV 文件
            integrated_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"知识库整合完成，输出文件: {output_file}")
            print(f"总行数: {len(integrated_df)}")
            print(f"成功处理的文件: {len(successful_files)} 个")
            if failed_files:
                print(f"失败的文件: {failed_files}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
    else:
        print("没有数据可整合。")

# 指定文件夹路径
folder_path = r'C:\Users\pt5156\Downloads\20250807_統一知識庫知識導出-手機及配件'
integrate_knowledge_base(folder_path)

import zipfile
import pandas as pd
from io import StringIO  # 确保从 io 模块导入 StringIO

def merge_csvs_from_zip(zip_path, output_csv_path):
    """
    将 ZIP 文件中的所有 CSV 文件合并成一个 CSV 文件，包含三列：
    - 流水號 (flow number)
    - 对话 (each Transcription on a new line)
    - 分类 (concatenated 投訴分類-二級 to 投訴分類-七級, non-empty values)
    """
    merged_data = []
    
    # 定义中文级别数字
    chinese_levels = ['二', '三', '四', '五', '六', '七']
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
        
        for csv_file in csv_files:
            with zip_ref.open(csv_file) as file:
                content = file.read().decode('utf-8-sig')
                # 添加 low_memory=False 解决混合类型警告
                df = pd.read_csv(StringIO(content), low_memory=False)
                
                if '流水號' not in df.columns:
                    print(f"警告: {csv_file} 中没有 '流水號' 列，将跳过此文件")
                    continue
                
                # 先筛选以 '投訴分類-' 开头的列，并排除 '投訴分類-一級'
                class_cols = [col for col in df.columns if col.startswith('投訴分類-') and col != '投訴分類-一級']
                
                # 进一步筛选：使用中文数字级别，确保匹配 '-二級' 等
                class_cols = [col for col in class_cols if any(col.endswith(f'-{level}級') for level in chinese_levels)]
                
                # 如果没有匹配到列，打印调试信息
                if not class_cols:
                    print(f"警告: 在 {csv_file} 中未找到分类列 ('投訴分類-二級' 到 '投訴分類-七級')，请检查列名。")
                    print("可用列: ", [col for col in df.columns if col.startswith('投訴分類-')])
                    continue
                
                grouped = df.groupby('流水號')
                
                for flow_num, group in grouped:
                    # 每段对话分行，使用 '\n' 连接
                    dialogs = group['Transcription'].dropna().astype(str).tolist()
                    dialog = '\n'.join(dialogs) if dialogs else ''
                    
                    first_row = group.iloc[0]
                    classes = [first_row[col] for col in class_cols if pd.notna(first_row[col]) and str(first_row[col]).strip()]
                    classification = '-'.join(classes) if classes else ''
                    
                    merged_data.append({
                        '流水號': flow_num,
                        '对话': dialog,
                        '分类': classification
                    })
    
    # 将结果写入新的 CSV 文件
    if merged_data:  # 确保有数据才写入文件
        final_df = pd.DataFrame(merged_data)
        final_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"已将 {len(merged_data)} 个唯一 '流水號' 合并到 {output_csv_path}")
    else:
        print("没有数据可合并。")

if __name__ == "__main__":
    # 使用原始字符串指定路径
    zip_path = r"C:\Users\pt5156\Downloads\callinter-analysis-result-transcription-20250921.zip"
    output_csv_path = r"C:\Users\pt5156\Desktop\0921-merged_data.csv"
    
    merge_csvs_from_zip(zip_path, output_csv_path)
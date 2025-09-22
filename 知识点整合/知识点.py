import pandas as pd
from bs4 import BeautifulSoup
import re
import warnings
warnings.filterwarnings('ignore')  # Suppress warnings for cleaner output

# Function to clean HTML tags from text
def clean_html(text):
    if pd.isna(text):
        return text
    soup = BeautifulSoup(str(text), 'html.parser')
    cleaned = soup.get_text(separator=' ', strip=True)
    # Remove extra spaces and newlines
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else None

# Read the Excel file generated previously
try:
    df = pd.read_excel('knowledge_points-手机及配件.xlsx', sheet_name='Sheet1', engine='openpyxl')
except FileNotFoundError:
    print("Error: 'knowledge_points-手机及配件.xlsx' not found. Please run the previous script first.")
    exit(1)

# Clean HTML in all columns
for col in df.columns:
    df[col] = df[col].apply(clean_html)

# Rename columns to remove "(必填)" and prepare for exclusion
df = df.rename(columns={
    '(必填)名称': '名称',
    '(必填)知识类型': '知识类型',
    '(必填)知识路径': '知识路径',
    '(必填)有效期': '有效期',
    '(必填)适用地市': '适用地市',  # Will be dropped later
    '(必填)渠道': '渠道'  # Will be dropped later
})

# Define columns to exclude (including city and channel related)
exclude_columns = ['适用地市', '渠道', '办理渠道']

# Filter out excluded columns
df_filtered = df[[col for col in df.columns if col not in exclude_columns]]

# Group by '名称' which is now the '服务或产品' column
df_filtered = df_filtered.rename(columns={'名称': '服务或产品'})

# Create a new DataFrame for the knowledge base
knowledge_base = []

# Group by '服务或产品'
grouped = df_filtered.groupby('服务或产品')

for name, group in grouped:
    # Merge all other columns into a single '知识点' string
    knowledge_point = ''
    for col in group.columns[1:]:  # Skip the '服务或产品' column
        col_values = group[col].dropna().unique()  # Get unique non-NaN values
        if len(col_values) > 0:
            knowledge_point += f"{col}: {'; '.join(map(str, col_values))}\n"

    knowledge_base.append({'服务或产品': name, '知识点': knowledge_point.strip()})

df_filtered = df_filtered.rename(columns={'名称': '服务或产品'})
# Convert to DataFrame
kb_df = pd.DataFrame(knowledge_base)

# Save to new Excel
output_file = 'agent_knowledge_base-手机及配件.xlsx'
kb_df.to_excel(output_file, index=False, engine='openpyxl')
print(f"Agent knowledge base Excel file '{output_file}' generated successfully.")

# Note: Further merging logic can be added as needed for other repetitive fields



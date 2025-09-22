import pandas as pd
import requests
import os

# 配置參數
APP_ID = 'cli_a8edcf446832900d'         
APP_SECRET = '0rN42bBGGY4naOHCHoSH1R5xv2clUjfX' 
APP_TOKEN = 'HYn6bLvxVa9lzdsNIwXcRNa4nEh'  
TABLE_ID = 'tblgYLosjgxyPFrJ'             
BASE_URL = 'https://open.feishu.cn/open-apis'
csv_file_path = r'C:\Users\pt5156\Desktop\combined_csv.csv'

# 獲取tenant_access_token
def get_tenant_access_token(app_id, app_secret):
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get('tenant_access_token')
    else:
        raise Exception(f"獲取token失敗: {response.text}")

# 添加記錄到飛書多維表格
def add_record_to_table(token, app_token, table_id, record_data):
    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"fields": record_data}
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    if result.get('code') == 0:  # 飛書成功code是0
        print(f"記錄添加成功: {result}")
    else:
        print(f"添加記錄失敗: {result}")

# 獲取表格欄位（用於調試）
def get_table_fields(token, app_token, table_id):
    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/meta/fields"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        fields = response.json().get('data', {}).get('fields', [])
        field_names = [field.get('name') for field in fields]
        print("飛書表格欄位名:", field_names)
        return field_names
    else:
        print(f"獲取欄位失敗: {response.text}")
        return []

def main():
    if not os.path.exists(csv_file_path):
        print(f"文件 {csv_file_path} 不存在，請檢查路徑！")
        return

    token = get_tenant_access_token(APP_ID, APP_SECRET)
    fields = get_table_fields(token, APP_TOKEN, TABLE_ID)  # 調試：獲取飛書欄位

    try:
        # 嘗試讀取文件，處理混合類型和列名
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            print("文件前5行內容：")
            for i, line in enumerate(file):
                if i < 5:
                    print(line.strip())
                else:
                    break

        df = pd.read_csv(csv_file_path, encoding='utf-8', low_memory=False)
        df.columns = df.columns.str.strip().str.replace('\n', '')  # 清理列名空格和換行
        print("清理後的CSV列名:", df.columns.tolist())  # 調試：查看CSV列名
    except UnicodeDecodeError as e:
        print(f"解碼錯誤: {e}. 嘗試使用'gbk'編碼...")
        df = pd.read_csv(csv_file_path, encoding='gbk', low_memory=False)
    except Exception as e:
        print(f"讀取CSV失敗: {e}")
        return

    for _, row in df.iterrows():
        record_data = {}
        # 字段映射（根據飛書實際欄位名調整）
        field_mapping = {
            '流水號': '流水號',
            'Transcription': 'Transcription',
            '技能隊列編號': '技能隊列編號',
            '坐席姓名': '坐席姓名',
            '主叫號碼': '主叫號碼',
            '被叫號碼': '被叫號碼',
        }
        # 處理投訴分類，合併多個欄位
        complaint_fields = ['投訴分類-二級', '投訴分類-三級', '投訴分類-四級', '投訴分類-五級', '投訴分類-六級', '投訴分類-七級']
        complaint_values = [str(row[field]) for field in complaint_fields if field in df.columns and pd.notna(row[field])]
        if complaint_values:
            record_data['投訴分類'] = ';'.join(complaint_values)

        # 映射其他字段
        for excel_col, feishu_col in field_mapping.items():
            if excel_col in df.columns and pd.notna(row[excel_col]):
                record_data[feishu_col] = str(row[excel_col])

        if record_data:
            add_record_to_table(token, APP_TOKEN, TABLE_ID, record_data)

if __name__ == "__main__":
    main()
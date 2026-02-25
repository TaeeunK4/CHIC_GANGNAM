import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

cg_file = '01_CG_eBay_active_listing_data_cleaned.csv'
db_file = '00_DB_eBay_active_listing_data.csv'
output_file = '02_CG_eBay_active_listing_data_filtered.csv'

cg_path = os.path.join(script_dir, cg_file)
db_path = os.path.join(script_dir, db_file)
output_path = os.path.join(script_dir, output_file)

df_cg = pd.read_csv(cg_path)
print(f'데이터 로드 완료:{cg_file}')
df_db = pd.read_csv(db_path)
print(f'데이터 로드 완료:{db_file}')

df_results = pd.merge(df_cg, df_db, how='left', left_on='Custom label (SKU)', right_on='origin_id')
print(f'데이터 병합 완료:{cg_file} 과 {db_file}')
df_results = df_results[['Item number', 'origin_id', 'Title', 'eBay category 1 name', 'raw_data']]

df_results.to_csv(output_path, index=False)

print(f'데이터 저장 완료:{output_file}')
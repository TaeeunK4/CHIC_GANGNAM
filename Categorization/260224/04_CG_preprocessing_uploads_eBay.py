import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = '05_CG_eBay_active_listing_data_subcategorized.csv'
output_file = '06_CG_eBay_uploads_file.csv'

input_path = os.path.join(script_dir, input_file)
output_path = os.path.join(script_dir, output_file)


df = pd.read_csv(input_path)

# 시크 강남 Category_id 지정
# Category == Accessaries
df.loc[(df['Category'] == 'Accessaries') & (df['Subcategory'] == 'Bracelets'), 'Category_id'] = 42101761010
df.loc[(df['Category'] == 'Accessaries') & (df['Subcategory'] == 'Earrings'), 'Category_id'] = 42103078010
df.loc[(df['Category'] == 'Accessaries') & (df['Subcategory'] == 'Necklaces'), 'Category_id'] = 42101762010
df.loc[(df['Category'] == 'Accessaries') & (df['Subcategory'] == 'Rings'), 'Category_id'] = 42101763010
df.loc[(df['Category'] == 'Accessaries') & (df['Subcategory'] == 'Others'), 'Category_id'] = 42101764010

# Category == Bags
df.loc[(df['Category'] == 'Bags') & (df['Subcategory'] == 'Crossbody'), 'Category_id'] = 42101755010
df.loc[(df['Category'] == 'Bags') & (df['Subcategory'] == 'Clutch'), 'Category_id'] = 42101756010
df.loc[(df['Category'] == 'Bags') & (df['Subcategory'] == 'Shoulder'), 'Category_id'] = 42101757010
df.loc[(df['Category'] == 'Bags') & (df['Subcategory'] == 'Tote'), 'Category_id'] = 42101758010
df.loc[(df['Category'] == 'Bags') & (df['Subcategory'] == 'Others'), 'Category_id'] = 42101759010

# Category == Clothes
df.loc[(df['Category'] == 'Clothes') & (df['Subcategory'] == 'Outer'), 'Category_id'] = 42101765010
df.loc[(df['Category'] == 'Clothes') & (df['Subcategory'] == 'Pants & Skirts'), 'Category_id'] = 42101766010
df.loc[(df['Category'] == 'Clothes') & (df['Subcategory'] == 'Tops'), 'Category_id'] = 42101767010
df.loc[(df['Category'] == 'Clothes') & (df['Subcategory'] == 'Dress'), 'Category_id'] = 42103319010
df.loc[(df['Category'] == 'Clothes') & (df['Subcategory'] == 'Others'), 'Category_id'] = 42101768010

# Category == Shoes
df.loc[(df['Category'] == 'Shoes') & (df['Subcategory'] == 'Boots'), 'Category_id'] = 42101769010
df.loc[(df['Category'] == 'Shoes') & (df['Subcategory'] == 'Heels'), 'Category_id'] = 42101770010
df.loc[(df['Category'] == 'Shoes') & (df['Subcategory'] == 'Dress'), 'Category_id'] = 42101771010
df.loc[(df['Category'] == 'Shoes') & (df['Subcategory'] == 'Sneakers'), 'Category_id'] = 42101772010
df.loc[(df['Category'] == 'Shoes') & (df['Subcategory'] == 'Others'), 'Category_id'] = 42101773010

# Category == Watches
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Breitling'), 'Category_id'] = 42101774010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Cartier'), 'Category_id'] = 42101775010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Ferragamo'), 'Category_id'] = 42101776010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Gucci'), 'Category_id'] = 42101777010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Mido'), 'Category_id'] = 42101778010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Montblanc'), 'Category_id'] = 42101779010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Omega'), 'Category_id'] = 42101780010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Tag Heuer'), 'Category_id'] = 42101781010
df.loc[(df['Category'] == 'Watches') & (df['Subcategory'] == 'Others'), 'Category_id'] = 42101782010

df_upload = pd.DataFrame({
    'Action': 'Revise',
    'ItemID': df['Item number'].astype(str),
    'StoreCategory': df['Category_id'].fillna(0).astype(int).astype(str)
})

df_upload = df_upload[df_upload['StoreCategory'] != '0']

df_upload.to_csv(output_path, index=False, encoding='utf-8')
print(f'파일 저장 완료 : {output_file}')
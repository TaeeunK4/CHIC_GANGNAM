import pandas as pd
import os

def get_subcategory_bags(title_value):
    """
    Bags 카테고리의 하위 카테고리 분류 (Title 기준)
    """
    if pd.isna(title_value) or title_value == '':
        return 'Others'

    title_lower = str(title_value).lower()
    title_words = title_lower.split()

    # Shoulder
    if any(keyword in title_words for keyword in ['shoulder']):
        return 'Shoulder'

    # Tote
    if any(keyword in title_words for keyword in ['tote', 'totes']):
        return 'Tote'

    # Crossbody
    if any(keyword in title_words for keyword in ['crossbody', 'cross-body']):
        return 'Crossbody'

    # Clutch
    if any(keyword in title_words for keyword in ['hand', 'handbag', 'handbags', 'clutch', 'clutches']):
        return 'Clutch'

    # Others
    return 'Others'

def get_subcategory_clothes(title_value):
    """
    Clothes 카테고리의 하위 카테고리 분류 (Title 기준)
    """
    if pd.isna(title_value) or title_value == '':
        return 'Others'

    title_lower = str(title_value).lower()
    title_words = title_lower.split()

    # Outer
    if any(keyword in title_words for keyword in ['outer', 'outerwear', 'coat', 'coats', 'jacket', 'jackets',
                                                   'blazer', 'blazers', 'vest', 'vests', 'puffer', 'bomber',
                                                   'biker', 'trench', 'windbreaker']):
        return 'Outer'

    # Tops
    if any(keyword in title_words for keyword in ['top', 'tops', 'shirt', 'shirts', 'blouse', 'blouses',
                                                   't-shirt', 't-shirts', 'sweater', 'sweaters', 'cardigan',
                                                   'cardigans', 'hoodie', 'hoodies', 'sweatshirt', 'sweatshirts',
                                                   'knit', 'sheer', 'jersey', 'polo']):
        return 'Tops'

    # Pants & Skirts
    if any(keyword in title_words for keyword in ['pant', 'pants', 'trouser', 'trousers', 'jean', 'jeans',
                                                   'short', 'shorts', 'skirt', 'skirts', 'jogging',
                                                   'legging', 'leggings', 'denim']):
        return 'Pants & Skirts'

    # Dresses
    if any(keyword in title_words for keyword in ['dress', 'dresses', 'gown', 'gowns', 'one-piece']):
        return 'Dress'

    # Others
    return 'Others'

def get_subcategory_shoes(title_value):
    """
    Shoes 카테고리의 하위 카테고리 분류 (Title 기준)
    """
    if pd.isna(title_value) or title_value == '':
        return 'Others'

    title_lower = str(title_value).lower()
    title_words = title_lower.split()

    # Sneakers
    if any(keyword in title_words for keyword in ['sneaker', 'sneakers', 'athletic', 'sport', 'running',
                                                   'lace-up', 'low-top', 'high-top']):
        return 'Sneakers'

    # Heels
    if any(keyword in title_words for keyword in ['heel', 'heels', 'pump', 'pumps', 'stiletto', 'wedge', 'wedges']):
        return 'Heels'

    # Loafers
    if any(keyword in title_words for keyword in ['loafer', 'loafers', 'moccasin', 'moccasins', 'driving', 'dress']):
        return 'Dress'

    # Boots
    if any(keyword in title_words for keyword in ['boot', 'boots', 'ankle', 'knee', 'combat']):
        return 'Boots'

    # Others
    return 'Others'

def get_subcategory_watches(brand_value):
    """
    Watches 카테고리의 하위 카테고리 분류 (Brand 기준)
    """
    if pd.isna(brand_value) or brand_value == '':
        return 'Others'
    
    brand_lower = str(brand_value).lower()
    
    # 지정된 브랜드들
    watch_brands = {
        'tag heuer': 'Tag Heuer',
        'cartier': 'Cartier',
        'montblanc': 'Montblanc',
        'gucci': 'Gucci',
        'ferragamo': 'Ferragamo',
        'salvatore ferragamo': 'Ferragamo',
        'mido': 'Mido',
        'omega': 'Omega',
        'breitling': 'Breitling'
    }
    
    for brand_key, brand_name in watch_brands.items():
        if brand_key in brand_lower:
            return brand_name
    
    # Others
    return 'Others'

def get_subcategory_accessaries(title_value):
    """
    Accessaries 카테고리의 하위 카테고리 분류 (eBay category 1 name 기준)
    """
    if pd.isna(title_value) or title_value == '':
        return 'Others'

    title_lower = str(title_value).lower()
    title_words = title_lower.split()

    # Earrings
    if any(keyword in title_words for keyword in ['earring', 'earrings']):
        return 'Earrings'

    # Rings
    if any(keyword in title_words for keyword in ['ring', 'rings']):
        return 'Rings'

    # Bracelets
    if any(keyword in title_words for keyword in ['bracelet', 'bracelets']):
        return 'Bracelets'

    # Necklaces
    if any(keyword in title_words for keyword in ['necklace', 'necklaces']):
        return 'Necklaces'

    # Others
    return 'Others'

def add_subcategory_column():
    """
    CSV 파일에 Subcategory 칼럼 추가
    """
    # 현재 스크립트가 있는 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    input_file = '04_CG_eBay_active_listing_data_categorized.csv'
    output_file = '05_CG_eBay_active_listing_data_subcategorized.csv'  # 같은 파일에 덮어쓰기
    
    print(f"파일 읽기 중: {input_file}")
    
    # 청크 단위로 읽기 (대용량 파일 처리)
    chunk_size = 10000
    chunks_processed = []
    total_rows = 0
    
    try:
        for chunk_num, chunk in enumerate(pd.read_csv(input_file, chunksize=chunk_size, dtype=str), 1):
            print(f"  청크 {chunk_num} 처리 중... ({len(chunk)}개 행)")
            
            # Subcategory 칼럼 생성
            subcategories = []
            
            for idx, row in chunk.iterrows():
                category = row.get('Category', '')
                
                if category == 'Bags':
                    subcategory = get_subcategory_bags(row.get('Title', ''))
                elif category == 'Clothes':
                    subcategory = get_subcategory_clothes(row.get('Title', ''))
                elif category == 'Shoes':
                    subcategory = get_subcategory_shoes(row.get('Title', ''))
                elif category == 'Watches':
                    subcategory = get_subcategory_watches(row.get('brand', ''))
                elif category == 'Accessaries':
                    subcategory = get_subcategory_accessaries(row.get('Title', ''))
                else:  # Others 또는 기타
                    subcategory = 'Others'
                
                subcategories.append(subcategory)
            
            chunk['Subcategory'] = subcategories
            chunks_processed.append(chunk)
            total_rows += len(chunk)
        
        # 모든 청크 합치기
        print(f"\n모든 청크 합치는 중... (총 {total_rows}개 행)")
        df_result = pd.concat(chunks_processed, ignore_index=True)
        
        # 결과 저장
        print(f"\n결과 저장 중: {output_file}")
        df_result.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\n=== 완료 ===")
        print(f"총 행 수: {len(df_result)}")
        
        print(f"\n=== 카테고리별 하위 카테고리 분포 ===")
        for category in ['Bags', 'Clothes', 'Shoes', 'Watches', 'Accessaries', 'Others']:
            category_data = df_result[df_result['Category'] == category]
            if len(category_data) > 0:
                print(f"\n{category} ({len(category_data)}개):")
                subcat_counts = category_data['Subcategory'].value_counts()
                for subcat, count in subcat_counts.items():
                    percentage = (count / len(category_data)) * 100
                    print(f"  - {subcat}: {count}개 ({percentage:.2f}%)")
        
        print(f"\n=== 샘플 데이터 (처음 10개 행) ===")
        sample_cols = ['Title', 'category', 'subcategory','Brand', 'eBay category 1 name']
        available_cols = [col for col in sample_cols if col in df_result.columns]
        print(df_result[available_cols].head(10).to_string())
        
        print(f"\n파일 저장 완료: {output_file}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_subcategory_column()
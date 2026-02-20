import pandas as pd
import os
import numpy as np

def categorize_ebay_category(title_name):
    """
    Title을 카테고리로 분류
    """
    # category_name 없으면 Others로 분류
    if pd.isna(title_name) or title_name == '':
        return 'Others'
    # category_name을 소문자로 변환하고 공백 기준으로 단어 리스트 생성
    title_lower = str(title_name).lower()
    title_words = title_lower.split()

    # Bags 카테고리
    bag_keywords = ['bag', 'bags', 'handbag', 'handbags', 'wallet', 'wallets',
                   'clutch', 'clutches', 'tote', 'totes', 'duffel', 'duffels',
                   'luggage', 'backpack', 'backpacks', 'crossbody', 'cross-body',
                   'pouch', 'pouches', 'shoulder']
    if any(keyword in title_words for keyword in bag_keywords):
        return 'Bags'
    
    # Watches 카테고리
    watch_keywords = ['watch', 'watches', 'wristwatch', 'wristwatches', 'timepiece', 'timepieces']
    if any(keyword in title_words for keyword in watch_keywords):
        return 'Watches'
    
    # Shoes 카테고리
    shoe_keywords = ['shoe', 'shoes', 'heel', 'heels', 'boot', 'boots',
                    'sandal', 'sandals', 'slipper', 'slippers', 'flat', 'flats',
                    'sneaker', 'sneakers', 'loafer', 'loafers', 'pump', 'pumps',
                    'espadrille', 'espadrilles', 'mule', 'mules', 'athletic',
                    'sport', 'running', 'lace-up', 'low-top', 'high-top',
                    'stiletto', 'stilettos', 'wedge', 'wedges', 'moccasin', 'moccasins',
                    'ankle', 'knee', 'combat']
    if any(keyword in title_words for keyword in shoe_keywords):
        return 'Shoes'

    # Clothes 카테고리
    clothes_keywords = ['coat', 'coats', 'jacket', 'jackets', 'vest', 'vests',
                       'sweater', 'sweaters', 'top', 'tops', 'shirt', 'shirts',
                       'blouse', 'blouses', 't-shirt', 't-shirts', 'pants',
                       'trouser', 'trousers', 'jean', 'jeans', 'short', 'shorts',
                       'skirt', 'skirts', 'dress', 'dresses', 'suit', 'suits',
                       'blazer', 'blazers', 'hoodie', 'hoodies', 'sweatshirt',
                       'sweatshirts', 'cardigan', 'cardigans', 'jogging',
                       'activewear', 'outerwear', 'sleepwear', 'robe', 'robes',
                       'kimono', 'kimonos', 'outer', 'puffer', 'puffers', 'bomber',
                       'bombers', 'biker', 'bikers', 'trench', 'trenches',
                       'windbreaker', 'windbreakers', 'knit', 'knits', 'sheer',
                       'jersey', 'jerseys', 'polo', 'polos', 'pant', 'legging',
                       'leggings', 'denim', 'gown', 'gowns', 'one-piece']
    if any(keyword in title_words for keyword in clothes_keywords):
        return 'Clothes'
    
    # Accessaries 카테고리
    accessory_keywords = ['belt', 'belts', 'scarf', 'scarves', 'glove', 'gloves',
                         'hat', 'hats', 'cap', 'caps', 'sunglass', 'sunglasses',
                         'jewelry', 'bracelet', 'bracelets', 'necklace', 'necklaces',
                         'ring', 'rings', 'earring', 'earrings', 'tie', 'ties',
                         'cufflink', 'cufflinks', 'umbrella', 'umbrellas',
                         'keychain', 'keychains']
    if any(keyword in title_words for keyword in accessory_keywords):
        return 'Accessaries'
    
    # 그 외는 Others
    return 'Others'

def add_category_column():
    """
    CSV 파일에 Category 칼럼 추가
    """
    # 현재 스크립트가 있는 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    input_file = '03_CG_eBay_active_listing_data_filtered_with_brand.csv'
    output_file = '04_CG_eBay_active_listing_data_categorized.csv'
    
    print(f"파일 읽기 중: {input_file}")
    
    # 청크 단위로 읽기 (대용량 파일 처리)
    chunk_size = 10000
    chunks_processed = []
    total_rows = 0
    
    try:
        for chunk_num, chunk in enumerate(pd.read_csv(input_file, chunksize=chunk_size, dtype=str), 1):
            print(f"  청크 {chunk_num} 처리 중... ({len(chunk)}개 행)")
            
            # Category 칼럼 생성
            chunk['Category'] = chunk['Title'].apply(categorize_ebay_category)
            
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
        print(f"\n=== 카테고리 분포 ===")
        category_counts = df_result['Category'].value_counts()
        for category, count in category_counts.items():
            percentage = (count / len(df_result)) * 100
            print(f"  {category}: {count}개 ({percentage:.2f}%)")
        
        print(f"\n=== 샘플 데이터 (처음 10개 행) ===")
        sample_cols = ['Title', 'Category']
        if all(col in df_result.columns for col in sample_cols):
            print(df_result[sample_cols].head(10).to_string())
        else:
            print(df_result.head(10).to_string())
        
        print(f"\n파일 저장 완료: {output_file}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_category_column()
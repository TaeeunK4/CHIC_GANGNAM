"""
eBay 명품 시계 판매 완료 데이터 수집 스크립트 (Serapi 활용)
수집 데이터: 판매일자, 가격, 상품제목, 색상, 종류, 모델
"""

import os
import pandas as pd
from serpapi import GoogleSearch
from datetime import datetime
import time
import re

# Serapi API 키 설정 (환경변수 또는 직접 입력)
API_KEY = os.getenv('SERPAPI_KEY', 'd266baa616db5d4f6a54863181fb1578c4eb6e2aa2888610f77155199b31b36c')

# 명품 시계 브랜드 리스트
LUXURY_WATCH_BRANDS = [
    'Rolex',
    'Patek Philippe',
    'Audemars Piguet',
    'Omega',
    'Cartier',
    'Tag Heuer',
    'Breitling',
    'IWC',
    'Panerai',
    'Jaeger-LeCoultre',
    'Vacheron Constantin',
    'A. Lange & Söhne',
    'Hublot',
    'Richard Mille',
    'Tudor'
]

def extract_color_from_title(title):
    """상품 제목에서 색상 추출"""
    colors = ['black', 'white', 'red', 'blue', 'brown', 'pink', 'green',
              'beige', 'gray', 'grey', 'navy', 'tan', 'gold', 'silver',
              'yellow', 'purple', 'orange', 'rose gold', 'two-tone', 'steel',
              'platinum', 'titanium', 'bronze', 'copper']

    title_lower = title.lower()
    for color in colors:
        if color in title_lower:
            return color.capitalize()
    return 'Unknown'

def extract_watch_type_from_title(title):
    """상품 제목에서 시계 종류 추출"""
    watch_types = ['automatic', 'quartz', 'chronograph', 'diver', 'dress',
                   'pilot', 'sport', 'gmt', 'tourbillon', 'perpetual',
                   'moonphase', 'skeleton', 'smartwatch', 'digital', 'analog']

    title_lower = title.lower()
    for watch_type in watch_types:
        if watch_type in title_lower:
            return watch_type.capitalize()
    return 'Watch'

def extract_case_material(title):
    """상품 제목에서 케이스 재질 추출"""
    materials = ['stainless steel', 'steel', 'gold', 'rose gold', 'white gold',
                 'yellow gold', 'platinum', 'titanium', 'ceramic', 'bronze',
                 'carbon', 'rubber']

    title_lower = title.lower()
    for material in materials:
        if material in title_lower:
            return material.title()
    return 'Unknown'

def extract_gender(title):
    """상품 제목에서 성별 추출"""
    title_lower = title.lower()
    if "men's" in title_lower or "mens" in title_lower:
        return "Men"
    elif "women's" in title_lower or "womens" in title_lower or "ladies" in title_lower:
        return "Women"
    elif "unisex" in title_lower:
        return "Unisex"
    return "Unknown"

def fetch_ebay_sold_watches(brand, max_pages=10):
    """
    특정 브랜드의 판매 완료된 명품 시계 데이터 수집

    Args:
        brand: 브랜드명
        max_pages: 최대 페이지 수 (기본 10페이지)

    Returns:
        list: 판매 완료 상품 리스트
    """
    all_items = []

    for page in range(max_pages):
        print(f"Fetching {brand} - Page {page + 1}/{max_pages}...")

        params = {
            "api_key": API_KEY,
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "_nkw": f"{brand} watch",  # 검색 키워드
            "LH_Sold": "1",  # 판매 완료 필터
            "LH_Complete": "1",  # 거래 완료 필터
            "_pgn": page + 1,  # 페이지 번호
            "_ipg": "100"  # 페이지당 결과 수 (최대 100)
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            # 에러 체크
            if "error" in results:
                print(f"❌ API Error: {results['error']}")
                break

            if "organic_results" not in results:
                if page == 0:
                    print(f"⚠️ No results found for {brand}")
                break

            items = results.get("organic_results", [])

            if not items:
                break

            for item in items:
                # 데이터 추출
                try:
                    # 가격 추출
                    price_raw = 'N/A'
                    if isinstance(item.get('price'), dict):
                        price_raw = item.get('price', {}).get('raw', 'N/A')
                    elif isinstance(item.get('price'), str):
                        price_raw = item.get('price')

                    # 판매 날짜 추출 (extensions에서)
                    sold_date = 'N/A'
                    extensions = item.get('extensions', [])
                    if extensions:
                        for ext in extensions:
                            if 'Sold' in ext or 'sold' in ext:
                                sold_date = ext
                                break

                    title = item.get('title', '')

                    product_data = {
                        'brand': brand,
                        'title': title,
                        'price': price_raw,
                        'sold_date': sold_date,
                        'condition': item.get('condition', 'N/A'),
                        'shipping': item.get('shipping', 'N/A'),
                        'location': item.get('location', 'N/A'),
                        'link': item.get('link', ''),
                        'color': extract_color_from_title(title),
                        'watch_type': extract_watch_type_from_title(title),
                        'case_material': extract_case_material(title),
                        'gender': extract_gender(title)
                    }
                    all_items.append(product_data)
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

            # API 호출 제한 방지를 위한 대기
            time.sleep(1)

        except Exception as e:
            print(f"Error fetching page {page + 1} for {brand}: {e}")
            break

    return all_items

def clean_price(price_str):
    """가격 문자열을 숫자로 변환"""
    if isinstance(price_str, str):
        # $ 기호와 쉼표 제거
        price_clean = re.sub(r'[$,]', '', price_str)
        try:
            return float(price_clean)
        except:
            return None
    return price_str

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("eBay 명품 시계 판매 완료 데이터 수집 시작")
    print("=" * 60)

    all_data = []

    # 각 브랜드별로 데이터 수집
    for brand in LUXURY_WATCH_BRANDS:
        print(f"\n🔍 Collecting data for: {brand}")
        brand_data = fetch_ebay_sold_watches(brand, max_pages=10)
        all_data.extend(brand_data)
        print(f"✓ Collected {len(brand_data)} items for {brand}")

    # DataFrame 생성
    df = pd.DataFrame(all_data)

    if df.empty:
        print("\n⚠️ No data collected. Please check your API key and internet connection.")
        return

    # 가격 정리
    df['price_cleaned'] = df['price'].apply(clean_price)

    # 최종 컬럼 선택 및 이름 변경
    final_df = df[[
        'brand',
        'title',
        'price',
        'price_cleaned',
        'sold_date',
        'color',
        'watch_type',
        'case_material',
        'gender',
        'condition',
        'shipping',
        'location',
        'link'
    ]].copy()

    # 컬럼명 변경 (영어로)
    final_df.columns = [
        'Brand',
        'Product_Title',
        'Price_Original',
        'Price_USD',
        'Sold_Date',
        'Color',
        'Watch_Type',
        'Case_Material',
        'Gender',
        'Condition',
        'Shipping',
        'Location',
        'Product_Link'
    ]

    # 결과 저장
    output_file = f'ebay_luxury_watches_sold_{datetime.now().strftime("%Y%m%d")}.csv'
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n" + "=" * 60)
    print(f"✅ Data collection completed!")
    print(f"📊 Total items collected: {len(final_df)}")
    print(f"💾 Saved to: {output_file}")
    print("=" * 60)

    # 간단한 통계 출력
    print("\n📈 Summary Statistics:")
    print(f"   - Brands collected: {final_df['Brand'].nunique()}")
    print(f"   - Date range: {final_df['Sold_Date'].min()} to {final_df['Sold_Date'].max()}")
    if final_df['Price_USD'].notna().sum() > 0:
        print(f"   - Average price: ${final_df['Price_USD'].mean():.2f}")
        print(f"   - Price range: ${final_df['Price_USD'].min():.2f} - ${final_df['Price_USD'].max():.2f}")

    print("\n🎨 Top 5 Colors:")
    print(final_df['Color'].value_counts().head())

    print("\n⌚ Top 5 Watch Types:")
    print(final_df['Watch_Type'].value_counts().head())

    print("\n🔧 Top 5 Case Materials:")
    print(final_df['Case_Material'].value_counts().head())

    print("\n👤 Gender Distribution:")
    print(final_df['Gender'].value_counts())

    return final_df

if __name__ == "__main__":
    # API 키 확인
    if not API_KEY or API_KEY == 'YOUR_API_KEY_HERE':
        print("⚠️ Please set your SERPAPI_KEY!")
        print("Option 1: Set environment variable: export SERPAPI_KEY='your_key'")
        print("Option 2: Replace 'YOUR_API_KEY_HERE' in the code with your actual API key")
        print("\nGet your free API key at: https://serpapi.com/")
    else:
        df = main()

"""
eBay 명품 백 판매 완료 데이터 수집 스크립트 (Serapi 활용)
수집 데이터: 판매일자, 가격, 상품제목, 색상, 종류
"""

import os
import pandas as pd
from serpapi import GoogleSearch
from datetime import datetime
import time
import re

# Serapi API 키 설정 (환경변수 또는 직접 입력)
API_KEY = os.getenv('SERPAPI_KEY', 'd266baa616db5d4f6a54863181fb1578c4eb6e2aa2888610f77155199b31b36c')

# 명품 브랜드 리스트 (브랜드 파싱용)
LUXURY_BRANDS = [
    'Louis Vuitton',
    'Chanel',
    'Hermes',
    'Hermès',
    'Gucci',
    'Prada',
    'Dior',
    'Fendi',
    'Celine',
    'Balenciaga',
    'Bottega Veneta',
    'Saint Laurent',
    'Yves Saint Laurent',
    'YSL',
    'Givenchy',
    'Valentino',
    'Burberry',
    'Michael Kors',
    'Coach',
    'Kate Spade',
    'Marc Jacobs',
    'Versace',
    'Dolce & Gabbana',
    'Dolce Gabbana',
    'Salvatore Ferragamo',
    'Ferragamo',
    'Mulberry',
    'Alexander McQueen',
    'Stella McCartney',
    'Loewe',
    'Goyard'
]

# 통합 검색 키워드 (전체 시장 데이터 수집용)
SEARCH_KEYWORDS = [
    'luxury designer bag authentic',
    'designer handbag authentic',
    'luxury handbag'
]

def extract_brand_from_title(title):
    """상품 제목에서 브랜드 추출"""
    title_lower = title.lower()

    # 브랜드 리스트를 길이순으로 정렬 (긴 것부터 매칭 - 'Louis Vuitton'이 'Louis'보다 먼저)
    sorted_brands = sorted(LUXURY_BRANDS, key=len, reverse=True)

    for brand in sorted_brands:
        if brand.lower() in title_lower:
            # 원본 브랜드명 중 가장 대표적인 것으로 통일
            if brand.lower() in ['ysl', 'yves saint laurent']:
                return 'Saint Laurent'
            elif brand.lower() in ['hermès']:
                return 'Hermes'
            elif brand.lower() in ['dolce gabbana', 'dolce & gabbana']:
                return 'Dolce & Gabbana'
            elif brand.lower() in ['ferragamo']:
                return 'Salvatore Ferragamo'
            else:
                return brand

    return 'Other'

def extract_color_from_title(title):
    """상품 제목에서 색상 추출"""
    colors = ['black', 'white', 'red', 'blue', 'brown', 'pink', 'green',
              'beige', 'gray', 'grey', 'navy', 'tan', 'gold', 'silver',
              'yellow', 'purple', 'orange', 'cream', 'burgundy']

    title_lower = title.lower()
    for color in colors:
        if color in title_lower:
            return color.capitalize()
    return 'Unknown'

def extract_bag_type_from_title(title):
    """상품 제목에서 가방 종류 추출"""
    bag_types = ['tote', 'shoulder', 'crossbody', 'clutch', 'backpack',
                 'hobo', 'satchel', 'wallet', 'handbag', 'purse',
                 'messenger', 'bucket', 'bowling']

    title_lower = title.lower()
    for bag_type in bag_types:
        if bag_type in title_lower:
            return bag_type.capitalize()
    return 'Handbag'

def fetch_ebay_sold_bags(keyword, max_pages=20):
    """
    통합 검색으로 판매 완료된 명품 백 데이터 수집

    Args:
        keyword: 검색 키워드
        max_pages: 최대 페이지 수 (기본 20페이지)

    Returns:
        list: 판매 완료 상품 리스트
    """
    all_items = []

    for page in range(max_pages):
        print(f"Fetching '{keyword}' - Page {page + 1}/{max_pages}...")

        params = {
            "api_key": API_KEY,
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "_nkw": keyword,  # 검색 키워드
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
                    print(f"⚠️ No results found for '{keyword}'")
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
                        'brand': extract_brand_from_title(title),
                        'title': title,
                        'price': price_raw,
                        'sold_date': sold_date,
                        'condition': item.get('condition', 'N/A'),
                        'shipping': item.get('shipping', 'N/A'),
                        'location': item.get('location', 'N/A'),
                        'link': item.get('link', ''),
                        'color': extract_color_from_title(title),
                        'bag_type': extract_bag_type_from_title(title)
                    }
                    all_items.append(product_data)
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

            # API 호출 제한 방지를 위한 대기
            time.sleep(1)

        except Exception as e:
            print(f"Error fetching page {page + 1}: {e}")
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
    print("eBay 명품 백 판매 완료 데이터 수집 시작 (전체 시장 분석)")
    print("=" * 60)

    all_data = []

    # 통합 검색으로 전체 시장 데이터 수집
    for idx, keyword in enumerate(SEARCH_KEYWORDS, 1):
        print(f"\n🔍 Collecting data for: '{keyword}' ({idx}/{len(SEARCH_KEYWORDS)})")
        keyword_data = fetch_ebay_sold_bags(keyword, max_pages=20)
        all_data.extend(keyword_data)
        print(f"✓ Collected {len(keyword_data)} items for '{keyword}'")

    # DataFrame 생성
    df = pd.DataFrame(all_data)

    if df.empty:
        print("\n⚠️ No data collected. Please check your API key and internet connection.")
        return

    # 중복 제거 (같은 상품이 여러 검색어에서 나올 수 있음)
    print(f"\n📊 Total items before deduplication: {len(df)}")
    df = df.drop_duplicates(subset=['link'], keep='first')
    print(f"📊 Total items after deduplication: {len(df)}")

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
        'bag_type',
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
        'Bag_Type',
        'Condition',
        'Shipping',
        'Location',
        'Product_Link'
    ]

    # 결과 저장
    output_file = f'ebay_luxury_bags_sold_{datetime.now().strftime("%Y%m%d")}.csv'
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("\n" + "=" * 60)
    print(f"✅ Data collection completed!")
    print(f"📊 Total items collected: {len(final_df)}")
    print(f"🔍 Search keywords used: {len(SEARCH_KEYWORDS)}")
    print(f"💾 Saved to: {output_file}")
    print("=" * 60)

    # 상세 통계 출력
    print("\n" + "=" * 60)
    print("📈 전체 시장 판매량 분석")
    print("=" * 60)

    # 브랜드별 판매량 (상위 15개)
    print("\n🏷️ 브랜드별 판매량 (Top 15):")
    brand_counts = final_df['Brand'].value_counts().head(15)
    for idx, (brand, count) in enumerate(brand_counts.items(), 1):
        percentage = (count / len(final_df)) * 100
        print(f"   {idx:2d}. {brand:20s} - {count:4d}개 ({percentage:5.1f}%)")

    # 색상별 판매량
    print("\n🎨 색상별 판매량:")
    color_counts = final_df['Color'].value_counts().head(10)
    for idx, (color, count) in enumerate(color_counts.items(), 1):
        percentage = (count / len(final_df)) * 100
        print(f"   {idx:2d}. {color:15s} - {count:4d}개 ({percentage:5.1f}%)")

    # 가방 종류별 판매량
    print("\n👜 가방 종류별 판매량:")
    bag_type_counts = final_df['Bag_Type'].value_counts().head(10)
    for idx, (bag_type, count) in enumerate(bag_type_counts.items(), 1):
        percentage = (count / len(final_df)) * 100
        print(f"   {idx:2d}. {bag_type:15s} - {count:4d}개 ({percentage:5.1f}%)")

    # 가격 통계
    print("\n💰 가격 통계:")
    if final_df['Price_USD'].notna().sum() > 0:
        print(f"   - 평균 가격: ${final_df['Price_USD'].mean():.2f}")
        print(f"   - 중간 가격: ${final_df['Price_USD'].median():.2f}")
        print(f"   - 최저 가격: ${final_df['Price_USD'].min():.2f}")
        print(f"   - 최고 가격: ${final_df['Price_USD'].max():.2f}")

    # 브랜드별 평균 가격 (상위 10개 브랜드)
    print("\n💎 브랜드별 평균 가격 (Top 10):")
    top_brands = final_df['Brand'].value_counts().head(10).index
    brand_avg_price = final_df[final_df['Brand'].isin(top_brands)].groupby('Brand')['Price_USD'].mean().sort_values(ascending=False)
    for idx, (brand, avg_price) in enumerate(brand_avg_price.items(), 1):
        if pd.notna(avg_price):
            print(f"   {idx:2d}. {brand:20s} - ${avg_price:,.2f}")

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
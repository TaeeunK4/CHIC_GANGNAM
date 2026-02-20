"""
eBay Browsing API를 활용한 상품 사진 추출
특정 seller의 active 상품들의 이미지를 추출하여 데이터프레임으로 저장
내부 토큰 API 서버를 통한 인증 사용
"""

import requests
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
import time


class EbayPhotoExtractor:
    def __init__(self, user_id: str, token_api_url: str = 'http://callback.codegurus.co.kr:5000', environment: str = 'PRODUCTION'):
        """
        eBay Photo Extractor 초기화

        Args:
            user_id: 토큰 API의 사용자 ID (예: 'chic_gangnam')
            token_api_url: 토큰 API 서버 URL
            environment: 'PRODUCTION' 또는 'SANDBOX'
        """
        self.user_id = user_id
        self.token_api_url = token_api_url.rstrip('/')
        self.environment = environment

        # eBay API 엔드포인트 설정
        if environment == 'PRODUCTION':
            self.browse_url = 'https://api.ebay.com/buy/browse/v1'
        else:
            self.browse_url = 'https://api.sandbox.ebay.com/buy/browse/v1'

        self.access_token = None
        self.token_expiry = None

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        내부 토큰 API에서 access token 획득

        Args:
            force_refresh: True인 경우 토큰 갱신 시도 (만료 5분 이내일 때만 가능)

        Returns:
            access_token 문자열
        """
        try:
            # 1. 토큰 갱신 시도 (force_refresh가 True이거나 토큰이 없는 경우)
            if force_refresh:
                print(f"토큰 갱신 시도 중... (user_id: {self.user_id})")
                refresh_url = f"{self.token_api_url}/api/ebay/token/{self.user_id}/refresh"

                response = requests.post(refresh_url)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        token_data = data.get('data', {})
                        self.access_token = token_data.get('access_token')
                        self.token_expiry = token_data.get('expires_at')
                        print("[OK] 토큰 갱신 성공")
                        print(f"  만료 시간: {self.token_expiry}")
                        return self.access_token
                    else:
                        print(f"[WARN] 토큰 갱신 불가: {data.get('error')}")
                        # 갱신 실패 시 기존 토큰 조회로 폴백
                else:
                    print(f"[WARN] 토큰 갱신 실패 (HTTP {response.status_code}), 기존 토큰 조회 시도")

            # 2. 기존 토큰 조회
            print(f"토큰 조회 중... (user_id: {self.user_id})")
            token_url = f"{self.token_api_url}/api/ebay/token/{self.user_id}"

            response = requests.get(token_url)
            response.raise_for_status()

            result = response.json()

            if result.get('success'):
                token_data = result.get('data', {})
                self.access_token = token_data.get('access_token')
                self.token_expiry = token_data.get('expires_at')

                print("[OK] Access token 조회 성공")
                print(f"  Source: {result.get('source')}")
                print(f"  만료 시간: {self.token_expiry}")
                print(f"  Token Type: {token_data.get('token_type')}")

                return self.access_token
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"[ERROR] 토큰 조회 실패: {error_msg}")
                raise Exception(f"Token not found: {error_msg}")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 토큰 API 호출 실패: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  응답 내용: {e.response.text}")
            raise

    def refresh_token_if_needed(self) -> bool:
        """
        토큰이 만료 5분 이내인 경우 자동으로 갱신 시도

        Returns:
            갱신 성공 여부
        """
        if not self.token_expiry:
            return False

        try:
            # 만료 시간 파싱
            from datetime import datetime
            expiry = datetime.fromisoformat(self.token_expiry.replace('Z', '+00:00'))
            now = datetime.now(expiry.tzinfo) if expiry.tzinfo else datetime.now()

            time_remaining = (expiry - now).total_seconds() / 60  # 분 단위

            if time_remaining <= 5:
                print(f"[WARN] 토큰 만료까지 {time_remaining:.1f}분 남음. 갱신 시도합니다.")
                self.get_access_token(force_refresh=True)
                return True
            else:
                print(f"[OK] 토큰 유효 (만료까지 {time_remaining:.1f}분 남음)")
                return False

        except Exception as e:
            print(f"[WARN] 토큰 만료 시간 확인 중 오류: {e}")
            return False

    def search_items(self,
                     seller_username: str,
                     limit: int = 200,
                     category_ids: Optional[List[str]] = None,
                     search_query: str = '*') -> List[Dict]:
        """
        특정 seller의 active 상품 검색

        Args:
            seller_username: eBay seller 사용자명
            limit: 최대 검색 결과 수 (최대 200)
            category_ids: 카테고리 ID 리스트 (선택사항)
            search_query: 검색어 (기본값: '*' - 모든 상품)

        Returns:
            상품 정보 리스트
        """
        if not self.access_token:
            self.get_access_token()

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'  # 필요시 변경 (EBAY_KR, EBAY_GB 등)
        }

        # 검색 쿼리 구성
        filter_parts = [f'sellers:{{{seller_username}}}']
        if category_ids:
            category_filter = ','.join(category_ids)
            filter_parts.append(f'categoryIds:{{{category_filter}}}')

        params = {
            'q': search_query,  # eBay API 요구사항: q 파라미터 필수
            'filter': '|'.join(filter_parts),
            'limit': min(limit, 200)  # API 제한: 최대 200
        }

        all_items = []
        offset = 0

        try:
            while True:
                params['offset'] = offset

                response = requests.get(
                    f'{self.browse_url}/item_summary/search',
                    headers=headers,
                    params=params
                )
                response.raise_for_status()

                data = response.json()

                if 'itemSummaries' in data:
                    items = data['itemSummaries']
                    all_items.extend(items)
                    print(f"[OK] {len(items)}개 상품 검색됨 (누적: {len(all_items)})")

                    # 다음 페이지가 있는지 확인
                    if 'next' in data:
                        offset += len(items)
                        time.sleep(0.5)  # API rate limit 고려
                    else:
                        break
                else:
                    print("검색 결과가 없습니다.")
                    break

                # 최대 limit에 도달하면 중단
                if len(all_items) >= limit:
                    all_items = all_items[:limit]
                    break

            print(f"\n총 {len(all_items)}개 상품 검색 완료")
            return all_items

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 상품 검색 실패: {e}")
            if hasattr(e.response, 'text'):
                print(f"응답 내용: {e.response.text}")
            raise

    def extract_photo_data(self, items: List[Dict]) -> pd.DataFrame:
        """
        상품 리스트에서 사진 정보를 추출하여 DataFrame으로 변환

        Args:
            items: search_items()에서 반환된 상품 리스트

        Returns:
            사진 정보가 포함된 DataFrame
        """
        photo_data = []

        for item in items:
            item_id = item.get('itemId', '')
            title = item.get('title', '')
            price = item.get('price', {}).get('value', '')
            currency = item.get('price', {}).get('currency', '')
            condition = item.get('condition', '')
            item_url = item.get('itemWebUrl', '')

            # 이미지 정보 추출
            image = item.get('image', {})
            thumbnail_url = item.get('thumbnailImages', [{}])[0].get('imageUrl', '') if item.get('thumbnailImages') else ''
            main_image_url = image.get('imageUrl', '')

            # 추가 이미지들 (있는 경우)
            additional_images = item.get('additionalImages', [])
            additional_image_urls = [img.get('imageUrl', '') for img in additional_images]

            # 기본 행 데이터
            row_data = {
                'item_id': item_id,
                'title': title,
                'price': price,
                'currency': currency,
                'condition': condition,
                'item_url': item_url,
                'main_image_url': main_image_url,
                'thumbnail_url': thumbnail_url,
                'additional_images_count': len(additional_image_urls),
                'total_images_count': 1 + len(additional_image_urls),  # 메인 이미지 + 추가 이미지들
            }

            # 추가 이미지 URL들 (최대 10개까지 별도 컬럼으로)
            for i, img_url in enumerate(additional_image_urls[:10], 1):
                row_data[f'additional_image_{i}'] = img_url

            photo_data.append(row_data)

        df = pd.DataFrame(photo_data)
        print(f"[OK] {len(df)}개 상품의 사진 정보를 DataFrame으로 변환 완료")

        return df

    def save_to_csv(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        DataFrame을 CSV 파일로 저장

        Args:
            df: 저장할 DataFrame
            filename: 파일명 (None이면 자동 생성)

        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'ebay_photos_{timestamp}.csv'

        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"[OK] CSV 파일 저장 완료: {filename}")

        return filename

    def download_images(self, items_by_category: Dict[str, List[Dict]],
                       max_items_per_category: int = 10,
                       base_folder: str = 'ebay_images') -> None:
        """
        카테고리별로 이미지 다운로드

        Args:
            items_by_category: 카테고리별로 그룹화된 상품 딕셔너리
            max_items_per_category: 카테고리당 최대 다운로드 상품 수
            base_folder: 이미지 저장 기본 폴더
        """
        import urllib.request
        from pathlib import Path

        # 기본 폴더 생성
        base_path = Path(base_folder)
        base_path.mkdir(exist_ok=True)

        total_downloaded = 0

        for category, items in items_by_category.items():
            print(f"\n[{category.upper()}] 이미지 다운로드 중...")

            # 카테고리 폴더 생성
            category_path = base_path / category
            category_path.mkdir(exist_ok=True)

            # 최대 개수만큼만 선택
            selected_items = items[:max_items_per_category]

            category_downloaded = 0

            for idx, item in enumerate(selected_items, 1):
                item_id = item.get('itemId', '').replace('|', '_')
                title = item.get('title', 'untitled')[:50]  # 제목 길이 제한

                # 안전한 파일명 생성
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()

                print(f"  [{idx}/{len(selected_items)}] {safe_title}...")

                # 모든 이미지 URL 수집
                image_urls = []

                # 메인 이미지
                main_image = item.get('image', {}).get('imageUrl')
                if main_image:
                    image_urls.append(main_image)

                # 추가 이미지들
                additional_images = item.get('additionalImages', [])
                for img in additional_images:
                    img_url = img.get('imageUrl')
                    if img_url:
                        image_urls.append(img_url)

                # 이미지 다운로드
                for img_idx, img_url in enumerate(image_urls):
                    try:
                        # 파일 확장자 추출
                        ext = 'jpg'
                        if '.png' in img_url.lower():
                            ext = 'png'
                        elif '.jpeg' in img_url.lower() or '.jpg' in img_url.lower():
                            ext = 'jpg'

                        # 파일명: safe_title_item_id_image_index.ext
                        filename = f"{safe_title}_{item_id}_{img_idx + 1}.{ext}"
                        filepath = category_path / filename

                        # 이미지 다운로드
                        urllib.request.urlretrieve(img_url, filepath)
                        category_downloaded += 1

                    except Exception as e:
                        print(f"    [WARN] 이미지 다운로드 실패 ({img_url}): {e}")
                        continue

            print(f"  -> {category_downloaded}개 이미지 파일 저장 완료")
            total_downloaded += category_downloaded

        print(f"\n[OK] 총 {total_downloaded}개 이미지 파일 다운로드 완료")
        print(f"[OK] 저장 위치: {base_path.absolute()}")


def main():
    """메인 실행 함수"""

    # 환경 변수에서 설정 로드 (또는 직접 입력)
    USER_ID = os.getenv('EBAY_USER_ID', 'chic_gangnam')  # 토큰 API 사용자 ID
    TOKEN_API_URL = os.getenv('TOKEN_API_URL', 'http://callback.codegurus.co.kr:5000')  # 토큰 API 서버 URL
    SELLER_USERNAME = os.getenv('EBAY_SELLER_USERNAME', 'CHIC_GANGNAM')

    # 환경 설정 ('PRODUCTION' 또는 'SANDBOX')
    ENVIRONMENT = 'PRODUCTION'

    # 검색 옵션
    MAX_ITEMS_PER_CATEGORY = 200  # 카테고리당 최대 검색할 상품 수

    # Store 카테고리별 검색 키워드
    SEARCH_KEYWORDS = ['bags', 'watches', 'clothes', 'shoes', 'rings']

    print("=" * 60)
    print("eBay Active 상품 사진 추출 시작")
    print("=" * 60)
    print(f"User ID: {USER_ID}")
    print(f"Token API: {TOKEN_API_URL}")
    print(f"Seller: {SELLER_USERNAME}")
    print(f"검색 카테고리: {', '.join(SEARCH_KEYWORDS)}")
    print("=" * 60)

    # Extractor 초기화
    extractor = EbayPhotoExtractor(USER_ID, TOKEN_API_URL, ENVIRONMENT)

    try:
        # 1. Access token 획득
        extractor.get_access_token()

        # 1-1. 필요시 토큰 갱신 확인
        extractor.refresh_token_if_needed()

        # 2. 카테고리별 상품 검색
        all_items = []
        items_by_category = {}  # 카테고리별로 상품 저장
        seen_item_ids = set()  # 중복 제거용

        for keyword in SEARCH_KEYWORDS:
            print(f"\n[{keyword.upper()}] 카테고리 검색 중...")
            try:
                items = extractor.search_items(
                    seller_username=SELLER_USERNAME,
                    limit=MAX_ITEMS_PER_CATEGORY,
                    search_query=keyword
                )

                # 카테고리별로 저장
                items_by_category[keyword] = items

                # 중복 제거하면서 전체 목록에 추가
                new_items = 0
                for item in items:
                    item_id = item.get('itemId')
                    if item_id and item_id not in seen_item_ids:
                        seen_item_ids.add(item_id)
                        all_items.append(item)
                        new_items += 1

                print(f"  -> {new_items}개의 새로운 상품 추가됨 (중복 제거 후)")

            except Exception as e:
                print(f"  [WARN] '{keyword}' 검색 중 오류 (건너뜀): {e}")
                continue

        print(f"\n" + "=" * 60)
        print(f"전체 검색 완료: 총 {len(all_items)}개 상품 (중복 제거 완료)")
        print("=" * 60)

        items = all_items

        if not items:
            print("검색된 상품이 없습니다.")
            return

        # 3. 사진 데이터 추출
        print("\n사진 정보 추출 중...")
        df = extractor.extract_photo_data(items)

        # 4. 데이터 미리보기
        print("\n" + "=" * 60)
        print("추출된 데이터 미리보기:")
        print("=" * 60)
        print(df.head())
        print(f"\n총 행 수: {len(df)}")
        print(f"총 컬럼 수: {len(df.columns)}")

        # 5. CSV 파일로 저장
        print("\n" + "=" * 60)
        extractor.save_to_csv(df)
        print("=" * 60)

        # 6. 통계 정보
        print("\n[STATS] 통계 정보:")
        print(f"  - 총 상품 수: {len(df)}")
        print(f"  - 평균 이미지 수/상품: {df['total_images_count'].mean():.2f}")
        print(f"  - 최대 이미지 수: {df['total_images_count'].max()}")
        print(f"  - 최소 이미지 수: {df['total_images_count'].min()}")

        # 7. 이미지 다운로드 (카테고리별로 10개씩)
        print("\n" + "=" * 60)
        print("이미지 파일 다운로드 시작 (카테고리당 10개씩)")
        print("=" * 60)

        extractor.download_images(
            items_by_category=items_by_category,
            max_items_per_category=10,
            base_folder='ebay_images'
        )

        print("\n[COMPLETE] 모든 작업 완료!")

    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        raise


if __name__ == "__main__":
    main()

"""
eBay Seller Hub - Sourcing Insights Top Opportunities 데이터 수집 스크립트
Selenium을 사용하여 자동으로 로그인 후 데이터 추출
"""

import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

# eBay 계정 정보 (환경변수 또는 직접 입력)
EBAY_USERNAME = os.getenv('EBAY_USERNAME', 'YOUR_EBAY_USERNAME')
EBAY_PASSWORD = os.getenv('EBAY_PASSWORD', 'YOUR_EBAY_PASSWORD')

# Sourcing Insights URL
SOURCING_INSIGHTS_URL = "https://www.ebay.com/sh/research/sourcing-insights"
SELLER_HUB_URL = "https://www.ebay.com/sh/ovw"

class eBaySourcerScraper:
    def __init__(self, headless=False):
        """
        eBay Sourcing Insights 스크래퍼 초기화

        Args:
            headless: 브라우저를 숨김 모드로 실행할지 여부
        """
        self.headless = headless
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # 자동화 감지 방지
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self.wait = WebDriverWait(self.driver, 20)

        print("✅ Chrome driver initialized")

    def login_to_ebay(self):
        """eBay에 로그인"""
        try:
            print("🔐 Logging in to eBay...")
            self.driver.get("https://signin.ebay.com/")
            time.sleep(2)

            # 사용자명 입력
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "userid"))
            )
            username_field.clear()
            username_field.send_keys(EBAY_USERNAME)

            # Continue 버튼 클릭
            continue_btn = self.driver.find_element(By.ID, "signin-continue-btn")
            continue_btn.click()
            time.sleep(2)

            # 비밀번호 입력
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "pass"))
            )
            password_field.clear()
            password_field.send_keys(EBAY_PASSWORD)

            # Sign in 버튼 클릭
            signin_btn = self.driver.find_element(By.ID, "sgnBt")
            signin_btn.click()

            print("⏳ Waiting for login to complete...")
            time.sleep(5)

            # 로그인 성공 확인
            if "sellerhub" in self.driver.current_url.lower() or "my.ebay" in self.driver.current_url.lower():
                print("✅ Login successful!")
                return True
            else:
                print("⚠️ Login may have failed. Please check manually.")
                return False

        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def navigate_to_sourcing_insights(self):
        """Sourcing Insights 페이지로 이동"""
        try:
            print("📊 Navigating to Sourcing Insights...")
            self.driver.get(SOURCING_INSIGHTS_URL)
            time.sleep(5)

            # 페이지 로딩 대기
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            print("✅ Arrived at Sourcing Insights page")
            return True

        except Exception as e:
            print(f"❌ Failed to navigate to Sourcing Insights: {e}")
            return False

    def extract_opportunities_data(self):
        """Top Opportunities 데이터 추출"""
        try:
            print("🔍 Extracting Top Opportunities data...")
            time.sleep(3)

            opportunities = []

            # 다양한 선택자 시도
            possible_selectors = [
                "div[class*='opportunity']",
                "div[class*='category']",
                "div[class*='insight']",
                "tr[class*='row']",
                "li[class*='item']",
                "[data-test-id*='opportunity']",
                "[data-testid*='opportunity']"
            ]

            elements_found = None
            for selector in possible_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        elements_found = elements
                        break
                except:
                    continue

            if not elements_found:
                print("⚠️ Could not find opportunities with predefined selectors")
                print("📄 Saving page source for manual inspection...")

                # 페이지 소스 저장
                page_source = self.driver.page_source
                with open('ebay_sourcing_insights_page.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)

                print("💾 Page source saved to: ebay_sourcing_insights_page.html")

                # 스크린샷 저장
                self.driver.save_screenshot('ebay_sourcing_insights_screenshot.png')
                print("📸 Screenshot saved to: ebay_sourcing_insights_screenshot.png")

                # 모든 텍스트 추출 시도
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                opportunities.append({
                    'raw_text': body_text,
                    'extraction_method': 'full_page_text'
                })

                return opportunities

            # 각 요소에서 데이터 추출
            for idx, element in enumerate(elements_found[:20], 1):  # 상위 20개만
                try:
                    opportunity_data = {
                        'index': idx,
                        'text': element.text,
                        'html': element.get_attribute('innerHTML'),
                        'class': element.get_attribute('class')
                    }

                    # 추가 정보 추출 시도
                    try:
                        # 카테고리명 찾기
                        category = element.find_element(By.CSS_SELECTOR, "[class*='category'], [class*='title'], h3, h4")
                        opportunity_data['category'] = category.text
                    except:
                        pass

                    try:
                        # 가격 정보 찾기
                        price = element.find_element(By.CSS_SELECTOR, "[class*='price'], [class*='amount']")
                        opportunity_data['price_info'] = price.text
                    except:
                        pass

                    try:
                        # 스코어/지표 찾기
                        score = element.find_element(By.CSS_SELECTOR, "[class*='score'], [class*='metric']")
                        opportunity_data['score'] = score.text
                    except:
                        pass

                    opportunities.append(opportunity_data)

                except Exception as e:
                    print(f"⚠️ Error extracting data from element {idx}: {e}")
                    continue

            print(f"✅ Extracted {len(opportunities)} opportunities")
            return opportunities

        except Exception as e:
            print(f"❌ Failed to extract opportunities: {e}")
            return []

    def save_data(self, opportunities, output_format='csv'):
        """데이터를 파일로 저장"""
        if not opportunities:
            print("⚠️ No data to save")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # DataFrame 생성
        df = pd.DataFrame(opportunities)

        # CSV 저장
        if output_format in ['csv', 'both']:
            csv_filename = f'ebay_sourcing_insights_{timestamp}.csv'
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"💾 Data saved to CSV: {csv_filename}")

        # JSON 저장
        if output_format in ['json', 'both']:
            json_filename = f'ebay_sourcing_insights_{timestamp}.json'
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(opportunities, f, ensure_ascii=False, indent=2)
            print(f"💾 Data saved to JSON: {json_filename}")

        # Excel 저장
        try:
            excel_filename = f'ebay_sourcing_insights_{timestamp}.xlsx'
            df.to_excel(excel_filename, index=False, engine='openpyxl')
            print(f"💾 Data saved to Excel: {excel_filename}")
        except:
            print("⚠️ Could not save to Excel format (openpyxl required)")

        return df

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("eBay Seller Hub - Sourcing Insights Top Opportunities Scraper")
    print("=" * 70)

    # 계정 정보 확인
    if EBAY_USERNAME == 'YOUR_EBAY_USERNAME' or EBAY_PASSWORD == 'YOUR_EBAY_PASSWORD':
        print("\n⚠️ eBay 계정 정보를 설정해주세요!")
        print("\n옵션 1: 환경변수 설정")
        print("  export EBAY_USERNAME='your_username'")
        print("  export EBAY_PASSWORD='your_password'")
        print("\n옵션 2: 코드에서 직접 수정")
        print("  EBAY_USERNAME = 'your_username'")
        print("  EBAY_PASSWORD = 'your_password'")
        return

    scraper = eBaySourcerScraper(headless=False)

    try:
        # 1. 드라이버 설정
        scraper.setup_driver()

        # 2. eBay 로그인
        if not scraper.login_to_ebay():
            print("❌ Login failed. Exiting...")
            return

        # 3. Sourcing Insights 페이지로 이동
        if not scraper.navigate_to_sourcing_insights():
            print("❌ Could not access Sourcing Insights. Exiting...")
            return

        # 사용자가 수동으로 페이지를 확인할 수 있도록 대기
        print("\n" + "=" * 70)
        print("⏸️  브라우저에서 Sourcing Insights 페이지를 확인하세요.")
        print("   필요한 경우 카테고리를 선택하거나 필터를 적용하세요.")
        print("   준비되면 Enter 키를 눌러 데이터 추출을 시작합니다...")
        print("=" * 70)
        input()

        # 4. 데이터 추출
        opportunities = scraper.extract_opportunities_data()

        # 5. 데이터 저장
        if opportunities:
            df = scraper.save_data(opportunities, output_format='both')

            print("\n" + "=" * 70)
            print("📊 Data Summary:")
            print(f"   - Total opportunities: {len(opportunities)}")
            if 'category' in df.columns:
                print(f"   - Categories found: {df['category'].nunique()}")
            print("=" * 70)
        else:
            print("\n⚠️ No data extracted. Please check the page manually.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 6. 정리
        print("\n브라우저를 종료하려면 Enter 키를 누르세요...")
        input()
        scraper.close()

if __name__ == "__main__":
    main()

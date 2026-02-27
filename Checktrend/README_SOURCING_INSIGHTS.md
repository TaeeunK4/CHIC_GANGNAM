# eBay Sourcing Insights Top Opportunities 데이터 수집 가이드

## 📋 개요
eBay Seller Hub의 Sourcing Insights에서 Top Opportunities 데이터를 자동으로 수집하는 스크립트입니다.

## 🔧 설치 방법

### 1. 필요한 패키지 설치
```bash
pip install -r requirements_sourcing_insights.txt
```

### 2. Chrome WebDriver 설치
이 스크립트는 Chrome 브라우저를 사용합니다. Chrome이 설치되어 있어야 합니다.

선택 사항으로 `webdriver-manager`를 사용하면 자동으로 드라이버를 다운로드합니다:
```bash
pip install webdriver-manager
```

## 🚀 사용 방법

### 방법 1: 환경변수 사용 (권장)
```bash
# Windows (CMD)
set EBAY_USERNAME=your_ebay_username
set EBAY_PASSWORD=your_password
python 00_ebay_sourcing_insights_scraper.py

# Windows (PowerShell)
$env:EBAY_USERNAME="your_ebay_username"
$env:EBAY_PASSWORD="your_password"
python 00_ebay_sourcing_insights_scraper.py

# Linux/Mac
export EBAY_USERNAME='your_ebay_username'
export EBAY_PASSWORD='your_password'
python 00_ebay_sourcing_insights_scraper.py
```

### 방법 2: 코드에서 직접 수정
`00_ebay_sourcing_insights_scraper.py` 파일을 열고 다음 부분을 수정:

```python
EBAY_USERNAME = os.getenv('EBAY_USERNAME', 'your_actual_username')
EBAY_PASSWORD = os.getenv('EBAY_PASSWORD', 'your_actual_password')
```

## 📊 실행 프로세스

1. **스크립트 실행**: `python 00_ebay_sourcing_insights_scraper.py`
2. **자동 로그인**: eBay에 자동으로 로그인됩니다
3. **페이지 이동**: Sourcing Insights 페이지로 자동 이동
4. **수동 확인**:
   - 브라우저 창이 열리면 원하는 카테고리나 필터를 선택
   - 준비되면 터미널에서 Enter 키를 눌러 데이터 추출 시작
5. **데이터 추출**: Top Opportunities 데이터를 자동으로 추출
6. **파일 저장**:
   - CSV 파일
   - JSON 파일
   - Excel 파일 (openpyxl 설치 시)
   - HTML 페이지 소스 (백업용)
   - 스크린샷 (백업용)

## 📁 출력 파일

### 자동 생성되는 파일들:
- `ebay_sourcing_insights_YYYYMMDD_HHMMSS.csv` - CSV 형식 데이터
- `ebay_sourcing_insights_YYYYMMDD_HHMMSS.json` - JSON 형식 데이터
- `ebay_sourcing_insights_YYYYMMDD_HHMMSS.xlsx` - Excel 형식 데이터
- `ebay_sourcing_insights_page.html` - 원본 HTML (문제 발생 시)
- `ebay_sourcing_insights_screenshot.png` - 페이지 스크린샷 (문제 발생 시)

## 🔍 데이터 필드

수집되는 데이터 (페이지 구조에 따라 다를 수 있음):
- `category`: 카테고리명
- `price_info`: 가격 범위 정보
- `score`: 기회 점수/지표
- `text`: 전체 텍스트 정보
- `html`: HTML 원본 데이터

## ⚠️ 주의사항

1. **eBay 계정 필요**: Seller Hub에 접근 가능한 eBay 판매자 계정이 필요합니다
2. **로그인 보안**:
   - 2단계 인증이 활성화된 경우 수동으로 처리해야 할 수 있습니다
   - 비밀번호는 절대 코드에 직접 저장하지 마세요 (환경변수 사용 권장)
3. **페이지 구조 변경**: eBay가 페이지 구조를 변경하면 스크립트 수정이 필요할 수 있습니다
4. **속도 제한**: 너무 빈번한 요청은 계정 제한을 받을 수 있습니다

## 🐛 트러블슈팅

### Chrome Driver 오류
```bash
# webdriver-manager 사용
pip install webdriver-manager
```

스크립트에서 다음 코드로 변경:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=chrome_options)
```

### 로그인 실패
- 수동으로 로그인 후 쿠키를 저장하는 방법을 사용할 수 있습니다
- 2단계 인증을 임시로 비활성화하거나 앱 전용 비밀번호를 사용하세요

### 데이터 추출 실패
- HTML 파일과 스크린샷이 자동으로 저장됩니다
- 이 파일들을 확인하여 페이지 구조를 분석하고 스크립트를 수정할 수 있습니다

## 📝 추가 커스터마이징

### Headless 모드 (백그라운드 실행)
```python
scraper = eBaySourcerScraper(headless=True)
```

### 특정 카테고리만 추출
코드에서 필터링 로직을 추가할 수 있습니다.

## 💡 팁

1. **첫 실행**: headless=False로 실행하여 프로세스를 확인하세요
2. **페이지 확인**: Enter 키를 누르기 전에 올바른 페이지가 로드되었는지 확인하세요
3. **백업**: HTML과 스크린샷 파일은 추후 분석에 유용합니다

## 📞 지원

문제가 발생하면:
1. HTML 파일과 스크린샷을 확인
2. 콘솔에 출력되는 에러 메시지 확인
3. eBay 페이지 구조가 변경되었는지 확인

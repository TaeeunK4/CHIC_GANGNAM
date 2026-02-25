import pandas as pd
import os

# 현재 스크립트가 있는 디렉토리 경로
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = script_dir

print(f"결과 저장 위치: {output_dir}")

# 파일 경로 설정
input_file = '00_CG_eBay_active_listing_data.csv'
output_file = '01_CG_eBay_active_listing_data_cleaned.csv'

input_path = os.path.join(output_dir, input_file)
output_path = os.path.join(output_dir, output_file)

print(f"\n{'=' * 50}")
print("CSV 파일 처리 중...")
print(f"{'=' * 50}")

# CSV 파일 읽기
print(f"\n1. CSV 파일 읽는 중: {input_path}")
df = pd.read_csv(input_path, encoding='utf-8-sig')
print(f"   총 {len(df):,}개 행")
print(f"   컬럼: {df.columns.tolist()}")

# 'Custom label (SKU)' 컬럼에서 접두사 제거 (콜론 기준)
if 'Custom label (SKU)' in df.columns:
    print(f"\n2. 'Custom label (SKU)' 컬럼에서 접두사 제거 중 (: 기준)...")

    # 처리 전 샘플 확인
    print(f"\n   처리 전 샘플 (처음 10개):")
    print(df[['Item number', 'Custom label (SKU)']].head(10))

    # 문자열로 변환 후 첫 번째 콜론 기준으로 split하여 뒤쪽만 남김
    df['Custom label (SKU)'] = df['Custom label (SKU)'].astype(str).str.split(':', n=1).str[-1]

    # 빈 문자열이나 'nan'을 원래대로 유지 (또는 빈 값으로 처리)
    df['Custom label (SKU)'] = df['Custom label (SKU)'].replace('nan', '')

    print(f"\n   접두사 제거 완료")
    print(f"   처리된 행 수: {len(df):,}")

    # 처리 결과 샘플 확인
    print(f"\n   처리 후 샘플 (처음 10개):")
    print(df[['Item number', 'Custom label (SKU)']].head(10))

    # 콜론이 남아있는지 확인
    remaining_colons = df['Custom label (SKU)'].astype(str).str.contains(':', na=False).sum()
    if remaining_colons > 0:
        print(f"\n   ℹ 참고: 콜론이 포함된 항목이 {remaining_colons}개 있습니다 (값 자체에 콜론 포함).")
    else:
        print(f"\n   ✓ 모든 접두사가 제거되었습니다.")
else:
    print("'Custom label (SKU)' 컬럼을 찾을 수 없습니다.")
    print(f"사용 가능한 컬럼: {df.columns.tolist()}")

# 처리된 데이터를 새 CSV 파일로 저장
print(f"\n3. 처리된 데이터 저장 중...")
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"   ✓ 처리된 데이터 저장 완료: {output_path}")

print(f"\n{'=' * 50}")
print("처리 완료!")
print(f"{'=' * 50}")

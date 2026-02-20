import pandas as pd
import json
import sys
import os
from typing import Dict, Any


def extract_brand_from_spec(spec_str: str) -> Dict[str, str]:

    result = {'brand': ''}
    
    if not spec_str or pd.isna(spec_str):
        return result
    
    try:
        # JSON 문자열을 딕셔너리로 파싱
        spec_dict = json.loads(spec_str)
        
        if isinstance(spec_dict, dict):
            # brand 추출
            if 'brand' in spec_dict:
                brand_value = spec_dict['brand']
                if isinstance(brand_value, str):
                    result['brand'] = brand_value
                elif isinstance(brand_value, list) and len(brand_value) > 0:
                    result['brand'] = str(brand_value[0])
                else:
                    result['brand'] = str(brand_value)
            
            # Brand (대문자) 확인
            if not result['brand'] and 'Brand' in spec_dict:
                brand_value = spec_dict['Brand']
                if isinstance(brand_value, str):
                    result['brand'] = brand_value
                elif isinstance(brand_value, list) and len(brand_value) > 0:
                    result['brand'] = str(brand_value[0])
                else:
                    result['brand'] = str(brand_value)
        
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 빈 문자열 반환
        pass
    except Exception as e:
        # 기타 오류 시 빈 문자열 반환
        pass
    
    return result


def process_csv_file(input_file: str, output_file: str, chunk_size: int = 10000):
    """
    CSV 파일을 청크 단위로 읽어서 brand를 추출하고 새로운 CSV 파일 생성
    
    Args:
        input_file: 입력 CSV 파일 경로
        output_file: 출력 CSV 파일 경로
        chunk_size: 한 번에 처리할 행 수
    """
    print(f"CSV 파일 처리 시작: {input_file}")
    
    # 첫 번째 청크를 읽어서 칼럼 확인
    first_chunk = pd.read_csv(input_file, nrows=5, encoding='utf-8-sig')
    print(f"칼럼: {first_chunk.columns.tolist()}")
    
    # 필요한 칼럼 확인
    required_columns = [
        'Item number', 'origin_id', 'Title', 'eBay category 1 name', 'raw_data']
    missing_columns = [col for col in required_columns if col not in first_chunk.columns]
    if missing_columns:
        print(f"오류: 필요한 칼럼이 없습니다: {missing_columns}")
        return
    
    # 결과를 저장할 리스트
    all_results = []
    
    # 청크 단위로 파일 읽기
    chunk_count = 0
    total_rows = 0
    
    try:
        for chunk in pd.read_csv(input_file, chunksize=chunk_size, encoding='utf-8-sig'):
            chunk_count += 1
            total_rows += len(chunk)
            
            print(f"청크 {chunk_count} 처리 중... (행 수: {len(chunk)}, 누적: {total_rows})")
            
            # brand 추출
            brand_data = chunk['raw_data'].apply(extract_brand_from_spec)
            
            # 새로운 DataFrame 생성
            result_chunk = pd.DataFrame({
                'Item number': chunk['Item number'],
                'origin_id': chunk['origin_id'],
                'Title': chunk['Title'],
                'eBay category 1 name': chunk['eBay category 1 name'],
                'raw_data': chunk['raw_data'],
                'brand': [x['brand'] for x in brand_data]
            })
            
            all_results.append(result_chunk)
            
            # 진행 상황 출력
            if chunk_count % 10 == 0:
                print(f"  진행: {total_rows}개 행 처리 완료")
        
        # 모든 청크 합치기
        print("\n모든 청크를 합치는 중...")
        final_df = pd.concat(all_results, ignore_index=True)
        
        print(f"\n총 {len(final_df)}개의 행이 처리되었습니다.")
        print(f"칼럼: {final_df.columns.tolist()}")
        print(f"\n샘플 데이터:")
        print(final_df.head())
        
        # 결과 저장
        print(f"\n결과를 '{output_file}'에 저장 중...")
        final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"저장 완료!")
        
        # 통계 정보
        print(f"\n=== 통계 ===")
        print(f"brand가 있는 행: {final_df['brand'].notna().sum()}개 ({final_df['brand'].notna().sum() / len(final_df) * 100:.1f}%)")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = '02_CG_eBay_active_listing_data_filtered.csv'
    output_file = '03_CG_eBay_active_listing_data_filtered_with_brand.csv'

    input_path = os.path.join(script_dir, input_file)
    output_path = os.path.join(script_dir, output_file)
    
    process_csv_file(input_path, output_path, chunk_size=10000)
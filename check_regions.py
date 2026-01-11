import asyncio
import httpx
import json

# 최신 행정동 데이터 소스
GEOJSON_URL = "https://raw.githubusercontent.com/vuski/admdongkor/master/ver20250101/HangJeongDong_ver20250101.geojson"

async def fetch_and_print_regions():
    print(f"--- 데이터 소스로부터 지역 정보를 불러오는 중 ---")
    print(f"URL: {GEOJSON_URL}\n")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(GEOJSON_URL)
            response.raise_for_status()
            geojson_data = response.json()
    except Exception as e:
        print(f"데이터 로드 실패: {e}")
        return

    features = geojson_data.get('features', [])
    print(f"총 {len(features)}개의 지역 데이터를 발견했습니다.\n")
    print(f"{'번호':<5} | {'시도':<10} | {'시군구':<12} | {'읍면동'}")
    print("-" * 50)

    for i, feature in enumerate(features, 1):
        props = feature.get('properties', {})
        
        sido = props.get('sidonm', 'N/A')
        sigugun = props.get('sggnm', 'N/A')
        full_name = props.get('adm_nm', '')
        
        # 읍면동 추출 (전체 이름의 마지막 단어)
        parts = full_name.split()
        dong = parts[-1] if parts else 'N/A'

        # 세종시 등 시군구가 없는 경우 처리
        if not sigugun or sigugun == 'None':
            sigugun = "-(세종시 등)"

        # 상위 30개만 출력하고 나머지는 생략 (너무 많으므로)
        if i <= 30:
            print(f"{i:<5} | {sido:<10} | {sigugun:<12} | {dong}")
        elif i == 31:
            print(f"... 내역이 너무 많아 생략합니다 (총 {len(features)}개) ...")
            break

    # 전체 통계 간단히 출력
    print("-" * 50)
    print(f"조회 완료: 총 {len(features)}개의 행정동 정보가 확인되었습니다.")

if __name__ == "__main__":
    asyncio.run(fetch_and_print_regions())
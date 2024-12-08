import streamlit as st
import requests
from dotenv import load_dotenv
import os
import pandas as pd

# 환경 변수 로드
load_dotenv()

# 환경 변수 확인 (디버깅 용도)
GEO_CLIENT_ID = os.getenv("GEO_CLIENT_ID")  # Geocoding API Client ID
GEO_CLIENT_SECRET = os.getenv("GEO_CLIENT_SECRET")  # Geocoding API Client Secret
PLACE_CLIENT_ID = os.getenv("PLACE_CLIENT_ID")  # Place Search API Client ID
PLACE_CLIENT_SECRET = os.getenv("PLACE_CLIENT_SECRET")  # Place Search API Client Secret

# 환경 변수 값 확인 (디버깅 용도)
st.write(f"GEO_CLIENT_ID: {GEO_CLIENT_ID}")
st.write(f"GEO_CLIENT_SECRET: {GEO_CLIENT_SECRET}")
st.write(f"PLACE_CLIENT_ID: {PLACE_CLIENT_ID}")
st.write(f"PLACE_CLIENT_SECRET: {PLACE_CLIENT_SECRET}")

# Geocoding API (주소 → 좌표 변환)
def get_coordinates(address):
    """주소를 받아 좌표(x, y)를 반환"""
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": GEO_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": GEO_CLIENT_SECRET
    }
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        coords = response.json()['addresses'][0]
        return float(coords['x']), float(coords['y'])
    else:
        raise Exception("Geocoding API Error: " + response.text)

# Place Search API (맛집 검색)
def search_nearby_places(query, x, y):
    """검색어와 좌표를 기반으로 맛집 정보를 반환"""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": PLACE_CLIENT_ID,
        "X-Naver-Client-Secret": PLACE_CLIENT_SECRET
    }
    params = {
        "query": query,
        "x": x,  # 경도
        "y": y,  # 위도
        "sort": "random",  # 정렬 방식
        "display": 5       # 결과 개수
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        raise Exception("Place Search API Error: " + response.text)

# Streamlit 앱
def recommend_restaurants():
    st.header("🍴 맛집 추천")
    
    # 주소 입력
    address = st.text_input("주소를 입력하세요", "서울 강남구")
    
    # 추천 버튼
    if st.button("추천받기"):
        try:
            # 1. Geocoding API로 좌표 가져오기
            x, y = get_coordinates(address)
            st.success(f"좌표를 찾았습니다: 경도={x}, 위도={y}")
            
            # 2. Place Search API로 맛집 검색
            places = search_nearby_places("맛집", x, y)
            st.subheader("추천 맛집 목록")
            
            # 3. 결과 출력
            for place in places:
                st.write(f"**{place['title']}** - {place['address']} ([상세보기]({place['link']}))")
            
            # 4. 결과 CSV 저장
            places_df = pd.DataFrame(places)
            places_df.to_csv('recommended_places.csv', index=False)
            st.success("추천 결과가 저장되었습니다: recommended_places.csv")
        
        except Exception as e:
            st.error(f"에러 발생: {e}")

# Main 실행
def main():
    st.sidebar.title("🍴 메뉴")
    menu = st.sidebar.radio("탭 선택", ["맛집 추천"])
    
    if menu == "맛집 추천":
        # session_state를 사용하여 상태를 초기화합니다
        if "places" in st.session_state:
            del st.session_state["places"]  # 이전 결과를 삭제하여 초기화
        
        recommend_restaurants()

if __name__ == '__main__':
    main()

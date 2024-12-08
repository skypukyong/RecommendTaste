import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()
GEO_CLIENT_ID = os.getenv("GEO_CLIENT_ID")  # Geocoding API Client ID
GEO_CLIENT_SECRET = os.getenv("GEO_CLIENT_SECRET")  # Geocoding API Client Secret
PLACE_CLIENT_ID = os.getenv("PLACE_CLIENT_ID")  # Place Search API Client ID
PLACE_CLIENT_SECRET = os.getenv("PLACE_CLIENT_SECRET")  # Place Search API Client Secret

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

# 맛 프로필 설문
def taste_preference_survey():
    """사용자 맛 프로필 설문"""
    st.header('🍽️ 맛 프로필 만들기기')
    
    spicy_level = st.slider(
        '얼마나 매운 음식을 좋아하시나요?', 
        min_value=0, 
        max_value=10, 
        value=5,
        help='0은 전혀 매운 음식을 못 먹음, 10은 아주 매운 음식도 OK'
    )
    
    cuisine_options = st.multiselect(
        '좋아하는 요리 스타일을 선택해주세요',
        ['한식', '중식', '일식', '양식', '동남아 음식', '인도 음식'],
        help='여러 개 선택 가능'
    )
    
    spice_intensity = st.radio(
        '향신료 강도 선호도',
        ['약한 향신료', '중간 강도', '강한 향신료'],
        help='음식의 향신료 강도를 선택해주세요'
    )
    
    diet_preference = st.radio(
        '식단 유형',
        ['육식', '채식', '비건'],
        help='주로 선호하는 식단 유형'
    )
    
    disliked_foods = st.text_area(
        '피하고 싶은 음식이나 알레르기 음식을 적어주세요',
        help='예: 새우, 견과류, 우유 등'
    )
    
    additional_preferences = st.text_area(
        '추가로 알려주고 싶은 음식 취향이 있나요?',
        help='예: 건강식, 다이어트 음식, 특정 요리 스타일 등'
    )
    
    # Save preferences to session state
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {}
        
    st.session_state.preferences.update({
        'spicy_level': spicy_level,
        'cuisine_preferences': cuisine_options,
        'spice_intensity': spice_intensity,
        'diet_preference': diet_preference,
        'disliked_foods': disliked_foods,
        'additional_preferences': additional_preferences
    })
    st.success("맛 프로필이 저장되었습니다!")

# 맛집 추천
def recommend_restaurants():
    st.header("🍴 맛집 추천")
    
    # 주소 입력
    address = st.text_input("주소를 입력하세요", "서울 강남구")
    
    # 사용자 맛 프로필 확인
    if 'preferences' in st.session_state:
        st.subheader("사용자 맛 프로필")
        st.json(st.session_state.preferences)
    
    # 추천 버튼
    if st.button("추천받기"):
        try:
            # 1. Geocoding API로 좌표 가져오기
            x, y = get_coordinates(address)
            st.success(f"좌표를 찾았습니다: 경도={x}, 위도={y}")
            
            # 2. Place Search API로 맛집 검색
            query = "맛집"
            if 'preferences' in st.session_state:
                query += " " + " ".join(st.session_state.preferences['cuisine_preferences'])
            places = search_nearby_places(query, x, y)
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
    menu = st.sidebar.radio("탭 선택", ["맛 프로필 입력", "맛집 추천"])
    
    if menu == "맛 프로필 입력":
        taste_preference_survey()
    elif menu == "맛집 추천":
        recommend_restaurants()

if __name__ == '__main__':
    main()

import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# API 키가 제대로 로드되었는지 확인 (디버깅용)
st.write(CLIENT_ID, CLIENT_SECRET)

# Helper functions
def get_coordinates(address, client_id, client_secret):
    """주어진 주소에 대한 좌표(위도, 경도)를 가져옵니다."""
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,  # 환경 변수로 읽은 CLIENT_ID 사용
        "X-NCP-APIGW-API-KEY": client_secret  # 환경 변수로 읽은 CLIENT_SECRET 사용
    }
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        coords = response.json()['addresses'][0]
        return float(coords['x']), float(coords['y'])
    else:
        raise Exception("Geocoding API 오류: " + response.text)

def search_nearby_places(query, x, y, client_id, client_secret):
    """네이버의 장소 검색 API를 사용하여 주변 장소를 검색합니다."""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": client_id,  # 환경 변수로 읽은 CLIENT_ID 사용
        "X-Naver-Client-Secret": client_secret  # 환경 변수로 읽은 CLIENT_SECRET 사용
    }
    params = {
        "query": query,
        "x": x,
        "y": y,
        "sort": "random",
        "display": 5
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['items']
    else:
        raise Exception("Place Search API 오류: " + response.text)

# Streamlit 앱 함수들
def taste_preference_survey():
    """사용자 맛 프로필 설문"""
    st.header('🍽️ 맛 프로필 설문')
    
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
    
    # 사용자 취향을 세션 상태에 저장
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

def recommend_restaurants():
    """사용자의 위치와 취향을 기반으로 맛집 추천"""
    st.header("🍴 맛집 추천")
    
    # 주소 입력
    address = st.text_input("주소를 입력하세요", "서울 강남구")
    
    # 사용자 맛 프로필 표시
    if 'preferences' in st.session_state:
        st.subheader("사용자 맛 프로필")
        st.json(st.session_state.preferences)
    
    # 맛집 추천 버튼
    if st.button("추천받기"):
        try:
            # 주소로 좌표 가져오기
            x, y = get_coordinates(address, CLIENT_ID, CLIENT_SECRET)
            
            # 맛집 검색
            places = search_nearby_places("맛집", x, y, CLIENT_ID, CLIENT_SECRET)
            
            # 결과 표시
            st.subheader("추천 맛집 목록")
            for place in places:
                st.write(f"**{place['title']}** - {place['address']} ([상세보기]({place['link']}))")
            
            # 결과를 CSV로 저장
            places_df = pd.DataFrame(places)
            places_df.to_csv('recommended_places.csv', index=False)
            st.success("추천 결과가 저장되었습니다: recommended_places.csv")
        
        except Exception as e:
            st.error(f"에러 발생: {e}")

# 메인 앱 함수
def main():
    st.sidebar.title("🍴 메뉴")
    menu = st.sidebar.radio("탭 선택", ["맛 프로필 입력", "맛집 추천"])
    
    if menu == "맛 프로필 입력":
        taste_preference_survey()
    elif menu == "맛집 추천":
        recommend_restaurants()

if __name__ == '__main__':
    main()

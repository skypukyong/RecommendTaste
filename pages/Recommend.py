import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
st.caching.clear_cache()
# Helper functions
def get_coordinates(address, client_id, client_secret):
    """Get coordinates (latitude and longitude) for a given address."""
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        coords = response.json()['addresses'][0]
        return float(coords['x']), float(coords['y'])
    else:
        raise Exception("Geocoding API Error: " + response.text)

def search_nearby_places(query, x, y, client_id, client_secret):
    """Search for nearby places using Naver's Place Search API."""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
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
        raise Exception("Place Search API Error: " + response.text)

# Streamlit app functions
def taste_preference_survey():
    """User taste profile survey."""
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

def recommend_restaurants():
    """Recommend restaurants based on user location and preferences."""
    st.header("🍴 맛집 추천")
    
    # Input address
    address = st.text_input("주소를 입력하세요", "서울 강남구")
    
    # Show user preferences if available
    if 'preferences' in st.session_state:
        st.subheader("사용자 맛 프로필")
        st.json(st.session_state.preferences)
    
    # Recommend restaurants
    if st.button("추천받기"):
        try:
            # Get coordinates from address
            x, y = get_coordinates(address, CLIENT_ID, CLIENT_SECRET)
            
            # Search for places
            places = search_nearby_places("맛집", x, y, CLIENT_ID, CLIENT_SECRET)
            
            # Display results
            st.subheader("추천 맛집 목록")
            for place in places:
                st.write(f"**{place['title']}** - {place['address']} ([상세보기]({place['link']}))")
            
            # Save to CSV
            places_df = pd.DataFrame(places)
            places_df.to_csv('recommended_places.csv', index=False)
            st.success("추천 결과가 저장되었습니다: recommended_places.csv")
        
        except Exception as e:
            st.error(f"에러 발생: {e}")

# Main app
def main():
    st.sidebar.title("🍴 메뉴")
    menu = st.sidebar.radio("탭 선택", ["맛 프로필 입력", "맛집 추천"])
    
    if menu == "맛 프로필 입력":
        taste_preference_survey()
    elif menu == "맛집 추천":
        recommend_restaurants()

if __name__ == '__main__':
    main() 

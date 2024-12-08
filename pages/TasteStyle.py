import streamlit as st
import requests
from dotenv import load_dotenv
import os
import re

# 환경 변수 로드
load_dotenv()
PLACE_CLIENT_ID = os.getenv("PLACE_CLIENT_ID")  # Place Search API Client ID
PLACE_CLIENT_SECRET = os.getenv("PLACE_CLIENT_SECRET")  # Place Search API Client Secret
api_key = os.getenv("api")

if api_key:
    st.session_state['api_key'] = api_key
    if 'openai_client' in st.session_state:
        client = st.session_state['openai_client']
    else:
        client = OpenAI(api_key=api_key)
        st.session_state['openai_client'] = client

# HTML 태그 제거 함수
def clean_html(text):
    """HTML 태그를 제거하는 함수"""
    return re.sub(r'<.*?>', '', text)  # <b>와 같은 HTML 태그를 제거

# Place Search API (맛집 검색)
def search_nearby_places(query):
    """검색어와 좌표를 기반으로 맛집 정보를 반환"""
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": PLACE_CLIENT_ID,
        "X-Naver-Client-Secret": PLACE_CLIENT_SECRET
    }
    params = {
        "query": query,  # 검색어 (예: "맛집")
        "sort": "random",  # 정렬 방식
        "display": 7,  # 결과 개수
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        raise Exception("Place Search API 오류: " + response.text)

# 맛 프로필 생성하기
def taste_preference_survey():
    st.title('🍽️맛 프로필 만들기')
    
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {}

    st.header('맛 프로필 제목')
    profile_title = st.text_input('맛 프로필 제목을 입력해주세요', '나의 맛 프로필')  # 기본값으로 '나의 맛 프로필' 제공

    if 'profile_list' not in st.session_state:
        st.session_state.profile_list = []  # 프로필 목록 초기화

    st.header('매운맛 선호도')
    spicy_level = st.slider(
        '얼마나 매운 음식을 좋아하시나요?', 
        min_value=0, 
        max_value=10, 
        value=5,
        help='0은 전혀 매운 음식을 못 먹음, 10은 아주 매운 음식도 OK'
    )
    st.session_state.preferences['spicy_level'] = spicy_level

    st.header('요리 스타일 선호도')
    cuisine_option = st.selectbox(
        '좋아하는 요리 스타일을 선택해주세요',
        ['한식', '중식', '일식', '양식', '동남아 음식', '인도 음식'],
        help='하나만 선택 가능'
    )
    st.session_state.preferences['cuisine_preferences'] = cuisine_option

    if st.button('맛 프로필 완성하기'):
        # 스피너 표시
        with st.spinner('맛 프로필을 생성하는 중...'):
            # 생성 작업을 수행한 후, 프로필 저장
            preference_str = generate_preference_string(profile_title)
            st.session_state.profile_list.append({'title': profile_title, 'preferences': preference_str})
            st.success(f'맛 프로필이 성공적으로 저장되었습니다! 🎉')

def generate_preference_string(profile_title):
    preferences = st.session_state.preferences
    
    # 매운맛 선호도 변환
    if preferences['spicy_level'] <= 3:
        spicy_description = "맵지 않은"
    elif preferences['spicy_level'] >= 7:
        spicy_description = "매운"
    else:
        spicy_description = "적당한 매운맛"
    
    # 각 항목을 문자열로 변환하여 하나의 문자열로 합침
    preference_str = f"{spicy_description} {preferences['cuisine_preferences']}"
    
    return f"{profile_title}: {preference_str}"

# 맛집 추천
def recommend_restaurants():
    st.title('🍽️ 맛집 추천')

    if 'profile_list' not in st.session_state or len(st.session_state.profile_list) == 0:
        st.warning('먼저 맛 프로필을 생성해주세요!')
        return

    # 맛 프로필 선택
    profile_titles = [profile['title'] for profile in st.session_state.profile_list]
    selected_profile_title = st.selectbox('추천할 맛 프로필을 선택하세요', profile_titles)

    selected_profile = next(profile for profile in st.session_state.profile_list if profile['title'] == selected_profile_title)
    
    st.write(f"선택된 맛 프로필: {selected_profile['preferences']}")
    
    # 맛집 추천
    query = selected_profile['preferences']
    try:
        places = search_nearby_places(query)
        st.write(f"추천 맛집 목록 (검색어: {query}):")
        for place in places:
            st.write(f"- {place['title']} (주소: {place['address']}, 전화: {place['telephone']})")
    except Exception as e:
        st.error(f"맛집 검색 중 오류 발생: {e}")

# Main 실행
def main():
    st.sidebar.title("🍴 메뉴")
    menu = st.sidebar.radio("탭 선택", ["맛 프로필", "맛집 추천"])

    if menu == "맛 프로필":
        taste_preference_survey()
    
    if menu == "맛집 추천":
        recommend_restaurants()

if __name__ == '__main__':
    main()

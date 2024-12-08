import streamlit as st
import requests
from dotenv import load_dotenv
import os
import pandas as pd
import re

# 환경 변수 로드
load_dotenv()
PLACE_CLIENT_ID = os.getenv("PLACE_CLIENT_ID")  # Place Search API Client ID
PLACE_CLIENT_SECRET = os.getenv("PLACE_CLIENT_SECRET")  # Place Search API Client Secret

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

# Streamlit 앱
def recommend_restaurants():
    st.header("🍴 맛집 추천")
    
    # 주소 입력
    address = st.text_input("주소를 입력하세요")
    
    # 추천 버튼
    if st.button("추천받기"):
        try:
            # 2. Place Search API로 맛집 검색
            places = search_nearby_places(address)
            st.subheader("추천 맛집 목록")
            
            # 3. 결과 출력
            for place in places:
                # HTML 태그 제거
                cleaned_title = clean_html(place['title'])
                cleaned_address = clean_html(place['address'])
                st.write(f"**{cleaned_title}** - {cleaned_address} ([상세보기]({place['link']}))")
            
            # 4. 결과 CSV 저장
            places_df = pd.DataFrame(places)
            places_df['title'] = places_df['title'].apply(clean_html)
            places_df['address'] = places_df['address'].apply(clean_html)
            csv_file = places_df.to_csv(index=False)
            st.download_button("CSV 다운로드", csv_file, file_name="recommended_places.csv", mime="text/csv")
            
            # 5. 결과 리스트로 출력
            st.subheader("추천된 맛집 정보")
            st.write(places_df)  # DataFrame을 리스트 형태로 출력
            
        except Exception as e:
            st.error(f"오류 발생: {e}")

# Main 실행
def main():
    st.sidebar.title("🍴 메뉴")
    menu = st.sidebar.radio("탭 선택", ["맛집 추천"])
    
    if menu == "맛집 추천":
        recommend_restaurants()

if __name__ == '__main__':
    main()

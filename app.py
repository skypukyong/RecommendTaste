import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# 네이버 지도 API 키
NAVER_CLIENT_ID = "YOUR_CLIENT_ID"
NAVER_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# 네이버 지도 API - Geocoding (주소 → 좌표 변환)
def geocode(address):
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET,
    }
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["addresses"]:
            lat = float(data["addresses"][0]["y"])
            lng = float(data["addresses"][0]["x"])
            return lat, lng
    return None

# 네이버 지도 API - Place Search (맛집 검색)
def search_places(query, coordinate, radius):
    url = "https://naveropenapi.apigw.ntruss.com/map-place/v1/search"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
        "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET,
    }
    params = {
        "query": query,
        "coordinate": f"{coordinate[1]},{coordinate[0]}",
        "radius": radius,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("places", [])
    return []

# Streamlit 앱 시작
st.title("맛집 추천 챗봇")
st.markdown("네이버 지도 API를 활용한 맛집 추천 챗봇입니다.")

# 사용자 입력
address = st.text_input("검색할 지역 (예: 부산 해운대)")
preference = st.selectbox("원하는 맛은 무엇인가요?", ["매운맛", "달콤한맛", "고소한맛"])
radius = st.slider("검색 반경 (m)", 100, 5000, step=100)

if st.button("검색하기"):
    if address:
        # 주소 → 좌표 변환
        coordinate = geocode(address)
        if coordinate:
            st.write(f"입력된 주소의 좌표: {coordinate}")
            
            # 맛집 검색
            query = f"{preference} 맛집"
            places = search_places(query, coordinate, radius)
            
            if places:
                st.write("추천 맛집 리스트:")
                # 지도 생성
                m = folium.Map(location=[coordinate[0], coordinate[1]], zoom_start=14)
                for place in places:
                    st.write(f"- **{place['name']}** ({place['category']})")
                    st.write(f"  위치: {place['address']} / 평점: {place.get('rating', 'N/A')}")
                    
                    # 지도에 마커 추가
                    folium.Marker(
                        location=[float(place["y"]), float(place["x"])],
                        popup=f"{place['name']} ({place['category']})",
                        tooltip=place["name"]
                    ).add_to(m)
                
                # 지도 출력
                st_folium(m, width=700, height=500)
            else:
                st.write("검색 결과가 없습니다.")
        else:
            st.error("주소를 좌표로 변환할 수 없습니다.")
    else:
        st.error("검색할 지역을 입력해주세요.")

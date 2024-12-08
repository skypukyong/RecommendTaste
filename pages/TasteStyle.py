import streamlit as st
import requests
from dotenv import load_dotenv
import os
import re
from openai import OpenAI

# 환경 변수 로드
load_dotenv()
api_key = os.getenv("api")

if api_key:
    st.session_state['api_key'] = api_key
    if 'openai_client' in st.session_state:
        client = st.session_state['openai_client']
    else:
        client = OpenAI(api_key=api_key)
        st.session_state['openai_client'] = client

@st.cache_data
def ask_gpt(messages):
    client = st.session_state['openai_client']
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 적절한 모델 이름으로 변경하세요
        messages=messages
    )
    return response.choices[0].message.content




st.header("Ask GPT")

# 대화 내역을 session_state에 저장
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Clear 버튼 기능: 대화 스레드를 초기화
if st.button('Clear'):
    st.session_state['messages'] = []  # 대화 내역 초기화
    st.experimental_rerun()  # 페이지 새로고침

# 대화창 나가기 버튼 기능: 대화 스레드 및 Assistant 삭제
if st.button('대화창 나가기'):
    st.session_state['messages'] = []  # 대화 내역 초기화
    st.session_state['openai_client'] = None  # OpenAI 클라이언트 정보 삭제
    st.experimental_rerun()  # 페이지 새로고침

# 사용자 입력 받기
prompt = st.chat_input("질문을 입력하세요.")
st.session_state.prompt = prompt

answer = ''
if prompt:
    # 사용자 메시지를 대화 내역에 추가
    st.session_state['messages'].append({"role": "user", "content": prompt})
    
    # 이전 대화와 함께 GPT 모델에 요청
    answer = ask_gpt(st.session_state['messages'])

    # AI의 응답을 대화 내역에 추가
    st.session_state['messages'].append({"role": "assistant", "content": answer})

# 전체 대화 내역을 출력
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.write(message['content'])

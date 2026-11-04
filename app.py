
import streamlit as st
from openai import OpenAI

# OpenAI 클라이언트 생성
client = OpenAI()

# 페이지 설정
st.set_page_config(
    page_title="음성 AI 서비스",
    page_icon="🤖",
    layout="wide"
)

# 화면 구성
left, right = st.columns([1, 5])

# 왼쪽 영역
with left:
    st.write("왼쪽")

# 오른쪽 영역
with right:
    st.write("오른쪽")

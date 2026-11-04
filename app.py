
import streamlit as st
from openai import OpenAI

# OpenAI 클라이언트
client = OpenAI()

# 페이지 설정
st.set_page_config(
    page_title="ABLE AI 개인비서",
    page_icon="🤖",
    layout="wide"
)

# -------------------------
# CSS 디자인
# -------------------------

st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background-color: #F3F6FC;
}

/* 왼쪽 사이드바 */
[data-testid="stSidebar"] {
    background-color: #172B50;
}

/* 사이드바 글자 */
[data-testid="stSidebar"] * {
    color: white;
}

/* 사이드바 버튼 */
[data-testid="stSidebar"] button {
    border-radius: 8px;
}

/* 메인 화면 위쪽 여백 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* 메인 화면 제목 */
h1, h2, h3 {
    color: #1C2F4E;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# 1. 메뉴 선택 상태 초기화
# -------------------------

if "menu" not in st.session_state:
    st.session_state.menu = "홈"


# 메뉴 변경 함수
def select_menu(name):
    st.session_state.menu = name


# -------------------------
# 2. 왼쪽 사이드바
# -------------------------

with st.sidebar:

    st.markdown("# 🅰 ABLE")
    st.caption("AI PERSONAL ASSISTANT")

    st.divider()

    st.caption("WORKSPACE")

    # 홈
    if st.button("🏠  홈", use_container_width=True):
        select_menu("홈")

    # 일정
    if st.button("📅  일정", use_container_width=True):
        select_menu("일정")

    # 회의
    st.markdown("**📝  회의**")

    if st.button("　회의 관리", use_container_width=True):
        select_menu("회의 관리")

    if st.button("　회의록 요약", use_container_width=True):
        select_menu("회의록 요약")

    # 자료
    st.markdown("**📁  자료**")

    if st.button("　자료 조사", use_container_width=True):
        select_menu("자료 조사")

    if st.button("　자료 요약", use_container_width=True):
        select_menu("자료 요약")

    if st.button("　자료 번역", use_container_width=True):
        select_menu("자료 번역")

    if st.button("　자료 교정", use_container_width=True):
        select_menu("자료 교정")

    # 이메일
    st.markdown("**✉️  이메일**")

    if st.button("　이메일 작성", use_container_width=True):
        select_menu("이메일 작성")

    if st.button("　이메일 관리", use_container_width=True):
        select_menu("이메일 관리")

    # 음성 비서
    st.markdown("**🎙  음성 비서**")

    if st.button("　음성 명령", use_container_width=True):
        select_menu("음성 명령")

    if st.button("　실시간 음성 대화", use_container_width=True):
        select_menu("실시간 음성 대화")

    # AI에게 질문
    st.markdown("**💬  AI에게 질문**")

    if st.button("　새로운 대화", use_container_width=True):
        select_menu("새로운 대화")

    if st.button("　최근 대화", use_container_width=True):
        select_menu("최근 대화")

    st.divider()

    st.caption("AI PERSONAL ASSISTANT")
    st.markdown("**김 대리의 업무 도우미**")
    st.caption("에이블과 함께 업무를 효율적으로 관리하세요.")


# -------------------------
# 3. 오른쪽 메인 화면
# -------------------------

menu = st.session_state.menu

# 상단 영역
col1, col2 = st.columns([7, 3])

with col1:
    st.caption("WORKSPACE  ·  " + menu)

with col2:
    st.markdown(
        "<p style='text-align:right; color:#65748C;'>김 대리 👤</p>",
        unsafe_allow_html=True
    )

st.divider()

# 선택한 메뉴 제목
st.title(menu)

# 메뉴별 화면
if menu == "홈":

    st.write("안녕하세요, 김 대리님! 👋")
    st.write("에이블과 함께 오늘의 업무를 관리하세요.")

    st.info("왼쪽 메뉴에서 원하는 기능을 선택해 주세요.")


elif menu == "일정":

    st.write("업무 및 회의 일정을 관리하는 화면입니다.")


elif menu == "회의 관리":

    st.write("회의 일정과 관련 정보를 관리하는 화면입니다.")


elif menu == "회의록 요약":

    st.write("회의록을 업로드하고 AI 요약 결과를 확인하는 화면입니다.")


elif menu == "자료 조사":

    st.write("업무에 필요한 자료를 조사하는 화면입니다.")


elif menu == "자료 요약":

    st.write("문서 파일을 업로드하고 핵심 내용을 요약하는 화면입니다.")


elif menu == "자료 번역":

    st.write("문서 및 텍스트를 번역하는 화면입니다.")


elif menu == "자료 교정":

    st.write("문서의 맞춤법과 문장 표현을 교정하는 화면입니다.")


elif menu == "이메일 작성":

    st.write("업무 이메일을 작성하는 화면입니다.")


elif menu == "이메일 관리":

    st.write("이메일 내용을 관리하는 화면입니다.")


elif menu == "음성 명령":

    st.write("음성으로 업무를 요청하는 화면입니다.")


elif menu == "실시간 음성 대화":

    st.write("에이블과 실시간으로 음성 대화를 나누는 화면입니다.")


elif menu == "새로운 대화":

    st.write("에이블에게 자유롭게 질문하는 화면입니다.")


elif menu == "최근 대화":

    st.write("이전 대화 기록을 확인하는 화면입니다.")

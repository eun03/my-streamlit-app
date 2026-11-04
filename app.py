
import os, base64, json, requests
import streamlit as st
from openai import OpenAI

# OpenAI 클라이언트 생성
client = OpenAI()

# 페이지 설정
st.set_page_config(
    page_title="ABLE - AI Personal Assistant",
    page_icon="🤖",
    layout="wide"
)

# 디자인 설정
st.markdown("""
<style>

/* 전체 메인 배경 */
[data-testid="stAppViewContainer"] {
    background-color: #F3F6FD;
}

/* 왼쪽 사이드바 */
[data-testid="stSidebar"] {
    background-color: #192D52;
}

/* 사이드바 글씨 */
[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

/* 사이드바 여백 */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 30px;
}

/* 메인 화면 여백 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* 상단 영역 */
[data-testid="stHeader"] {
    background-color: transparent;
}

/* 입력 폼 */
[data-testid="stForm"] {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #E5EAF3;
}

/* 버튼 */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    border-radius: 8px;
    border: 1px solid #DCE3F0;
    background-color: white;
    color: #192D52;
}

/* 버튼에 마우스를 올렸을 때 */
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #EEF1FF;
    color: #4D5BD4;
    border-color: #AAB5FF;
}

</style>
""", unsafe_allow_html=True)


# 왼쪽 사이드바
with st.sidebar:

    st.title("ABLE")

    st.caption("AI PERSONAL ASSISTANT")

    st.divider()

    st.subheader("메뉴")

    st.write("🏠  홈")
    st.write("📅  일정")
    st.write("📋  회의")
    st.write("✉️  이메일")
    st.write("🎙️  음성 비서")


# 오른쪽 메인 화면
st.title("메인 화면")


# 역할 지정
sys_role = """
당신은 다양한 업무를 처리하는 AI 서비스입니다.
개인 비서처럼 친절하게 응대합니다.
"""


# 대화 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []


# 지시 영역
with st.form("task_form"):

    uploaded_file = st.file_uploader(
        "텍스트 파일 업로드",
        type=["txt"]
    )

    audio_value = st.audio_input("무엇을 도와드릴까요?")

    submit = st.form_submit_button("실행")


# 버튼을 눌렀을 때만 실행
if submit:

    # 업로드된 파일이 있으면 디코딩
    text = ""

    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")

    # 녹음이 없으면 녹음 요청
    if audio_value is None:
        st.warning("음성을 녹음해주세요.")
        st.stop()

    # 시스템 메시지
    system_content = sys_role

    if text:
        system_content += f"\n\n다음 내용을 참고하세요:\n{text}"

    input_messages = [
        {"role": "system", "content": system_content}
    ]

    # STT: 음성 → 텍스트
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.wav", audio_value, "audio/wav")
    )

    # 사용자 메시지
    input_messages.append({
        "role": "user",
        "content": transcript.text
    })

    # LLM 호출 및 응답 듣기
    with st.spinner("답변을 준비하고 있습니다..."):

        # LLM 호출
        response = client.responses.create(
            model="gpt-4o-mini",
            input=input_messages
        )

        answer = response.output_text

        # 응답 출력
        st.subheader("AI 답변")
        st.write(answer)


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
[data-testid="stAppViewContainer"] {
    background-color: #F3F6FD;
}

[data-testid="stSidebar"] {
    background-color: #192D52;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 30px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stHeader"] {
    background-color: transparent;
}

.stButton > button {
    border-radius: 8px;
    border: 1px solid #DCE3F0;
    background-color: white;
    color: #192D52;
}

.stButton > button:hover {
    background-color: #EEF1FF;
    color: #4D5BD4;
    border-color: #AAB5FF;
}
</style>
""", unsafe_allow_html=True)


# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_chat_id" not in st.session_state:
    st.session_state.selected_chat_id = None

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0


# 왼쪽 사이드바
with st.sidebar:

    st.title("ABLE")
    st.caption("AI PERSONAL ASSISTANT")

    st.divider()

    st.subheader("메뉴")

    menu = st.radio(
        "메뉴 선택",
        ["🏠 홈", "📅 일정", "📋 회의", "✉️ 이메일",
         "🎙️ 음성 비서", "💬 AI 챗봇"],
        label_visibility="collapsed"
    )


# 홈 화면
if menu == "🏠 홈":

    st.title("메인 화면")


# 일정 화면
elif menu == "📅 일정":

    st.title("일정")
    st.write("일정 관리 페이지입니다.")


# 회의 화면
elif menu == "📋 회의":

    st.title("회의")
    st.write("회의 관리 페이지입니다.")


# 이메일 화면
elif menu == "✉️ 이메일":

    st.title("이메일")
    st.write("이메일 관리 페이지입니다.")


# 음성 비서 화면
elif menu == "🎙️ 음성 비서":

    st.title("음성 비서")

    sys_role = """
    당신은 다양한 업무를 처리하는 AI 서비스입니다.
    개인 비서처럼 친절하게 응대합니다.
    """

    with st.form("task_form"):

        uploaded_file = st.file_uploader(
            "텍스트 파일 업로드",
            type=["txt"]
        )

        audio_value = st.audio_input("무엇을 도와드릴까요?")

        submit = st.form_submit_button("실행")

    if submit:

        text = ""

        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8")

        if audio_value is None:
            st.warning("음성을 녹음해주세요.")
            st.stop()

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

        input_messages.append({
            "role": "user",
            "content": transcript.text
        })

        with st.spinner("답변을 준비하고 있습니다..."):

            response = client.responses.create(
                model="gpt-4o-mini",
                input=input_messages
            )

            answer = response.output_text

            st.subheader("AI 답변")
            st.write(answer)


# AI 챗봇 화면
elif menu == "💬 AI 챗봇":

    st.title("AI 챗봇")
    st.caption("에이블과 자유롭게 대화를 나눠보세요.")

    # 새로운 대화 버튼
    if st.button("＋ 새로운 대화"):

        st.session_state.selected_chat_id = None
        st.rerun()

    st.divider()

    # 현재 선택된 대화 찾기
    selected_chat = None

    if st.session_state.selected_chat_id is not None:

        for chat in st.session_state.chat_history:

            if chat["id"] == st.session_state.selected_chat_id:
                selected_chat = chat
                break

    # 대화 내용 표시
    if selected_chat is not None:

        for message in selected_chat["messages"]:

            with st.chat_message(message["role"]):
                st.write(message["content"])

    else:

        st.subheader("새로운 대화")
        st.write("안녕하세요! 에이블입니다. 무엇을 도와드릴까요?")

    # 채팅 입력창
    user_input = st.chat_input("메시지를 입력하세요.")

    # 사용자가 메시지를 입력했을 때
    if user_input:

        # 기존 대화가 없으면 새 대화 생성
        if selected_chat is None:

            new_chat = {
                "id": st.session_state.chat_counter,
                "title": user_input[:30],
                "messages": []
            }

            st.session_state.chat_counter += 1

            st.session_state.chat_history.insert(0, new_chat)

            st.session_state.selected_chat_id = new_chat["id"]

            selected_chat = new_chat

        # 사용자 메시지 저장
        selected_chat["messages"].append({
            "role": "user",
            "content": user_input
        })

        # 이전 대화 + 현재 질문을 함께 전달
        input_messages = [
            {
                "role": "system",
                "content": """
                당신은 업무를 도와주는 친절한 AI 개인 비서 에이블입니다.
                사용자의 이전 대화 내용을 참고하여 자연스럽게 대화를 이어가세요.
                """
            }
        ]

        input_messages.extend(selected_chat["messages"])

        # AI 답변 생성
        with st.spinner("에이블이 답변을 작성하고 있습니다..."):

            response = client.responses.create(
                model="gpt-4o-mini",
                input=input_messages
            )

            answer = response.output_text

        # AI 답변 저장
        selected_chat["messages"].append({
            "role": "assistant",
            "content": answer
        })

        # 최근 대화 10개만 유지
        st.session_state.chat_history = (
            st.session_state.chat_history[:10]
        )

        # 화면 새로고침
        st.rerun()

    st.divider()

    # 최근 대화 목록
    st.subheader("🕘 최근 대화")

    if st.session_state.chat_history:

        for chat in st.session_state.chat_history:

            if st.button(
                chat["title"],
                key=f"chat_{chat['id']}",
                use_container_width=True
            ):

                st.session_state.selected_chat_id = chat["id"]
                st.rerun()

    else:

        st.info("아직 이전 대화가 없습니다.")

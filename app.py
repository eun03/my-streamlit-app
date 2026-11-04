
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

[data-testid="stForm"] {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #E5EAF3;
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
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_chat_id" not in st.session_state:
    st.session_state.selected_chat_id = None


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
    st.caption("에이블에게 업무와 관련된 내용을 질문해 보세요.")

    st.divider()

    # 새로운 대화 영역
    st.subheader("✏️ 새로운 대화")

    with st.form("chat_form"):

        user_input = st.text_area(
            "메시지 입력",
            placeholder="에이블에게 무엇이든 질문해 보세요.",
            height=100
        )

        send = st.form_submit_button("전송")

    # 메시지 전송
    if send:

        if user_input.strip():

            with st.spinner("에이블이 답변을 작성하고 있습니다..."):

                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {
                            "role": "system",
                            "content": "당신은 업무를 도와주는 친절한 AI 개인 비서 에이블입니다."
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                )

                answer = response.output_text

            # 새로운 대화 저장
            new_chat = {
                "id": len(st.session_state.chat_history),
                "title": user_input[:30],
                "messages": [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": answer}
                ]
            }

            st.session_state.chat_history.insert(0, new_chat)

            # 최근 대화 10개만 유지
            st.session_state.chat_history = st.session_state.chat_history[:10]

            st.session_state.selected_chat_id = new_chat["id"]

            st.rerun()

        else:
            st.warning("메시지를 입력해주세요.")

    st.divider()

    # 최근 대화 영역
    st.subheader("🕘 최근 대화")

    if st.session_state.chat_history:

        for chat in st.session_state.chat_history:

            if st.button(
                chat["title"],
                key=f"chat_{chat['id']}",
                use_container_width=True
            ):
                st.session_state.selected_chat_id = chat["id"]

        # 선택한 대화 내용 표시
        selected_chat = next(
            (
                chat for chat in st.session_state.chat_history
                if chat["id"] == st.session_state.selected_chat_id
            ),
            None
        )

        if selected_chat:

            st.divider()
            st.subheader("대화 내용")

            for message in selected_chat["messages"]:

                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])

                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])

    else:

        st.info("아직 이전 대화가 없습니다. 새로운 대화를 시작해 보세요.")

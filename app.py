
import os, base64, json, requests
import streamlit as st
from openai import OpenAI
from datetime import datetime

# OpenAI 클라이언트 생성
client = OpenAI()

# 페이지 설정
st.set_page_config(
    page_title="ABLE - AI Personal Assistant",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# 세션 상태 초기화
# ==========================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_chat_id" not in st.session_state:
    st.session_state.selected_chat_id = None

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

if "chat_page" not in st.session_state:
    st.session_state.chat_page = "새로운 대화"

if "menu" not in st.session_state:
    st.session_state.menu = "🏠  홈"

if "edit_chat_id" not in st.session_state:
    st.session_state.edit_chat_id = None

# 음성 비서 하위 메뉴
if "voice_page" not in st.session_state:
    st.session_state.voice_page = "음성 명령"

# 음성 명령 대화 기록
if "voice_messages" not in st.session_state:
    st.session_state.voice_messages = []

# 실시간 음성 대화 기록
if "realtime_messages" not in st.session_state:
    st.session_state.realtime_messages = []


# ==========================================
# 디자인 설정
# ==========================================

st.markdown("""
<style>

/* 전체 메인 배경 */
[data-testid="stAppViewContainer"] {
    background-color: #F3F6FD;
}

/* 왼쪽 사이드바 배경 */
[data-testid="stSidebar"] {
    background-color: #192D52;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 30px;
}

/* 사이드바 글자 흰색 */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
    color: #FFFFFF !important;
}

/* 사이드바 구분선 */
[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.15);
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

/* 사이드바 버튼 기본 디자인 */
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    color: #FFFFFF !important;
    text-align: left;
    justify-content: flex-start;
    padding: 8px 12px;
    min-height: 40px;
    font-size: 15px;
    box-shadow: none;
    transition: background-color 0.2s;
}

/* 버튼 내부 글씨 */
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span {
    color: #FFFFFF !important;
}

/* 버튼 내부 글씨 왼쪽 정렬 */
[data-testid="stSidebar"] .stButton > button > div {
    justify-content: flex-start;
    width: 100%;
}

/* 사이드바 버튼 마우스 올렸을 때 */
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.12);
    color: #FFFFFF;
    border: none;
}

/* 하위 메뉴 기본 디자인 */
[data-testid="stSidebar"] .st-key-sub_new button,
[data-testid="stSidebar"] .st-key-sub_recent button,
[data-testid="stSidebar"] .st-key-voice_command button,
[data-testid="stSidebar"] .st-key-voice_realtime button {
    color: #B8C5DC !important;
    background-color: transparent;
    font-size: 14px;
    padding-left: 30px;
    min-height: 36px;
}

/* 하위 메뉴 글씨 */
[data-testid="stSidebar"] .st-key-sub_new button p,
[data-testid="stSidebar"] .st-key-sub_recent button p,
[data-testid="stSidebar"] .st-key-voice_command button p,
[data-testid="stSidebar"] .st-key-voice_realtime button p {
    color: #B8C5DC !important;
}

/* 하위 메뉴 마우스 올렸을 때 */
[data-testid="stSidebar"] .st-key-sub_new button:hover,
[data-testid="stSidebar"] .st-key-sub_recent button:hover,
[data-testid="stSidebar"] .st-key-voice_command button:hover,
[data-testid="stSidebar"] .st-key-voice_realtime button:hover {
    background-color: rgba(255, 255, 255, 0.10);
    color: #FFFFFF !important;
}

/* 메인 화면 버튼 */
.stMain .stButton > button {
    border-radius: 8px;
    border: 1px solid #DCE3F0;
    background-color: white;
    color: #192D52;
}

/* 메인 화면 버튼 마우스 올렸을 때 */
.stMain .stButton > button:hover {
    background-color: #EEF1FF;
    color: #4D5BD4;
    border-color: #AAB5FF;
}

/* 채팅 입력창 */
[data-testid="stChatInput"] {
    background-color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 대화 찾기 함수
# ==========================================

def get_chat(chat_id):

    for chat in st.session_state.chat_history:

        if chat["id"] == chat_id:
            return chat

    return None


# ==========================================
# AI 메시지 전송 함수
# ==========================================

def send_message(chat, user_input):

    chat["messages"].append({
        "role": "user",
        "content": user_input
    })

    input_messages = [
        {
            "role": "system",
            "content": """
            당신은 업무를 도와주는 친절한 AI 개인 비서 에이블입니다.
            사용자의 이전 대화 내용을 참고하여 자연스럽게 대화를 이어가세요.
            """
        }
    ]

    input_messages.extend(chat["messages"])

    try:

        with st.spinner("에이블이 답변을 작성하고 있습니다..."):

            response = client.responses.create(
                model="gpt-4o-mini",
                input=input_messages
            )

            answer = response.output_text

        chat["messages"].append({
            "role": "assistant",
            "content": answer
        })

        chat["updated_at"] = datetime.now()

        st.session_state.chat_history.sort(
            key=lambda x: x["updated_at"],
            reverse=True
        )

        st.session_state.chat_history = (
            st.session_state.chat_history[:10]
        )

    except Exception as e:

        st.error(f"답변 생성 중 오류가 발생했습니다: {e}")


# ==========================================
# AI 답변 생성 함수
# ==========================================

def get_ai_answer(messages):

    input_messages = [
        {
            "role": "system",
            "content": """
            당신은 업무를 도와주는 친절한 AI 개인 비서 에이블입니다.
            사용자의 이전 대화 내용을 참고하여 자연스럽게 대화를 이어가세요.
            """
        }
    ]

    input_messages.extend(messages)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=input_messages
    )

    return response.output_text


# ==========================================
# 음성 → 텍스트 변환 함수
# ==========================================

def speech_to_text(audio_value):

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=(
            "audio.wav",
            audio_value.getvalue(),
            "audio/wav"
        )
    )

    return transcript.text


# ==========================================
# 텍스트 → 음성 변환 함수
# ==========================================

def text_to_speech(text):

    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    return speech_response.content


# ==========================================
# 대화 내용 출력 함수
# ==========================================

def show_messages(chat):

    for message in chat["messages"]:

        with st.chat_message(message["role"]):
            st.write(message["content"])


# ==========================================
# 왼쪽 사이드바
# ==========================================

with st.sidebar:

    st.title("ABLE")
    st.caption("AI PERSONAL ASSISTANT")

    st.divider()

    st.subheader("메뉴")

    menu_list = [
        "🏠  홈",
        "📅  일정",
        "📋  회의",
        "✉️  이메일",
        "🎙️  음성 비서",
        "💬  AI 챗봇"
    ]

    # 메인 메뉴
    for i, item in enumerate(menu_list):

        if st.button(
            item,
            key=f"menu_{i}",
            use_container_width=True
        ):

            st.session_state.menu = item

            if item != "💬  AI 챗봇":

                st.session_state.chat_page = "새로운 대화"
                st.session_state.selected_chat_id = None
                st.session_state.edit_chat_id = None

            if item != "🎙️  음성 비서":
                st.session_state.voice_page = "음성 명령"

            st.rerun()

        # 음성 비서 하위 메뉴
        if item == "🎙️  음성 비서":

            if st.session_state.menu == "🎙️  음성 비서":

                if st.button(
                    "🎤  음성 명령",
                    key="voice_command",
                    use_container_width=True
                ):

                    st.session_state.voice_page = "음성 명령"
                    st.rerun()

                if st.button(
                    "🔊  실시간 음성 대화",
                    key="voice_realtime",
                    use_container_width=True
                ):

                    st.session_state.voice_page = "실시간 음성 대화"
                    st.rerun()

        # AI 챗봇 하위 메뉴
        if item == "💬  AI 챗봇":

            if st.session_state.menu == "💬  AI 챗봇":

                if st.button(
                    "✏️  새로운 대화",
                    key="sub_new",
                    use_container_width=True
                ):

                    st.session_state.chat_page = "새로운 대화"
                    st.session_state.selected_chat_id = None
                    st.session_state.edit_chat_id = None

                    st.rerun()

                if st.button(
                    "🕘  최근 대화",
                    key="sub_recent",
                    use_container_width=True
                ):

                    st.session_state.chat_page = "최근 대화"
                    st.session_state.selected_chat_id = None
                    st.session_state.edit_chat_id = None

                    st.rerun()


# 현재 선택한 메뉴
menu = st.session_state.menu


# ==========================================
# 홈 화면
# ==========================================

if menu == "🏠  홈":

    st.title("메인 화면")


# ==========================================
# 일정 화면
# ==========================================

elif menu == "📅  일정":

    st.title("일정")
    st.write("일정 관리 페이지입니다.")


# ==========================================
# 회의 화면
# ==========================================

elif menu == "📋  회의":

    st.title("회의")
    st.write("회의 관리 페이지입니다.")


# ==========================================
# 이메일 화면
# ==========================================

elif menu == "✉️  이메일":

    st.title("이메일")
    st.write("이메일 관리 페이지입니다.")


# ==========================================
# 음성 비서 화면
# ==========================================

elif menu == "🎙️  음성 비서":

    # --------------------------------------
    # 음성 명령
    # --------------------------------------

    if st.session_state.voice_page == "음성 명령":

        st.title("🎤 음성 명령")

        st.caption(
            "음성으로 업무를 요청하고 STT 변환 결과와 AI 답변을 확인하세요."
        )

        # 텍스트 파일 업로드
        uploaded_file = st.file_uploader(
            "텍스트 파일 업로드",
            type=["txt"],
            key="command_file"
        )

        # 음성 녹음
        audio_value = st.audio_input(
            "무엇을 도와드릴까요?",
            key="command_audio"
        )

        # 실행 버튼
        if st.button("실행", key="command_submit"):

            if audio_value is None:

                st.warning("음성을 녹음해주세요.")

            else:

                try:

                    # STT 변환
                    with st.spinner("음성을 텍스트로 변환하고 있습니다..."):

                        transcript_text = speech_to_text(audio_value)

                    # STT 결과 표시
                    st.subheader("음성 인식 결과")
                    st.write(transcript_text)

                    # 업로드 파일 읽기
                    file_text = ""

                    if uploaded_file is not None:

                        file_text = uploaded_file.read().decode("utf-8")

                    # 음성 인식 결과와 파일 내용 결합
                    user_message = transcript_text

                    if file_text:

                        user_message += (
                            "\n\n다음 업로드 파일 내용도 참고하세요:\n"
                            + file_text
                        )

                    # 대화 기록에 사용자 메시지 저장
                    st.session_state.voice_messages.append({
                        "role": "user",
                        "content": user_message
                    })

                    # AI 답변 생성
                    with st.spinner("에이블이 답변을 작성하고 있습니다..."):

                        answer = get_ai_answer(
                            st.session_state.voice_messages
                        )

                    # AI 답변 저장
                    st.session_state.voice_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                    # AI 답변 표시
                    st.subheader("AI 답변")
                    st.write(answer)

                except Exception as e:

                    st.error(f"오류가 발생했습니다: {e}")


    # --------------------------------------
    # 실시간 음성 대화
    # --------------------------------------

    elif st.session_state.voice_page == "실시간 음성 대화":

        st.title("🔊 실시간 음성 대화")

        st.caption(
            "에이블과 음성으로 대화해 보세요. 답변은 음성으로 들려드립니다."
        )

        st.info(
            "텍스트 파일을 업로드하거나 마이크로 말해보세요."
        )

        # 텍스트 파일 업로드
        uploaded_file = st.file_uploader(
            "텍스트 파일 업로드",
            type=["txt"],
            key="realtime_file"
        )

        # 음성 녹음
        audio_value = st.audio_input(
            "에이블에게 말해보세요.",
            key="realtime_audio"
        )

        # 대화하기 버튼
        if st.button("대화하기", key="realtime_submit"):

            if audio_value is None:

                st.warning("먼저 음성을 녹음해주세요.")

            else:

                try:

                    # STT 변환
                    with st.spinner("말씀을 듣고 있습니다..."):

                        transcript_text = speech_to_text(audio_value)

                    # 업로드 파일 읽기
                    file_text = ""

                    if uploaded_file is not None:

                        file_text = uploaded_file.read().decode("utf-8")

                    # 음성 내용과 파일 내용 결합
                    user_message = transcript_text

                    if file_text:

                        user_message += (
                            "\n\n다음 업로드 파일 내용을 참고하여 답변해주세요:\n"
                            + file_text
                        )

                    # 사용자 메시지 저장
                    st.session_state.realtime_messages.append({
                        "role": "user",
                        "content": user_message
                    })

                    # AI 답변 생성
                    with st.spinner("에이블이 답변하고 있습니다..."):

                        answer = get_ai_answer(
                            st.session_state.realtime_messages
                        )

                    # AI 답변 저장
                    st.session_state.realtime_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                    # 답변 음성 변환
                    with st.spinner("답변을 음성으로 변환하고 있습니다..."):

                        audio_response = text_to_speech(answer)

                    # 음성으로 답변 재생
                    st.audio(
                        audio_response,
                        format="audio/mp3"
                    )

                except Exception as e:

                    st.error(f"음성 대화 중 오류가 발생했습니다: {e}")

        # 대화 초기화
        if st.button("대화 초기화", key="realtime_reset"):

            st.session_state.realtime_messages = []

            st.rerun()


# ==========================================
# AI 챗봇 화면
# ==========================================

elif menu == "💬  AI 챗봇":

    # --------------------------------------
    # 새로운 대화
    # --------------------------------------

    if st.session_state.chat_page == "새로운 대화":

        st.title("✏️ 새로운 대화")
        st.caption("에이블과 자유롭게 대화를 나눠보세요.")

        selected_chat = get_chat(
            st.session_state.selected_chat_id
        )

        if selected_chat is not None:

            show_messages(selected_chat)

        else:

            st.write(
                "안녕하세요! 에이블입니다. 무엇을 도와드릴까요?"
            )

        user_input = st.chat_input(
            "메시지를 입력하세요.",
            key="new_chat_input"
        )

        if user_input:

            if selected_chat is None:

                selected_chat = {
                    "id": st.session_state.chat_counter,
                    "title": user_input[:30],
                    "messages": [],
                    "updated_at": datetime.now()
                }

                st.session_state.chat_counter += 1

                st.session_state.chat_history.insert(
                    0, selected_chat
                )

                st.session_state.selected_chat_id = (
                    selected_chat["id"]
                )

            send_message(selected_chat, user_input)

            st.rerun()


    # --------------------------------------
    # 최근 대화
    # --------------------------------------

    elif st.session_state.chat_page == "최근 대화":

        st.title("🕘 최근 대화")
        st.caption(
            "이전에 나눈 대화를 확인하고 이어서 대화할 수 있습니다."
        )

        if not st.session_state.chat_history:

            st.info("아직 저장된 대화가 없습니다.")

        else:

            st.session_state.chat_history.sort(
                key=lambda x: x["updated_at"],
                reverse=True
            )

            st.subheader("대화 목록")

            for chat in st.session_state.chat_history:

                # 제목 수정 중인 경우
                if st.session_state.edit_chat_id == chat["id"]:

                    title_col, save_col = st.columns([8, 1])

                    with title_col:

                        new_title = st.text_input(
                            "대화 제목",
                            value=chat["title"],
                            key=f"title_input_{chat['id']}",
                            label_visibility="collapsed"
                        )

                    with save_col:

                        if st.button(
                            "저장",
                            key=f"save_{chat['id']}"
                        ):

                            if new_title.strip():

                                chat["title"] = new_title.strip()

                                st.session_state.edit_chat_id = None

                                st.rerun()

                            else:

                                st.warning("제목을 입력해주세요.")

                # 일반 상태인 경우
                else:

                    col1, col2 = st.columns([8, 1])

                    with col1:

                        if st.button(
                            chat["title"],
                            key=f"open_{chat['id']}",
                            use_container_width=True
                        ):

                            st.session_state.selected_chat_id = (
                                chat["id"]
                            )

                            st.session_state.edit_chat_id = None

                            st.rerun()

                    with col2:

                        with st.popover("⋯"):

                            if st.button(
                                "✏️ 제목 수정",
                                key=f"edit_{chat['id']}",
                                use_container_width=True
                            ):

                                st.session_state.edit_chat_id = chat["id"]

                                st.rerun()

                            if st.button(
                                "🗑️ 삭제",
                                key=f"delete_{chat['id']}",
                                use_container_width=True
                            ):

                                st.session_state.chat_history = [
                                    item
                                    for item in st.session_state.chat_history
                                    if item["id"] != chat["id"]
                                ]

                                if st.session_state.selected_chat_id == chat["id"]:
                                    st.session_state.selected_chat_id = None

                                if st.session_state.edit_chat_id == chat["id"]:
                                    st.session_state.edit_chat_id = None

                                st.rerun()

                st.caption(
                    chat["updated_at"].strftime("%m/%d")
                )

            # 선택한 대화 가져오기
            selected_chat = get_chat(
                st.session_state.selected_chat_id
            )

            if selected_chat is not None:

                st.divider()

                st.subheader("대화 내용")

                show_messages(selected_chat)

                user_input = st.chat_input(
                    "이 대화에서 계속 질문하세요.",
                    key=f"recent_chat_input_{selected_chat['id']}"
                )

                if user_input:

                    send_message(selected_chat, user_input)

                    st.rerun()

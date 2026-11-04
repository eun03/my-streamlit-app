
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


# ==========================================
# 디자인 설정
# ==========================================

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

/* 사이드바 버튼 기본 디자인 */
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    color: #FFFFFF;
    text-align: left;
    justify-content: flex-start;
    padding: 8px 12px;
    min-height: 40px;
    font-size: 15px;
    box-shadow: none;
    transition: background-color 0.2s;
}

/* 버튼 내부 글씨 왼쪽 정렬 */
[data-testid="stSidebar"] .stButton > button > div {
    justify-content: flex-start;
    width: 100%;
}

/* 메인 메뉴 마우스 올렸을 때 */
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.12);
    color: #FFFFFF;
    border: none;
}

/* 하위 메뉴 기본 디자인 */
[data-testid="stSidebar"] .st-key-sub_new button,
[data-testid="stSidebar"] .st-key-sub_recent button {
    color: #B8C5DC;
    background-color: transparent;
    font-size: 14px;
    padding-left: 30px;
    min-height: 36px;
}

/* 하위 메뉴 마우스 올렸을 때 */
[data-testid="stSidebar"] .st-key-sub_new button:hover,
[data-testid="stSidebar"] .st-key-sub_recent button:hover {
    background-color: rgba(255, 255, 255, 0.10);
    color: #FFFFFF;
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

    # 사용자 메시지 저장
    chat["messages"].append({
        "role": "user",
        "content": user_input
    })

    # 시스템 메시지
    input_messages = [
        {
            "role": "system",
            "content": """
            당신은 업무를 도와주는 친절한 AI 개인 비서 에이블입니다.
            사용자의 이전 대화 내용을 참고하여 자연스럽게 대화를 이어가세요.
            """
        }
    ]

    # 이전 대화 내용 추가
    input_messages.extend(chat["messages"])

    try:

        with st.spinner("에이블이 답변을 작성하고 있습니다..."):

            response = client.responses.create(
                model="gpt-4o-mini",
                input=input_messages
            )

            answer = response.output_text

        # AI 답변 저장
        chat["messages"].append({
            "role": "assistant",
            "content": answer
        })

        # 대화 시간 갱신
        chat["updated_at"] = datetime.now()

        # 최신 대화가 위쪽에 오도록 정렬
        st.session_state.chat_history.sort(
            key=lambda x: x["updated_at"],
            reverse=True
        )

        # 최근 대화 10개만 유지
        st.session_state.chat_history = (
            st.session_state.chat_history[:10]
        )

    except Exception as e:

        st.error(f"답변 생성 중 오류가 발생했습니다: {e}")


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

    # 메인 메뉴 목록
    menu_list = [
        "🏠  홈",
        "📅  일정",
        "📋  회의",
        "✉️  이메일",
        "🎙️  음성 비서",
        "💬  AI 챗봇"
    ]

    # 메인 메뉴 버튼
    for i, item in enumerate(menu_list):

        if st.button(
            item,
            key=f"menu_{i}",
            use_container_width=True
        ):

            st.session_state.menu = item

            # 다른 메뉴로 이동하면 선택된 대화 초기화
            if item != "💬  AI 챗봇":

                st.session_state.chat_page = "새로운 대화"
                st.session_state.selected_chat_id = None
                st.session_state.edit_chat_id = None

            st.rerun()

    # AI 챗봇 하위 메뉴
    if st.session_state.menu == "💬  AI 챗봇":

        st.markdown(
            "<div style='height:5px'></div>",
            unsafe_allow_html=True
        )

        # 새로운 대화
        if st.button(
            "✏️  새로운 대화",
            key="sub_new",
            use_container_width=True
        ):

            st.session_state.chat_page = "새로운 대화"
            st.session_state.selected_chat_id = None
            st.session_state.edit_chat_id = None

            st.rerun()

        # 최근 대화
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

        # 현재 대화 가져오기
        selected_chat = get_chat(
            st.session_state.selected_chat_id
        )

        # 기존 대화 내용 출력
        if selected_chat is not None:

            show_messages(selected_chat)

        else:

            st.write(
                "안녕하세요! 에이블입니다. 무엇을 도와드릴까요?"
            )

        # 채팅 입력창
        user_input = st.chat_input(
            "메시지를 입력하세요.",
            key="new_chat_input"
        )

        if user_input:

            # 새 대화 생성
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

            # AI 메시지 전송
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

        # 대화가 없는 경우
        if not st.session_state.chat_history:

            st.info("아직 저장된 대화가 없습니다.")

        else:

            # 최신 대화순 정렬
            st.session_state.chat_history.sort(
                key=lambda x: x["updated_at"],
                reverse=True
            )

            st.subheader("대화 목록")

            # 최근 대화 목록 출력
            for chat in st.session_state.chat_history:

                col1, col2 = st.columns([8, 1])

                # 대화 제목 또는 제목 수정 입력창
                with col1:

                    if st.session_state.edit_chat_id == chat["id"]:

                        title_col, save_col, cancel_col = st.columns(
                            [6, 1, 1]
                        )

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

                        with cancel_col:

                            if st.button(
                                "취소",
                                key=f"cancel_{chat['id']}"
                            ):

                                st.session_state.edit_chat_id = None

                                st.rerun()

                    else:

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

                # 점 세 개 메뉴
                with col2:

                    with st.popover("⋯"):

                        # 제목 수정
                        if st.button(
                            "✏️ 제목 수정",
                            key=f"edit_{chat['id']}",
                            use_container_width=True
                        ):

                            st.session_state.edit_chat_id = chat["id"]

                            st.rerun()

                        # 대화 삭제
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

                            # 선택된 대화가 삭제된 경우 초기화
                            if st.session_state.selected_chat_id == chat["id"]:

                                st.session_state.selected_chat_id = None

                            # 수정 중이던 대화가 삭제된 경우 초기화
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

                # 이전 대화 내용 출력
                show_messages(selected_chat)

                # 기존 대화 이어서 질문하기
                user_input = st.chat_input(
                    "이 대화에서 계속 질문하세요.",
                    key=f"recent_chat_input_{selected_chat['id']}"
                )

                if user_input:

                    send_message(selected_chat, user_input)

                    st.rerun()

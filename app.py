
import os, base64, json, requests
import streamlit as st
from openai import OpenAI
from datetime import datetime
import calendar
from datetime import date

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


# 회의 기능 세션 상태
if "meeting_page" not in st.session_state:
    st.session_state.meeting_page = "회의 관리"

if "meeting_events" not in st.session_state:
    st.session_state.meeting_events = []

if "meeting_counter" not in st.session_state:
    st.session_state.meeting_counter = 0

if "meeting_selected_date" not in st.session_state:
    st.session_state.meeting_selected_date = date.today()

if "meeting_year" not in st.session_state:
    st.session_state.meeting_year = date.today().year

if "meeting_month" not in st.session_state:
    st.session_state.meeting_month = date.today().month

if "meeting_edit_id" not in st.session_state:
    st.session_state.meeting_edit_id = None

if "meeting_summary_result" not in st.session_state:
    st.session_state.meeting_summary_result = ""

if "meeting_task_result" not in st.session_state:
    st.session_state.meeting_task_result = ""


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
[data-testid="stSidebar"] .st-key-voice_realtime button,
[data-testid="stSidebar"] .st-key-meeting_manage button,
[data-testid="stSidebar"] .st-key-meeting_summary button,
[data-testid="stSidebar"] .st-key-meeting_tasks button {
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
[data-testid="stSidebar"] .st-key-voice_realtime button p,
[data-testid="stSidebar"] .st-key-meeting_manage button p,
[data-testid="stSidebar"] .st-key-meeting_summary button p,
[data-testid="stSidebar"] .st-key-meeting_tasks button p {
    color: #B8C5DC !important;
}

/* 하위 메뉴 마우스 올렸을 때 */
[data-testid="stSidebar"] .st-key-sub_new button:hover,
[data-testid="stSidebar"] .st-key-sub_recent button:hover,
[data-testid="stSidebar"] .st-key-voice_command button:hover,
[data-testid="stSidebar"] .st-key-voice_realtime button:hover,
[data-testid="stSidebar"] .st-key-meeting_manage button:hover,
[data-testid="stSidebar"] .st-key-meeting_summary button:hover,
[data-testid="stSidebar"] .st-key-meeting_tasks button:hover {
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
# 회의 기능 함수
# ==========================================

def read_meeting_txt(uploaded_file):
    """TXT 회의록 파일을 읽습니다."""
    file_bytes = uploaded_file.getvalue()
    for encoding in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("TXT 파일 인코딩을 읽을 수 없습니다.")


def get_meeting_ai_result(meeting_text, task_mode=False):
    """회의록 요약 또는 김 대리 담당 업무를 AI로 추출합니다."""
    if task_mode:
        instruction = """
회의록을 분석하여 '김 대리'에게 배정된 업무만 추출하세요.
각 업무별로 업무 내용, 담당자, 마감일, 주의사항을 정리하세요.
김 대리에게 배정된 업무가 명확하지 않으면 임의로 추측하지 말고
'회의록에서 김 대리 담당 업무를 확인할 수 없습니다.'라고 답하세요.
마감일이나 주의사항이 명시되지 않았다면 '명시되지 않음'이라고 표시하세요.
표 또는 항목별 목록으로 읽기 쉽게 작성하세요.
"""
    else:
        instruction = """
회의록의 주요 내용을 요약하세요.
회의 목적, 주요 논의 내용, 결정 사항, 후속 조치 순서로 정리하세요.
회의록에 없는 내용은 추측하지 마세요.
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": meeting_text}
        ]
    )
    return response.output_text


def show_meeting_calendar():
    """월별 회의 달력과 날짜 선택 기능을 표시합니다."""
    year = st.session_state.meeting_year
    month = st.session_state.meeting_month

    prev_col, title_col, next_col = st.columns([1, 3, 1])
    with prev_col:
        if st.button("◀ 이전 달", key="meeting_prev_month"):
            if month == 1:
                st.session_state.meeting_year -= 1
                st.session_state.meeting_month = 12
            else:
                st.session_state.meeting_month -= 1
            st.rerun()
    with title_col:
        st.markdown(
            f"<h3 style='text-align:center'>{year}년 {month}월</h3>",
            unsafe_allow_html=True
        )
    with next_col:
        if st.button("다음 달 ▶", key="meeting_next_month"):
            if month == 12:
                st.session_state.meeting_year += 1
                st.session_state.meeting_month = 1
            else:
                st.session_state.meeting_month += 1
            st.rerun()

    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_cols = st.columns(7)
    for col, weekday in zip(weekday_cols, weekdays):
        col.markdown(f"**{weekday}**")

    month_matrix = calendar.monthcalendar(year, month)
    for week_index, week in enumerate(month_matrix):
        cols = st.columns(7)
        for col, day_number in zip(cols, week):
            if day_number == 0:
                col.write(" ")
                continue

            selected = (
                st.session_state.meeting_selected_date
                == date(year, month, day_number)
            )
            event_count = sum(
                1 for event in st.session_state.meeting_events
                if event["date"] == date(year, month, day_number)
            )
            label = f"● {day_number}" if event_count else str(day_number)
            if selected:
                label = f"▣ {label}"

            if col.button(
                label,
                key=f"meeting_day_{year}_{month}_{day_number}",
                use_container_width=True
            ):
                st.session_state.meeting_selected_date = date(
                    year, month, day_number
                )
                st.session_state.meeting_edit_id = None
                st.rerun()


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

        # 회의 하위 메뉴
        if item == "📋  회의":

            if st.session_state.menu == "📋  회의":

                if st.button(
                    "📅  회의 관리",
                    key="meeting_manage",
                    use_container_width=True
                ):
                    st.session_state.meeting_page = "회의 관리"
                    st.session_state.meeting_edit_id = None
                    st.rerun()

                if st.button(
                    "📝  회의록 요약",
                    key="meeting_summary",
                    use_container_width=True
                ):
                    st.session_state.meeting_page = "회의록 요약"
                    st.rerun()

                if st.button(
                    "📌  업무 추출",
                    key="meeting_tasks",
                    use_container_width=True
                ):
                    st.session_state.meeting_page = "업무 추출"
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

    # --------------------------------------
    # 회의 관리
    # --------------------------------------
    if st.session_state.meeting_page == "회의 관리":

        st.subheader("📅 회의 관리")
        show_meeting_calendar()

        selected_date = st.session_state.meeting_selected_date
        st.divider()
        st.subheader(f"{selected_date.strftime('%Y년 %m월 %d일')} 회의 일정")

        selected_events = [
            event for event in st.session_state.meeting_events
            if event["date"] == selected_date
        ]
        selected_events.sort(key=lambda event: event["time"])

        if not selected_events:
            st.info("선택한 날짜에 등록된 회의가 없습니다.")

        for event in selected_events:
            with st.container(border=True):
                info_col, edit_col, delete_col = st.columns([7, 1, 1])
                with info_col:
                    st.markdown(f"**{event['time']} · {event['title']}**")
                    if event["place"]:
                        st.write(f"장소: {event['place']}")
                    if event["attendees"]:
                        st.write(f"참석자: {event['attendees']}")
                    if event["memo"]:
                        st.write(f"메모: {event['memo']}")
                with edit_col:
                    if st.button("수정", key=f"meeting_edit_{event['id']}"):
                        st.session_state.meeting_edit_id = event["id"]
                        st.rerun()
                with delete_col:
                    if st.button("삭제", key=f"meeting_delete_{event['id']}"):
                        st.session_state.meeting_events = [
                            item for item in st.session_state.meeting_events
                            if item["id"] != event["id"]
                        ]
                        st.rerun()

        editing_event = next(
            (
                event for event in st.session_state.meeting_events
                if event["id"] == st.session_state.meeting_edit_id
            ),
            None
        )

        st.divider()
        if editing_event:
            st.subheader("회의 일정 수정")
        else:
            st.subheader("회의 일정 등록")

        with st.form("meeting_event_form"):
            title_value = st.text_input(
                "회의 제목",
                value=editing_event["title"] if editing_event else ""
            )
            date_value = st.date_input(
                "회의 날짜",
                value=editing_event["date"] if editing_event else selected_date
            )
            time_value = st.time_input(
                "회의 시간",
                value=(
                    datetime.strptime(editing_event["time"], "%H:%M").time()
                    if editing_event else datetime.now().replace(
                        minute=0, second=0, microsecond=0
                    ).time()
                )
            )
            place_value = st.text_input(
                "회의 장소",
                value=editing_event["place"] if editing_event else ""
            )
            attendees_value = st.text_input(
                "참석자",
                value=editing_event["attendees"] if editing_event else ""
            )
            memo_value = st.text_area(
                "메모 및 안건",
                value=editing_event["memo"] if editing_event else ""
            )
            save_meeting = st.form_submit_button(
                "수정 완료" if editing_event else "회의 등록"
            )

        if save_meeting:
            if not title_value.strip():
                st.warning("회의 제목을 입력해주세요.")
            else:
                event_data = {
                    "title": title_value.strip(),
                    "date": date_value,
                    "time": time_value.strftime("%H:%M"),
                    "place": place_value.strip(),
                    "attendees": attendees_value.strip(),
                    "memo": memo_value.strip()
                }

                if editing_event:
                    for event in st.session_state.meeting_events:
                        if event["id"] == editing_event["id"]:
                            event.update(event_data)
                            break
                    st.session_state.meeting_edit_id = None
                else:
                    event_data["id"] = st.session_state.meeting_counter
                    st.session_state.meeting_counter += 1
                    st.session_state.meeting_events.append(event_data)

                st.session_state.meeting_selected_date = date_value
                st.session_state.meeting_year = date_value.year
                st.session_state.meeting_month = date_value.month
                st.success("회의 일정이 저장되었습니다.")
                st.rerun()

        if editing_event:
            if st.button("수정 취소", key="meeting_edit_cancel"):
                st.session_state.meeting_edit_id = None
                st.rerun()

    # --------------------------------------
    # 회의록 요약
    # --------------------------------------
    elif st.session_state.meeting_page == "회의록 요약":

        st.subheader("📝 회의록 요약")
        st.write("TXT 형식의 회의록을 업로드하면 AI가 주요 내용을 요약합니다.")

        meeting_file = st.file_uploader(
            "회의록 TXT 파일 업로드",
            type=["txt"],
            key="meeting_summary_file"
        )

        text_col, voice_col = st.columns(2)

        with text_col:
            if st.button("텍스트 답변", key="meeting_summary_text"):
                if meeting_file is None:
                    st.warning("회의록 TXT 파일을 업로드해주세요.")
                else:
                    try:
                        meeting_text = read_meeting_txt(meeting_file)
                        with st.spinner("회의록을 요약하고 있습니다..."):
                            st.session_state.meeting_summary_result = (
                                get_meeting_ai_result(meeting_text)
                            )
                    except Exception as e:
                        st.error(f"회의록 요약 중 오류가 발생했습니다: {e}")

        with voice_col:
            if st.button("음성 답변", key="meeting_summary_voice"):
                if meeting_file is None:
                    st.warning("회의록 TXT 파일을 업로드해주세요.")
                else:
                    try:
                        meeting_text = read_meeting_txt(meeting_file)
                        with st.spinner("회의록을 요약하고 있습니다..."):
                            st.session_state.meeting_summary_result = (
                                get_meeting_ai_result(meeting_text)
                            )
                        with st.spinner("요약 내용을 음성으로 변환하고 있습니다..."):
                            audio_result = text_to_speech(
                                st.session_state.meeting_summary_result
                            )
                        st.audio(audio_result, format="audio/mp3")
                    except Exception as e:
                        st.error(f"음성 답변 생성 중 오류가 발생했습니다: {e}")

        if st.session_state.meeting_summary_result:
            st.markdown("### AI 회의록 요약")
            st.write(st.session_state.meeting_summary_result)

    # --------------------------------------
    # 업무 추출
    # --------------------------------------
    elif st.session_state.meeting_page == "업무 추출":

        st.subheader("📌 업무 추출")
        st.write(
            "회의록에서 김 대리에게 배정된 업무, 마감일 및 주의사항을 추출합니다."
        )

        task_file = st.file_uploader(
            "회의록 TXT 파일 업로드",
            type=["txt"],
            key="meeting_task_file"
        )

        text_col, voice_col = st.columns(2)

        with text_col:
            if st.button("텍스트 답변", key="meeting_task_text"):
                if task_file is None:
                    st.warning("회의록 TXT 파일을 업로드해주세요.")
                else:
                    try:
                        meeting_text = read_meeting_txt(task_file)
                        with st.spinner("김 대리의 담당 업무를 추출하고 있습니다..."):
                            st.session_state.meeting_task_result = (
                                get_meeting_ai_result(meeting_text, task_mode=True)
                            )
                    except Exception as e:
                        st.error(f"업무 추출 중 오류가 발생했습니다: {e}")

        with voice_col:
            if st.button("음성 답변", key="meeting_task_voice"):
                if task_file is None:
                    st.warning("회의록 TXT 파일을 업로드해주세요.")
                else:
                    try:
                        meeting_text = read_meeting_txt(task_file)
                        with st.spinner("김 대리의 담당 업무를 추출하고 있습니다..."):
                            st.session_state.meeting_task_result = (
                                get_meeting_ai_result(meeting_text, task_mode=True)
                            )
                        with st.spinner("업무 추출 결과를 음성으로 변환하고 있습니다..."):
                            audio_result = text_to_speech(
                                st.session_state.meeting_task_result
                            )
                        st.audio(audio_result, format="audio/mp3")
                    except Exception as e:
                        st.error(f"음성 답변 생성 중 오류가 발생했습니다: {e}")

        if st.session_state.meeting_task_result:
            st.markdown("### 김 대리 담당 업무")
            st.write(st.session_state.meeting_task_result)


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

        uploaded_file = st.file_uploader(
            "텍스트 파일 업로드",
            type=["txt"],
            key="command_file"
        )

        audio_value = st.audio_input(
            "무엇을 도와드릴까요?",
            key="command_audio"
        )

        if st.button("실행", key="command_submit"):

            if audio_value is None:

                st.warning("음성을 녹음해주세요.")

            else:

                try:

                    # STT 변환
                    with st.spinner("음성을 텍스트로 변환하고 있습니다..."):

                        transcript_text = speech_to_text(audio_value)

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

                    st.session_state.voice_messages.append({
                        "role": "user",
                        "content": user_message
                    })

                    # AI 답변 생성
                    with st.spinner("에이블이 답변을 작성하고 있습니다..."):

                        answer = get_ai_answer(
                            st.session_state.voice_messages
                        )

                    st.session_state.voice_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

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

        # 음성 명령과 동일한 실행 버튼
        if st.button("실행", key="realtime_submit"):

            if audio_value is None:

                st.warning("음성을 녹음해주세요.")

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

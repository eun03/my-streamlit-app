import streamlit as st
import calendar as pycalendar
import uuid
from datetime import date
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from operator import itemgetter


# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="AIVLE School 학습 도우미",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 2. CSS 디자인
# ==========================================
st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background-color: #edf6f7;
}

/* 전체 여백 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* 기본 메뉴 및 푸터 숨기기 */
#MainMenu, footer {
    visibility: hidden;
}

/* 상단 헤더 유지 - 사이드바 버튼 보호 */
.stAppHeader {
    background-color: transparent;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #78c5cd;
    min-width: 230px;
}

/* 사이드바 내부 여백 */
section[data-testid="stSidebar"] > div {
    padding: 25px 15px;
}

/* 사이드바 글자 */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: white;
}

/* 로고 */
.logo-area {
    background-color: rgba(255,255,255,0.95);
    border-radius: 18px;
    padding: 17px 10px;
    margin-bottom: 30px;
    text-align: center;
}

.logo-area p {
    color: #9aa8b0 !important;
    font-size: 11px;
    margin-bottom: 0;
}

/* 사이드바 메뉴 */
.menu-item {
    color: white;
    padding: 13px 15px;
    margin: 8px 0;
    border-radius: 13px;
    font-size: 15px;
    font-weight: 600;
}

.menu-active {
    background-color: rgba(255,255,255,0.27);
}

/* 메인 인사말 */
.greeting {
    font-size: 29px;
    font-weight: 800;
    color: #19334d;
    margin-bottom: 5px;
}

.sub-greeting {
    color: #91a2ae;
    font-size: 13px;
    margin-bottom: 20px;
}

/* 검색창 */
div[data-testid="stTextInput"] input {
    border: none;
    border-radius: 15px;
    background-color: white;
    min-height: 45px;
    box-shadow: 0 3px 15px rgba(30,60,80,0.07);
}

/* 대시보드 카드 */
.dashboard-card {
    border-radius: 23px;
    padding: 24px;
    min-height: 155px;
    box-shadow: 0 5px 20px rgba(50,80,100,0.07);
    margin-bottom: 18px;
    box-sizing: border-box;
}

.welcome-card {
    background: #43aebe;
    color: white;
}

.result-card {
    background: #83b3f5;
    color: white;
}

.dashboard-card h3 {
    font-size: 20px;
    margin: 0 0 12px 0;
    color: white;
}

.dashboard-card p {
    font-size: 13px;
    line-height: 1.7;
    color: white;
}

/* 기능 카드 */
.feature-card {
    background-color: white;
    border-radius: 20px;
    padding: 17px 12px;
    box-shadow: 0 5px 18px rgba(50,80,100,0.06);
    min-height: 105px;
    text-align: center;
    color: #263c54;
    box-sizing: border-box;
}

.feature-icon {
    font-size: 28px;
    margin-bottom: 8px;
}

.feature-title {
    font-size: 15px;
    font-weight: 800;
}

.feature-desc {
    font-size: 11px;
    color: #a0abb6;
    margin-top: 5px;
}

/* 섹션 제목 */
.section-title {
    font-size: 19px;
    font-weight: 800;
    color: #19334d;
    margin: 15px 0;
}

/* 출결 및 일정 달력 */
.st-key-calendar_panel {
    background: #ffffff;
    border-radius: 24px;
    padding: 22px;
    margin: 18px 0 24px 0;
    box-shadow: 0 5px 20px rgba(50,80,100,0.06);
}
.calendar-panel {
    background: #ffffff;
    border-radius: 24px;
    padding: 22px;
    margin: 18px 0 24px 0;
    box-shadow: 0 5px 20px rgba(50,80,100,0.06);
}
.calendar-caption {
    color: #91a2ae;
    font-size: 12px;
    margin-top: -6px;
    margin-bottom: 12px;
}
.calendar-weekday {
    text-align: center;
    color: #7f929f;
    font-size: 12px;
    font-weight: 700;
    padding: 7px 0;
}
.calendar-legend {
    color: #8496a3;
    font-size: 11px;
    margin-top: 10px;
}
.calendar-subcard {
    background: #f7fafc;
    border: 1px solid #edf2f5;
    border-radius: 16px;
    padding: 15px;
    min-height: 150px;
}
.calendar-subtitle {
    color: #19334d;
    font-weight: 800;
    font-size: 14px;
    margin-bottom: 10px;
}

/* 달력 날짜 버튼 */
.st-key-calendar_day button {
    min-height: 58px;
}

/* 채팅 영역 */
.st-key-chat_panel {
    background-color: white;
    border-radius: 25px;
    padding: 20px;
    box-shadow: 0 5px 20px rgba(50,80,100,0.06);
    min-height: 450px;
}

/* 채팅 제목 */
.chat-heading {
    font-size: 17px;
    font-weight: 800;
    color: #19334d;
    margin-bottom: 12px;
}

.chat-description {
    font-size: 12px;
    color: #9baab4;
    margin-bottom: 15px;
}

/* 채팅 말풍선 */
div[data-testid="stChatMessage"] {
    border-radius: 15px;
    padding: 13px;
    margin-bottom: 12px;
}

/* 사용자 메시지 */
div[data-testid="stChatMessage"]:has(
    div[data-testid="chatAvatarIcon-user"]
) {
    background-color: #e5f5f5;
}

/* AI 메시지 */
div[data-testid="stChatMessage"]:has(
    div[data-testid="chatAvatarIcon-assistant"]
) {
    background-color: #f2f6fb;
}

/* 오른쪽 프로필 */
.profile-card {
    background-color: white;
    border-radius: 24px;
    padding: 25px 15px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(50,80,100,0.06);
    margin-bottom: 20px;
}

.profile-icon {
    font-size: 42px;
    background-color: #e9f1fa;
    width: 80px;
    height: 80px;
    line-height: 80px;
    border-radius: 50%;
    margin: auto;
}

.profile-name {
    color: #19334d;
    font-size: 18px;
    font-weight: 800;
    margin-top: 12px;
}

.profile-desc {
    font-size: 12px;
    color: #a1adb8;
    margin-top: 5px;
}

/* 오른쪽 정보 카드 */
.info-card {
    background-color: white;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(50,80,100,0.05);
}

.info-title {
    color: #19334d;
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 12px;
}

.info-card p {
    font-size: 12px;
    color: #9aa8b3;
    line-height: 1.8;
}

/* 버튼 */
.stButton > button {
    border-radius: 12px;
    border: 1px solid #e5edf1;
    background-color: white;
    color: #29445b;
    min-height: 42px;
    font-size: 13px;
    transition: 0.2s;
}

.stButton > button:hover {
    border-color: #55b9c1;
    color: #269eaa;
    background-color: #f0fbfb;
}

/* 파일 업로드 */
div[data-testid="stFileUploader"] {
    background-color: white;
    border-radius: 13px;
    padding: 10px;
}

/* 채팅 입력 폼 */
div[data-testid="stForm"] {
    background-color: #f3f6fa;
    border-radius: 15px;
    padding: 10px;
    border: none;
}

/* 구분선 */
hr {
    border-color: #e9eff2;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. RAG 설정
# ==========================================
CHROMA_DIR = "chroma_db"
COLLECTION = "aivle_docs"


# 문서 포맷팅 함수
def format_docs(docs):
    return "\n\n".join(
        doc.page_content for doc in docs
    )


# Embedding 및 검색기
@st.cache_resource
def get_retriever():

    embedding = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vectorstore = Chroma(
        collection_name=COLLECTION,
        embedding_function=embedding,
        persist_directory=CHROMA_DIR
    )

    return vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )


# RAG 체인
@st.cache_resource
def get_chain():

    retriever = get_retriever()

    s_msg = """
    당신은 주어진 문서를 기반으로 답변하는
    AIVLE School 학습 도우미입니다.

    반드시 제공된 문서를 기반으로 답변하세요.
    문서에 근거가 없는 내용은 추측하지 마세요.

    [문서]
    {context}
    """

    h_msg = "{input}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", s_msg),
        ("human", h_msg)
    ])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True,
        temperature=0
    )

    rag_chain = (
        {
            "context": itemgetter("input") | retriever | format_docs,
            "input": itemgetter("input")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# ==========================================
# 4. 세션 상태 초기화
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# 달력/출결/일정 데이터
if "calendar_month" not in st.session_state:
    st.session_state.calendar_month = date.today().replace(day=1)

if "selected_calendar_date" not in st.session_state:
    st.session_state.selected_calendar_date = date.today()

if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = []

if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = {}


def events_on(day):
    """해당 날짜에 진행 중인 일정 목록을 반환합니다."""
    result = []
    for event in st.session_state.calendar_events:
        start = date.fromisoformat(event["start"])
        end = date.fromisoformat(event["end"])
        if start <= day <= end:
            result.append(event)
    return result


# 검색창 콜백
def submit_search():

    value = st.session_state.get(
        "search_input", ""
    ).strip()

    if value:
        st.session_state.pending_prompt = value


# ==========================================
# 5. 사이드바
# ==========================================
with st.sidebar:

    # AIVLE 로고
    st.html("""
    <div class="logo-area">
        <img
            src="https://raw.githubusercontent.com/Jangrae/img/master/aivle.png"
            width="145">
        <p>AIVLE SCHOOL</p>
    </div>
    """)

    # 사이드바 메뉴
    st.html("""
    <div class="menu-item menu-active">
        🏠　홈
    </div>
    <div class="menu-item">
        👋　소개
    </div>
    <div class="menu-item">
        📚　교육과정
    </div>
    <div class="menu-item">
        💼　취업과정
    </div>
    <div class="menu-item">
        🗂️　포트폴리오
    </div>
    <div class="menu-item">
        📂　파일 불러오기
    </div>
    <div class="menu-item">
        🧩　온톨로지
    </div>
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    # 관리자
    st.html("""
    <p style="font-size:14px;font-weight:800;color:white;">
        ⚙️ 관리자
    </p>
    """)

    uploaded_file = st.file_uploader(
        "파일 업로드",
        type=["pdf", "txt", "docx"]
    )

    if uploaded_file is not None:
        st.success(
            f"{uploaded_file.name} 선택됨"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 대화 삭제
    if st.button(
        "🗑️ 대화 삭제",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.html("""
    <p style="color:white;font-size:12px;">
        AIVLE School<br>
        Learning Assistant
    </p>
    """)


# ==========================================
# 6. 전체 화면 레이아웃
# ==========================================
left, right = st.columns(
    [7, 3],
    gap="large"
)


# ==========================================
# 7. 중앙 대시보드
# ==========================================
with left:

    # 인사말 및 검색창
    title_col, search_col = st.columns(
        [5, 4]
    )

    with title_col:

        st.html("""
        <div class="greeting">
            Hello, AIVLE! 👋
        </div>
        <div class="sub-greeting">
            오늘도 새로운 지식을 함께 배워봐요.
        </div>
        """)

    with search_col:

        st.text_input(
            "검색",
            placeholder="궁금한 내용을 검색해 보세요.",
            label_visibility="collapsed",
            key="search_input",
            on_change=submit_search
        )

    # ======================================
    # 환영 카드
    # ======================================
    card1, card2 = st.columns(2)

    with card1:

        st.html("""
        <div class="dashboard-card welcome-card">
            <h3>Welcome back! ✨</h3>
            <p>
                AIVLE School 학습 도우미입니다.<br>
                교육 과정, 강의 내용, 미니프로젝트 등<br>
                궁금한 내용을 자유롭게 질문해 보세요!
            </p>
            <div style="font-size:27px;text-align:right;">
                📘 🤖
            </div>
        </div>
        """)

    with card2:

        st.html("""
        <div class="dashboard-card result-card">
            <h3>Learning Guide 📊</h3>
            <p>
                여러분의 학습을 도와드릴게요.<br>
                문서 기반 RAG 시스템을 활용하여<br>
                필요한 정보를 빠르게 찾아보세요.
            </p>
            <div style="font-size:27px;text-align:right;">
                💡 📚
            </div>
        </div>
        """)

    # ======================================
    # 주요 기능 카드
    # ======================================
    st.html("""
    <div class="section-title">
        Quick Menu
    </div>
    """)

    f1, f2, f3 = st.columns(3)

    with f1:

        st.html("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">학습 자료</div>
            <div class="feature-desc">
                교육 문서 기반 질문
            </div>
        </div>
        """)

    with f2:

        st.html("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">학습 Q&A</div>
            <div class="feature-desc">
                AI 문서 검색 및 답변
            </div>
        </div>
        """)

    with f3:

        st.html("""
        <div class="feature-card">
            <div class="feature-icon">🚀</div>
            <div class="feature-title">미니프로젝트</div>
            <div class="feature-desc">
                프로젝트 정보 확인
            </div>
        </div>
        """)

    # ======================================
    # 출결 및 일정 관리 달력
    # ======================================
    st.html("""
    <div class="section-title">📅 출결 & 일정 관리</div>
    <div class="calendar-caption">
        교육 일정과 개인 학습 일정을 확인하고 출결 상태를 기록해 보세요.
    </div>
    """)

    with st.container(key="calendar_panel"):
        # 월 이동 및 월 표시
        month_prev, month_title, month_next = st.columns([1, 5, 1])

        with month_prev:
            if st.button("‹", key="calendar_prev_month", use_container_width=True):
                current_month = st.session_state.calendar_month
                if current_month.month == 1:
                    st.session_state.calendar_month = date(current_month.year - 1, 12, 1)
                else:
                    st.session_state.calendar_month = date(current_month.year, current_month.month - 1, 1)
                st.rerun()

        with month_title:
            st.markdown(
                f"<h3 style='text-align:center;color:#19334d;margin:4px 0 15px 0;'>"
                f"{st.session_state.calendar_month.year}년 {st.session_state.calendar_month.month}월"
                f"</h3>",
                unsafe_allow_html=True
            )

        with month_next:
            if st.button("›", key="calendar_next_month", use_container_width=True):
                current_month = st.session_state.calendar_month
                if current_month.month == 12:
                    st.session_state.calendar_month = date(current_month.year + 1, 1, 1)
                else:
                    st.session_state.calendar_month = date(current_month.year, current_month.month + 1, 1)
                st.rerun()

        # 요일 헤더
        weekday_cols = st.columns(7)
        weekdays = ["일", "월", "화", "수", "목", "금", "토"]
        for col, weekday in zip(weekday_cols, weekdays):
            with col:
                st.markdown(f"<div class='calendar-weekday'>{weekday}</div>", unsafe_allow_html=True)

        # 달력 날짜 버튼
        month_matrix = pycalendar.Calendar(firstweekday=6).monthdayscalendar(
            st.session_state.calendar_month.year,
            st.session_state.calendar_month.month
        )

        for week_index, week in enumerate(month_matrix):
            day_cols = st.columns(7)
            for col_index, day_num in enumerate(week):
                with day_cols[col_index]:
                    if day_num == 0:
                        st.write("")
                    else:
                        this_day = date(
                            st.session_state.calendar_month.year,
                            st.session_state.calendar_month.month,
                            day_num
                        )
                        day_events = events_on(this_day)
                        attendance = st.session_state.attendance_records.get(this_day.isoformat(), {})
                        marker_parts = []
                        if day_events:
                            marker_parts.append("📌")
                        if attendance:
                            marker_parts.append("✓")
                        marker = " ".join(marker_parts)
                        is_selected = this_day == st.session_state.selected_calendar_date
                        label = f"{day_num}\n{marker}" if marker else str(day_num)
                        if st.button(
                            label,
                            key=f"calendar_day_{this_day.isoformat()}",
                            type="primary" if is_selected else "secondary",
                            use_container_width=True
                        ):
                            st.session_state.selected_calendar_date = this_day
                            st.rerun()

        st.markdown(
            "<div class='calendar-legend'>📌 일정 있음　 ✓ 출결 기록 있음　 날짜를 누르면 상세 내용을 확인할 수 있습니다.</div>",
            unsafe_allow_html=True
        )

        st.divider()
        selected_day = st.session_state.selected_calendar_date
        st.markdown(
            f"<div class='calendar-subtitle'>🗓️ {selected_day.strftime('%Y년 %m월 %d일')} 상세 관리</div>",
            unsafe_allow_html=True
        )

        attendance_col, schedule_col = st.columns(2, gap="medium")

        # 출결 관리
        with attendance_col:
            st.markdown("<div class='calendar-subtitle'>✅ 출결 기록</div>", unsafe_allow_html=True)
            saved_attendance = st.session_state.attendance_records.get(selected_day.isoformat(), {})
            with st.form("attendance_form", clear_on_submit=False):
                attendance_status = st.selectbox(
                    "출결 상태",
                    ["미기록", "출석", "지각", "결석", "공결"],
                    index=["미기록", "출석", "지각", "결석", "공결"].index(saved_attendance.get("status", "미기록"))
                )
                attendance_memo = st.text_input(
                    "메모",
                    value=saved_attendance.get("memo", ""),
                    placeholder="출결 관련 메모를 입력하세요."
                )
                save_attendance = st.form_submit_button("출결 저장", use_container_width=True)

            if save_attendance:
                if attendance_status == "미기록":
                    st.session_state.attendance_records.pop(selected_day.isoformat(), None)
                else:
                    st.session_state.attendance_records[selected_day.isoformat()] = {
                        "status": attendance_status,
                        "memo": attendance_memo
                    }
                st.success("출결 정보가 저장되었습니다.")
                st.rerun()

            if saved_attendance:
                st.caption(
                    f"현재 기록: {saved_attendance.get('status', '')}"
                    + (f" · {saved_attendance.get('memo')}" if saved_attendance.get("memo") else "")
                )

        # 일정 등록 및 조회
        with schedule_col:
            st.markdown("<div class='calendar-subtitle'>📝 일정 등록</div>", unsafe_allow_html=True)
            with st.form("schedule_form", clear_on_submit=True):
                event_title = st.text_input("일정 이름", placeholder="예: 데이터 분석 강의")
                event_type = st.selectbox("일정 유형", ["교육", "과제", "시험", "프로젝트", "개인", "기타"])
                event_start = st.date_input("시작일", value=selected_day)
                event_end = st.date_input("종료일", value=selected_day)
                event_memo = st.text_input("상세 내용", placeholder="장소 또는 준비 사항")
                save_event = st.form_submit_button("일정 추가", use_container_width=True)

            if save_event:
                if not event_title.strip():
                    st.warning("일정 이름을 입력해 주세요.")
                elif event_end < event_start:
                    st.warning("종료일은 시작일보다 빠를 수 없습니다.")
                else:
                    st.session_state.calendar_events.append({
                        "id": str(uuid.uuid4()),
                        "title": event_title.strip(),
                        "type": event_type,
                        "start": event_start.isoformat(),
                        "end": event_end.isoformat(),
                        "memo": event_memo.strip()
                    })
                    st.success("일정이 추가되었습니다.")
                    st.rerun()

        # 선택 날짜 일정 목록 및 삭제
        selected_events = events_on(selected_day)
        if selected_events:
            st.markdown("**등록된 일정**")
            for event in selected_events:
                event_col, delete_col = st.columns([8, 1])
                with event_col:
                    date_range = event["start"] if event["start"] == event["end"] else f"{event['start']} ~ {event['end']}"
                    st.markdown(
                        f"📌 **{event['title']}**　`{event['type']}`<br>"
                        f"<span style='color:#8b9aa6;font-size:12px;'>{date_range}"
                        f"{' · ' + event['memo'] if event['memo'] else ''}</span>",
                        unsafe_allow_html=True
                    )
                with delete_col:
                    if st.button("🗑️", key=f"delete_event_{event['id']}"):
                        st.session_state.calendar_events = [
                            item for item in st.session_state.calendar_events
                            if item["id"] != event["id"]
                        ]
                        st.rerun()
        else:
            st.caption("선택한 날짜에 등록된 일정이 없습니다.")

    # ======================================
    # 채팅 영역
    # ======================================
    st.html("""
    <div class="section-title">
        💬 AI Learning Assistant
    </div>
    """)

    with st.container(key="chat_panel"):

        st.html("""
        <div class="chat-heading">
            🤖 AIVLE School 학습 도우미
        </div>
        <div class="chat-description">
            궁금한 내용을 질문하면 관련 문서를 찾아
            답변해 드립니다.
        </div>
        """)

        # 최초 안내 메시지
        if not st.session_state.messages:

            st.info(
                "안녕하세요! 😊 무엇이 궁금하신가요? "
                "아래 입력창에 질문을 작성해 주세요."
            )

        # 기존 대화 출력
        for message in st.session_state.messages:

            role = (
                "user"
                if isinstance(message, HumanMessage)
                else "assistant"
            )

            with st.chat_message(role):
                st.markdown(message.content)

        # 채팅 입력창
        with st.form(
            "chat_form",
            clear_on_submit=True
        ):

            question = st.text_input(
                "질문 입력",
                placeholder="질문을 입력하세요.",
                label_visibility="collapsed"
            )

            submitted = st.form_submit_button(
                "질문 보내기 ➤",
                use_container_width=True
            )


# ==========================================
# 8. 오른쪽 프로필 및 추천 질문
# ==========================================
with right:

    # 프로필
    st.html("""
    <div class="profile-card">
        <div class="profile-icon">
            👩🏻‍💻
        </div>
        <div class="profile-name">
            AIVLE Assistant
        </div>
        <div class="profile-desc">
            Your Learning Partner
        </div>
    </div>
    """)

    # 학습 도우미 안내
    st.html("""
    <div class="info-card">
        <div class="info-title">
            📘 학습 도우미 안내
        </div>
        <p>
            AIVLE School 교육 자료를 기반으로
            질문에 대한 답변을 제공합니다.<br><br>
            <b style="color:#29445b;">
                RAG 기반 문서 검색
            </b><br>
            관련 문서를 검색하고 답변을 생성합니다.
        </p>
    </div>
    """)

    # 추천 질문
    st.html("""
    <div class="section-title">
        💡 추천 질문
    </div>
    """)

    questions = [
        "KT 에이블스쿨 지원 자격은?",
        "미니프로젝트는 어떻게 진행되나요?",
        "교육 과정은 어떻게 구성되나요?",
        "수료 기준은 무엇인가요?"
    ]

    for i, q in enumerate(questions):

        if st.button(
            q,
            key=f"recommend_{i}",
            use_container_width=True
        ):

            st.session_state.pending_prompt = q
            st.rerun()

    # 최근 대화
    st.markdown("<br>", unsafe_allow_html=True)

    st.html("""
    <div class="info-card">
        <div class="info-title">
            🕒 Recent Activity
        </div>
        <p>
            최근 대화 기록
        </p>
    </div>
    """)

    recent_questions = [
        msg.content
        for msg in reversed(st.session_state.messages)
        if isinstance(msg, HumanMessage)
    ]

    if recent_questions:

        for q in recent_questions[:5]:
            st.caption("💬 " + q[:35])

    else:

        st.caption("아직 대화 기록이 없습니다.")


# ==========================================
# 9. RAG 질문 처리
# ==========================================
prompt = None

# 직접 입력한 질문
if submitted and question.strip():

    prompt = question.strip()

# 추천 질문 또는 검색창 질문
elif st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt


if prompt:

    st.session_state.pending_prompt = None

    # 사용자 질문 저장
    st.session_state.messages.append(
        HumanMessage(content=prompt)
    )

    try:

        chain = get_chain()

        with st.spinner(
            "관련 문서를 검색하고 있습니다..."
        ):

            with st.chat_message("assistant"):

                response_stream = chain.stream({
                    "input": prompt
                })

                full_response = st.write_stream(
                    response_stream
                )

        # AI 답변 저장
        st.session_state.messages.append(
            AIMessage(content=full_response)
        )

    except Exception as e:

        st.error(
            f"답변 생성 중 오류가 발생했습니다: {e}"
        )

    st.rerun()

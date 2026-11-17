
import streamlit as st
import calendar
from datetime import date

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from operator import itemgetter


# =====================================================
# 1. 페이지 설정
# =====================================================

st.set_page_config(
    page_title="AIVLE School Learning Assistant",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. 기본 설정
# =====================================================

CHROMA_DIR = "chroma_db"
COLLECTION = "aivle_docs"


# =====================================================
# 3. CSS 디자인
# =====================================================

st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background-color: #EDF6F7;
}

/* 기본 여백 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background-color: #78C2C9;
    min-width: 220px;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

/* 사이드바 텍스트 */
[data-testid="stSidebar"] * {
    color: white;
}

/* 사이드바 버튼 */
[data-testid="stSidebar"] .stButton button {
    background-color: transparent;
    color: white;
    border: none;
    text-align: left;
    font-weight: 600;
    border-radius: 10px;
    height: 45px;
}

[data-testid="stSidebar"] .stButton button:hover {
    background-color: rgba(255,255,255,0.25);
}

/* 메인 제목 */
.main-title {
    font-size: 27px;
    font-weight: 800;
    color: #203D56;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 13px;
    color: #91A6B5;
    margin-bottom: 25px;
}

/* 카드 공통 */
.info-card {
    padding: 24px;
    border-radius: 20px;
    min-height: 170px;
    margin-bottom: 15px;
    box-shadow: 0px 5px 18px rgba(40,80,100,0.06);
}

.welcome-card {
    background-color: #40AFBD;
    color: white;
}

.guide-card {
    background-color: #80AEF2;
    color: white;
}

.info-card h3 {
    font-size: 18px;
    margin-bottom: 12px;
}

.info-card p {
    font-size: 13px;
    line-height: 1.8;
}

/* 섹션 제목 */
.section-title {
    font-size: 19px;
    font-weight: 800;
    color: #203D56;
    margin-top: 20px;
    margin-bottom: 15px;
}

/* 퀵 메뉴 */
.quick-card {
    background: white;
    border-radius: 18px;
    padding: 20px 10px;
    text-align: center;
    min-height: 125px;
    box-shadow: 0px 5px 18px rgba(40,80,100,0.05);
}

.quick-card .emoji {
    font-size: 27px;
    margin-bottom: 10px;
}

.quick-card .quick-name {
    font-size: 15px;
    font-weight: bold;
    color: #29445F;
}

.quick-card .quick-desc {
    font-size: 11px;
    color: #9AAAB8;
    margin-top: 5px;
}

/* 오른쪽 카드 */
.right-card {
    background: white;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0px 5px 18px rgba(40,80,100,0.05);
}

/* 달력 */
.calendar-card {
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 5px 18px rgba(40,80,100,0.05);
}

.calendar-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 8px;
    table-layout: fixed;
}

.calendar-table th {
    color: #91A5B5;
    font-size: 12px;
    padding: 8px;
}

.calendar-table td {
    height: 43px;
    background: white;
    border: 1px solid #E6EEF3;
    border-radius: 10px;
    text-align: center;
    color: #48637D;
    font-size: 12px;
}

.calendar-table td.today {
    background: #40AFBD;
    color: white;
    font-weight: bold;
    border: none;
}

.calendar-table td.empty {
    border: none;
    background: transparent;
}

/* 추천 질문 */
.question-button button {
    background: white;
    border: 1px solid #E8EFF3;
    color: #48637D;
    border-radius: 10px;
    font-size: 12px;
    min-height: 40px;
}

/* 입력창 */
.stTextInput input {
    border-radius: 12px;
    border: 1px solid #E5EDF0;
}

/* 모바일 */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 4. RAG 체인
# =====================================================

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


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


@st.cache_resource
def get_chain():

    retriever = get_retriever()

    s_msg = """
    당신은 주어진 문서를 기반으로 답변하는
    AIVLE School 학습 도우미입니다.

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


# =====================================================
# 5. 세션 상태
# =====================================================

if "page" not in st.session_state:
    st.session_state.page = "홈"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

if "activities" not in st.session_state:
    st.session_state.activities = []


# =====================================================
# 6. 사이드바
# =====================================================

with st.sidebar:

    st.markdown("""
    <div style="
        background:white;
        border-radius:15px;
        padding:20px 10px;
        text-align:center;
        margin-bottom:35px;
    ">
        <div style="font-size:25px; font-weight:900; color:#182C3D;">
            ◢ AIVLE
        </div>
        <div style="font-size:10px; color:#91A6B5;">
            AIVLE SCHOOL
        </div>
    </div>
    """, unsafe_allow_html=True)

    menu_items = {
        "🏠  홈": "홈",
        "👋  소개": "소개",
        "📚  교육과정": "교육과정",
        "💼  취업과정": "취업과정",
        "🗂️  포트폴리오": "포트폴리오",
        "📁  파일 불러오기": "파일 불러오기",
        "🕸️  온톨로지": "온톨로지"
    }

    for label, page in menu_items.items():

        if st.button(
            label,
            key=f"menu_{page}",
            use_container_width=True
        ):
            st.session_state.page = page
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("⚙️  관리자", use_container_width=True):
        st.session_state.page = "관리자"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:white;
        border-radius:12px;
        padding:20px;
        color:#8195A6;
        text-align:center;
    ">
        <div style="font-size:25px;">📤</div>
        <b style="color:#526C80;">파일 업로드</b>
        <p style="font-size:11px; color:#91A6B5;">
            200MB per file · PDF, TXT, DOCX
        </p>
    </div>

    <br>

    <div style="
        background:white;
        border-radius:12px;
        padding:10px;
        text-align:center;
        color:#91A6B5;
        font-size:12px;
    ">
        🗑️
    </div>

    <br><br><br><br>

    <div style="font-size:10px; line-height:1.8;">
        AIVLE School<br>
        Learning Assistant
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 7. 홈 화면
# =====================================================

def page_home():

    # 중앙 + 오른쪽 영역
    main_col, right_col = st.columns(
        [2.5, 1],
        gap="large"
    )

    # ---------------------------------------------
    # 중앙 메인 영역
    # ---------------------------------------------

    with main_col:

        # 상단 제목
        header_col, search_col = st.columns(
            [1.2, 0.9]
        )

        with header_col:
            st.markdown("""
            <div class="main-title">
                Hello, AIVLE! 👋
            </div>
            <div class="sub-title">
                오늘도 새로운 지식을 함께 배워봐요.
            </div>
            """, unsafe_allow_html=True)

        with search_col:

            with st.form("search_form"):
                search = st.text_input(
                    "검색",
                    placeholder="궁금한 내용을 검색해 보세요.",
                    label_visibility="collapsed"
                )

                search_submit = st.form_submit_button(
                    "검색",
                    use_container_width=True
                )

            if search_submit and search.strip():
                st.session_state.pending_question = search
                st.session_state.page = "학습 Q&A"
                st.rerun()

        # 환영 카드
        welcome1, welcome2 = st.columns(2, gap="medium")

        with welcome1:
            st.markdown("""
            <div class="info-card welcome-card">
                <h3>Welcome back! ✨</h3>
                <p>
                    AIVLE School 학습 도우미입니다.<br>
                    교육 과정, 강의 내용, 미니프로젝트 등<br>
                    궁금한 내용을 자유롭게 질문해 보세요!
                </p>
                <div style="text-align:right; font-size:23px;">
                    💻 💬
                </div>
            </div>
            """, unsafe_allow_html=True)

        with welcome2:
            st.markdown("""
            <div class="info-card guide-card">
                <h3>Learning Guide 📊</h3>
                <p>
                    여러분의 학습을 도와드릴게요.<br>
                    문서 기반 RAG 시스템을 활용하여<br>
                    필요한 정보를 빠르게 찾아보세요.
                </p>
                <div style="text-align:right; font-size:23px;">
                    💡 📚
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Quick Menu
        st.markdown(
            '<div class="section-title">Quick Menu</div>',
            unsafe_allow_html=True
        )

        q1, q2, q3 = st.columns(3, gap="small")

        quick_menus = [
            ("📚", "학습 자료", "교육 문서 기반 질문", "학습 Q&A"),
            ("🧠", "학습 Q&A", "AI 문서 검색 및 답변", "학습 Q&A"),
            ("🚀", "미니프로젝트", "프로젝트 정보 확인", "미니프로젝트")
        ]

        for col, item in zip([q1, q2, q3], quick_menus):

            emoji, name, desc, target = item

            with col:

                st.markdown(f"""
                <div class="quick-card">
                    <div class="emoji">{emoji}</div>
                    <div class="quick-name">{name}</div>
                    <div class="quick-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(
                    "바로가기",
                    key=f"quick_{name}",
                    use_container_width=True
                ):
                    st.session_state.page = target
                    st.rerun()

        # 달력 제목
        st.markdown("""
        <div class="section-title">
            🗓️ 출결 & 일정 관리
        </div>
        <div style="font-size:12px; color:#91A6B5;
                    margin-bottom:20px;">
            교육 일정과 개인 학습 일정을 확인하고
            출결 상태를 기록해 보세요.
        </div>
        """, unsafe_allow_html=True)

        # 달력
        today = date.today()

        if "cal_year" not in st.session_state:
            st.session_state.cal_year = today.year

        if "cal_month" not in st.session_state:
            st.session_state.cal_month = today.month

        prev_col, month_col, next_col = st.columns(
            [1, 4, 1]
        )

        with prev_col:
            if st.button("‹", use_container_width=True):
                st.session_state.cal_month -= 1

                if st.session_state.cal_month < 1:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1

                st.rerun()

        with month_col:
            st.markdown(
                f"<h3 style='text-align:center; color:#29445F;'>"
                f"{st.session_state.cal_year}년 "
                f"{st.session_state.cal_month}월"
                f"</h3>",
                unsafe_allow_html=True
            )

        with next_col:
            if st.button("›", use_container_width=True):
                st.session_state.cal_month += 1

                if st.session_state.cal_month > 12:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1

                st.rerun()

        cal = calendar.Calendar(firstweekday=6)

        weeks = cal.monthdayscalendar(
            st.session_state.cal_year,
            st.session_state.cal_month
        )

        calendar_html = """
        <div class="calendar-card">
        <table class="calendar-table">
        <thead>
        <tr>
        <th>일</th><th>월</th><th>화</th>
        <th>수</th><th>목</th><th>금</th><th>토</th>
        </tr>
        </thead>
        <tbody>
        """

        for week in weeks:

            calendar_html += "<tr>"

            for day in week:

                if day == 0:
                    calendar_html += '<td class="empty"></td>'

                elif (
                    day == today.day
                    and st.session_state.cal_month == today.month
                    and st.session_state.cal_year == today.year
                ):
                    calendar_html += (
                        f'<td class="today">{day}</td>'
                    )

                else:
                    calendar_html += f"<td>{day}</td>"

            calendar_html += "</tr>"

        calendar_html += """
        </tbody>
        </table>
        <div style="font-size:11px; color:#91A6B5;
                    margin-top:12px;">
            📌 날짜별 학습 일정을 확인해 보세요.
        </div>
        </div>
        """

        st.markdown(
            calendar_html,
            unsafe_allow_html=True
        )


    # ---------------------------------------------
    # 오른쪽 어시스턴트 영역
    # ---------------------------------------------

    with right_col:

        st.markdown("""
        <div class="right-card" style="text-align:center;">
            <div style="
                background:#EAF1FA;
                width:65px;
                height:65px;
                border-radius:50%;
                margin:auto;
                display:flex;
                justify-content:center;
                align-items:center;
                font-size:30px;
            ">
                👩🏻‍💻
            </div>

            <h3 style="font-size:16px; color:#29445F;">
                AIVLE Assistant
            </h3>

            <p style="font-size:11px; color:#91A6B5;">
                Your Learning Partner
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="right-card">
            <h4 style="font-size:15px; color:#29445F;">
                📘 학습 도우미 안내
            </h4>

            <p style="font-size:11px; color:#91A6B5;
                      line-height:1.8;">
                AIVLE School 교육 자료를 기반으로
                질문에 대한 답변을 제공합니다.
            </p>

            <b style="font-size:12px; color:#29445F;">
                RAG 기반 문서 검색
            </b>

            <p style="font-size:11px; color:#91A6B5;">
                관련 문서를 검색하고 답변을 생성합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-title">
            💡 추천 질문
        </div>
        """, unsafe_allow_html=True)

        questions = [
            "KT 에이블스쿨 지원 자격은?",
            "미니프로젝트는 어떻게 진행되나요?",
            "교육 과정은 어떻게 구성되나요?",
            "수료 기준은 무엇인가요?"
        ]

        for i, question in enumerate(questions):

            if st.button(
                question,
                key=f"recommend_{i}",
                use_container_width=True
            ):
                st.session_state.pending_question = question
                st.session_state.page = "학습 Q&A"
                st.rerun()

        st.markdown("""
        <div class="right-card" style="margin-top:25px;">
            <h4 style="font-size:14px; color:#29445F;">
                🕒 Recent Activity
            </h4>
            <p style="font-size:11px; color:#91A6B5;">
                최근 대화 기록
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.activities:

            for activity in reversed(
                st.session_state.activities[-3:]
            ):
                st.markdown(
                    f"<div style='font-size:11px; "
                    f"color:#8195A6; margin-bottom:10px;'>"
                    f"💬 {activity}</div>",
                    unsafe_allow_html=True
                )

        else:
            st.caption("아직 대화 기록이 없습니다.")


# =====================================================
# 8. 학습 Q&A 화면
# =====================================================

def page_chat():

    st.markdown(
        '<div class="main-title">🧠 학습 Q&A</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'AIVLE School 교육 자료를 기반으로 질문해 보세요.'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("← 홈으로"):
        st.session_state.page = "홈"
        st.rerun()

    # 기존 대화 출력
    for message in st.session_state.messages:

        role = (
            "user"
            if isinstance(message, HumanMessage)
            else "assistant"
        )

        with st.chat_message(role):
            st.markdown(message.content)

    # 추천 질문 등에서 전달된 질문
    pending = st.session_state.pop(
        "pending_question",
        None
    )

    user_input = st.chat_input(
        "궁금한 내용을 입력하세요."
    )

    if pending:
        user_input = pending

    if user_input:

        st.session_state.messages.append(
            HumanMessage(content=user_input)
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):

            chain = get_chain()

            response_stream = chain.stream({
                "input": user_input
            })

            full_response = st.write_stream(
                response_stream
            )

        st.session_state.messages.append(
            AIMessage(content=full_response)
        )

        st.session_state.activities.append(
            user_input
        )

        st.rerun()


# =====================================================
# 9. 기타 페이지
# =====================================================

def page_placeholder():

    st.markdown(
        f'<div class="main-title">'
        f'{st.session_state.page}</div>',
        unsafe_allow_html=True
    )

    st.info(
        f"{st.session_state.page} 페이지는 "
        "다음 단계에서 구현할 예정입니다."
    )

    if st.button("← 홈으로"):
        st.session_state.page = "홈"
        st.rerun()


# =====================================================
# 10. 페이지 실행
# =====================================================

if st.session_state.page == "홈":

    page_home()

elif st.session_state.page == "학습 Q&A":

    page_chat()

else:

    page_placeholder()





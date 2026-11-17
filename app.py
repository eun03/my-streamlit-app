
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
    background: linear-gradient(120deg, #F5FAFB, #EAF5F7);
}

/* 메인 영역 */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1700px;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #55C2CA, #62C3C9);
    min-width: 215px;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

[data-testid="stSidebar"] * {
    color: white;
}

/* 사이드바 버튼 */
[data-testid="stSidebar"] .stButton button {
    background: transparent;
    color: white;
    border: none;
    border-radius: 10px;
    text-align: left;
    font-weight: 700;
    min-height: 42px;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.3);
    color: white;
}

/* 사이드바 파일 업로드 */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: white;
    border-radius: 12px;
    padding: 8px;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: #526C80;
}

/* 공통 제목 */
.main-title {
    font-size: 27px;
    font-weight: 850;
    color: #193653;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 13px;
    color: #91A6B5;
    margin-bottom: 22px;
}

.section-title {
    font-size: 19px;
    font-weight: 850;
    color: #193653;
    margin-top: 15px;
    margin-bottom: 12px;
}

/* 환영 카드 */
.info-card {
    padding: 23px;
    border-radius: 20px;
    min-height: 170px;
    margin-bottom: 12px;
    box-shadow: 0 5px 18px rgba(40,80,100,0.06);
}

.welcome-card {
    background: #40AFBD;
    color: white;
}

.guide-card {
    background: #80AEF2;
    color: white;
}

/* 오른쪽 카드 */
.right-card {
    background: white;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 5px 18px rgba(40,80,100,0.05);
}

/* 퀵 메뉴 */
.quick-card {
    background: white;
    border-radius: 18px;
    padding: 20px 10px;
    text-align: center;
    min-height: 120px;
    box-shadow: 0 5px 18px rgba(40,80,100,0.05);
}

.quick-card .emoji {
    font-size: 27px;
    margin-bottom: 8px;
}

.quick-card .quick-name {
    font-size: 15px;
    font-weight: bold;
    color: #29445F;
}

.quick-card .quick-desc {
    font-size: 11px;
    color: #91A6B5;
    margin-top: 5px;
}

/* 소개 페이지 배너 */
.intro-banner {
    background: linear-gradient(110deg, #DDF5F5, #D5F0F4);
    border-radius: 21px;
    padding: 23px 28px;
    min-height: 185px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 5px 18px rgba(40,80,100,0.05);
    margin-bottom: 17px;
}

.intro-banner h1 {
    font-size: 30px;
    font-weight: 900;
    color: #183653;
    margin: 0 0 5px 0;
}

.intro-banner h3 {
    font-size: 18px;
    color: #169BAA;
    font-weight: 800;
    margin: 0 0 13px 0;
}

.intro-banner p {
    color: #29445F;
    font-size: 13px;
    line-height: 1.8;
    margin: 0;
}

.intro-banner .banner-image {
    font-size: 85px;
    text-align: center;
    min-width: 180px;
}

/* 소개 섹션 번호 */
.section-number {
    display: inline-block;
    background: linear-gradient(90deg, #32BFC6, #1CA7B8);
    color: white;
    border-radius: 9px;
    padding: 4px 10px;
    font-size: 13px;
    font-weight: 900;
    margin-right: 8px;
}

.intro-heading {
    font-size: 19px;
    font-weight: 850;
    color: #193653;
    margin: 10px 0 12px 0;
}

/* 소개 공통 카드 */
.intro-white-card {
    background: white;
    border-radius: 18px;
    padding: 17px;
    box-shadow: 0 5px 17px rgba(40,80,100,0.06);
    height: 100%;
}

.intro-white-card h4 {
    font-size: 15px;
    font-weight: 850;
    color: #193653;
    margin: 5px 0;
}

.intro-white-card p {
    font-size: 12px;
    line-height: 1.7;
    color: #708399;
    margin: 5px 0 0 0;
}

/* 교육 트랙 카드 */
.track-card {
    color: white;
    border-radius: 19px;
    padding: 19px 12px;
    text-align: center;
    min-height: 155px;
}

.track-card h3 {
    font-size: 19px;
    margin: 7px 0;
    font-weight: 850;
}

.track-card p {
    font-size: 12px;
    line-height: 1.7;
    margin: 0;
}

.track-ai {
    background: linear-gradient(135deg, #36C1C7, #20AEBB);
}

.track-dx {
    background: linear-gradient(135deg, #7BB9FF, #5299ED);
}

/* 분야 카드 */
.field-card {
    background: white;
    border-radius: 17px;
    min-height: 75px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 14px rgba(40,80,100,0.06);
    margin-bottom: 7px;
}

.field-card .field-icon {
    font-size: 28px;
}

.field-card strong {
    color: #193653;
    font-size: 13px;
}

.field-card small {
    display: block;
    color: #708399;
    font-size: 11px;
    margin-top: 4px;
}

/* 교육 진행 과정 */
.process-card {
    background: white;
    border-radius: 18px;
    padding: 12px;
    box-shadow: 0 5px 17px rgba(40,80,100,0.05);
}

.process-item {
    background: #E2F6F5;
    border-radius: 15px;
    padding: 15px 8px;
    min-height: 74px;
    display: flex;
    align-items: center;
    gap: 9px;
}

.process-item.blue {
    background: #E8F2FE;
}

.process-item .process-icon {
    font-size: 27px;
}

.process-item strong {
    font-size: 13px;
    color: #193653;
}

.process-item small {
    display: block;
    font-size: 11px;
    color: #708399;
    margin-top: 5px;
}

.process-arrow {
    color: #168B9D;
    font-size: 23px;
    font-weight: 900;
    text-align: center;
    padding-top: 20px;
}

/* 핵심 역량 */
.skill-card {
    background: white;
    border-radius: 18px;
    padding: 17px 10px;
    text-align: center;
    min-height: 130px;
    box-shadow: 0 5px 17px rgba(40,80,100,0.06);
}

.skill-card .skill-icon {
    font-size: 29px;
}

.skill-card h4 {
    color: #193653;
    font-size: 14px;
    font-weight: 850;
    margin: 7px 0;
}

.skill-card p {
    color: #708399;
    font-size: 11px;
    line-height: 1.7;
    margin: 0;
}

/* 하단 배너 */
.bottom-banner {
    background: linear-gradient(110deg, #147E8D, #168B9A);
    border-radius: 19px;
    padding: 17px 25px;
    color: white;
    margin-top: 20px;
}

.bottom-banner h3 {
    color: white;
    font-size: 19px;
    margin: 0 0 5px 0;
}

.bottom-banner p {
    font-size: 12px;
    margin: 0;
}

/* 달력 */
.calendar-card {
    background: white;
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 5px 18px rgba(40,80,100,0.05);
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
}

.calendar-table td.empty {
    border: none;
    background: transparent;
}

/* 검색창 */
.stTextInput input {
    border-radius: 12px;
    border: 1px solid #E5EDF0;
}

/* 일반 버튼 */
.stButton button {
    border-radius: 10px;
}

/* 반응형 */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    .intro-banner h1 {
        font-size: 22px;
    }

    .intro-banner .banner-image {
        font-size: 50px;
        min-width: 70px;
    }
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 4. RAG 체인
# =====================================================

def format_docs(docs):
    return "\n\n".join(
        doc.page_content for doc in docs
    )


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

    문서에 없는 내용은 임의로 만들어내지 마세요.
    문서에서 확인할 수 없는 내용이라면
    확인할 수 없다고 안내하세요.

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
# 5. 세션 상태 초기화
# =====================================================

if "page" not in st.session_state:
    st.session_state.page = "홈"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "activities" not in st.session_state:
    st.session_state.activities = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


# =====================================================
# 6. 사이드바
# =====================================================

def render_sidebar():

    with st.sidebar:

        # 로고
        st.markdown("""
        <div style="
            background:white;
            border-radius:14px;
            padding:16px 8px;
            text-align:center;
            margin-bottom:27px;
        ">
            <div style="
                font-size:27px;
                font-weight:900;
                color:#17354F;
            ">
                ◢ AIVLE
            </div>
            <div style="
                color:#159EAD;
                font-size:12px;
            ">
                AIVLE SCHOOL
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 메뉴
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

        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.4);'>",
            unsafe_allow_html=True
        )

        if st.button(
            "⚙️  관리자",
            use_container_width=True
        ):

            st.session_state.page = "관리자"
            st.rerun()

        # 문서 업로드
        st.markdown("""
        <div style="
            font-size:13px;
            font-weight:700;
            margin:10px 0;
        ">
            📄 백서 및 학습 문서 업로드
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "파일 선택",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            key="sidebar_upload"
        )

        if uploaded:

            st.session_state.uploaded_files = [
                f.name for f in uploaded
            ]

        st.caption("200MB per file · PDF, TXT, DOCX")

        # 등록된 문서 관리
        st.markdown("""
        <div style="
            font-size:13px;
            font-weight:700;
            margin:15px 0 8px 0;
        ">
            📋 등록된 문서 관리
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.uploaded_files:

            selected_doc = st.selectbox(
                "문서 선택",
                st.session_state.uploaded_files,
                key="document_select"
            )

            if st.button(
                "선택 문서 목록에서 삭제",
                use_container_width=True
            ):

                st.session_state.uploaded_files.remove(
                    selected_doc
                )
                st.rerun()

        else:

            st.selectbox(
                "문서 선택",
                ["등록된 문서 없음"],
                disabled=True
            )

        st.markdown(
            f"""
            <div style="font-size:12px; margin-top:8px;">
                저장된 문서: {len(st.session_state.uploaded_files)}개
            </div>
            """,
            unsafe_allow_html=True
        )

        # 전체 대화 삭제
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "🗑️  대화 전체 삭제",
            use_container_width=True
        ):

            st.session_state.messages = []
            st.session_state.activities = []
            st.rerun()

        # 하단 문구
        st.markdown("""
        <div style="
            margin-top:55px;
            padding-left:10px;
            font-size:12px;
            line-height:1.8;
        ">
            AIVLE School<br>
            Learning Assistant
        </div>
        """, unsafe_allow_html=True)


# =====================================================
# 7. 오른쪽 공통 영역
# =====================================================

def render_right_panel():

    with st.container():

        # AI Assistant
        st.markdown("""
        <div class="right-card" style="text-align:center;">

            <div style="
                background:#EAF1FA;
                width:80px;
                height:80px;
                border-radius:50%;
                margin:auto;
                display:flex;
                justify-content:center;
                align-items:center;
                font-size:38px;
            ">
                👩🏻‍💻
            </div>

            <h3 style="
                font-size:18px;
                color:#193653;
                margin:12px 0 5px 0;
            ">
                AIVLE Assistant
            </h3>

            <p style="
                font-size:12px;
                color:#91A6B5;
            ">
                Your Learning Partner
            </p>

        </div>
        """, unsafe_allow_html=True)

        # 학습 도우미 안내
        st.markdown("""
        <div class="right-card">

            <h4 style="color:#193653; font-size:16px;">
                📘 학습 도우미 안내
            </h4>

            <p style="
                color:#8195A6;
                font-size:13px;
                line-height:1.8;
            ">
                AIVLE School 교육 자료를 기반으로
                질문에 대한 답변을 제공합니다.
            </p>

            <b style="color:#193653; font-size:13px;">
                RAG 기반 문서 검색
            </b>

            <p style="
                color:#8195A6;
                font-size:13px;
                line-height:1.8;
            ">
                관련 문서를 검색하고 답변을 생성합니다.
            </p>

        </div>
        """, unsafe_allow_html=True)

        # 추천 질문
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

        # 최근 활동
        st.markdown("""
        <div class="right-card" style="margin-top:22px;">

            <h4 style="font-size:15px; color:#193653;">
                🕒 Recent Activity
            </h4>

            <p style="font-size:12px; color:#91A6B5;">
                최근 대화 기록
            </p>

        </div>
        """, unsafe_allow_html=True)

        if st.session_state.activities:

            for activity in reversed(
                st.session_state.activities[-3:]
            ):

                st.markdown(
                    f"""
                    <div style="
                        color:#8195A6;
                        font-size:11px;
                        margin-bottom:10px;
                    ">
                        💬 {activity}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.markdown(
                '<p style="font-size:12px;color:#91A6B5;">'
                '아직 대화 기록이 없습니다.</p>',
                unsafe_allow_html=True
            )


# =====================================================
# 8. 홈 화면
# =====================================================

def page_home():

    main_col, right_col = st.columns(
        [2.5, 1],
        gap="large"
    )

    with main_col:

        header_col, search_col = st.columns([1.2, 0.9])

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
        c1, c2 = st.columns(2, gap="medium")

        with c1:

            st.markdown("""
            <div class="info-card welcome-card">
                <h3>Welcome back! ✨</h3>

                <p>
                    AIVLE School 학습 도우미입니다.<br>
                    교육 과정, 강의 내용, 미니프로젝트 등<br>
                    궁금한 내용을 자유롭게 질문해 보세요!
                </p>

                <div style="text-align:right;font-size:23px;">
                    💻 💬
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:

            st.markdown("""
            <div class="info-card guide-card">
                <h3>Learning Guide 📊</h3>

                <p>
                    여러분의 학습을 도와드릴게요.<br>
                    문서 기반 RAG 시스템을 활용하여<br>
                    필요한 정보를 빠르게 찾아보세요.
                </p>

                <div style="text-align:right;font-size:23px;">
                    💡 📚
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Quick Menu
        st.markdown(
            '<div class="section-title">Quick Menu</div>',
            unsafe_allow_html=True
        )

        quick_items = [
            ("📚", "학습 자료", "교육 문서 기반 질문", "학습 Q&A"),
            ("🧠", "학습 Q&A", "AI 문서 검색 및 답변", "학습 Q&A"),
            ("🚀", "미니프로젝트", "프로젝트 정보 확인", "미니프로젝트")
        ]

        cols = st.columns(3)

        for col, item in zip(cols, quick_items):

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

        # 달력
        st.markdown("""
        <div class="section-title">
            🗓️ 출결 & 일정 관리
        </div>

        <div class="sub-title">
            교육 일정과 개인 학습 일정을 확인해 보세요.
        </div>
        """, unsafe_allow_html=True)

        today = date.today()

        if "cal_year" not in st.session_state:
            st.session_state.cal_year = today.year

        if "cal_month" not in st.session_state:
            st.session_state.cal_month = today.month

        prev, month, next_ = st.columns([1, 4, 1])

        with prev:

            if st.button("‹", use_container_width=True):

                st.session_state.cal_month -= 1

                if st.session_state.cal_month < 1:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1

                st.rerun()

        with month:

            st.markdown(
                f"""
                <h3 style="text-align:center;color:#29445F;">
                    {st.session_state.cal_year}년
                    {st.session_state.cal_month}월
                </h3>
                """,
                unsafe_allow_html=True
            )

        with next_:

            if st.button("›", use_container_width=True):

                st.session_state.cal_month += 1

                if st.session_state.cal_month > 12:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1

                st.rerun()

        weeks = calendar.Calendar(
            firstweekday=6
        ).monthdayscalendar(
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
        </div>
        """

        st.markdown(
            calendar_html,
            unsafe_allow_html=True
        )

    with right_col:

        render_right_panel()


# =====================================================
# 9. 소개 페이지
# =====================================================

def page_intro():

    main_col, right_col = st.columns(
        [2.5, 1],
        gap="large"
    )

    with main_col:

        # 페이지 제목
        st.markdown(
            '<div class="main-title">소개</div>',
            unsafe_allow_html=True
        )

        # 0. 상단 배너
        st.markdown("""
        <div class="intro-banner">

            <div>
                <h1>AIVLE School 학습 도우미 소개</h1>

                <h3>
                    AIVLE School 교육생을 위한 맞춤형 학습 지원 서비스
                </h3>

                <p>
                    KT AIVLE School의 교육 과정, 학습 자료, 프로젝트, 취업 준비까지<br>
                    교육생이 궁금한 내용을 빠르고 정확하게 안내하는<br>
                    RAG 기반 AI 학습 도우미입니다.
                </p>
            </div>

            <div class="banner-image">
                🤖💡
            </div>

        </div>
        """, unsafe_allow_html=True)

        # 01. AIVLE School이란?
        st.markdown("""
        <div class="intro-heading">
            <span class="section-number">01.</span>
            AIVLE School이란?
        </div>

        <div class="intro-white-card" style="
            display:flex;
            align-items:center;
            gap:20px;
            padding:20px;
        ">

            <div style="
                font-size:35px;
                font-weight:900;
                color:#222;
                min-width:65px;
                text-align:center;
            ">
                kt
            </div>

            <div style="
                width:1px;
                height:65px;
                background:#E1EAF0;
            "></div>

            <div style="flex:1;">
                <h4>
                    KT AIVLE School은 KT가 운영하는 AI·DX 실무형 인재 양성 프로그램으로,
                </h4>

                <p>
                    기업 현장에서 요구하는 디지털 역량을 갖춘 인재를 육성합니다.
                </p>
            </div>

            <div style="
                background:#E5F8F7;
                border-radius:15px;
                padding:13px;
                min-width:105px;
                text-align:center;
            ">
                <div style="font-size:23px;">⚙️</div>
                <b style="color:#193653;">AI</b>
                <p>인공지능 역량</p>
            </div>

            <div style="
                background:#EDF5FE;
                border-radius:15px;
                padding:13px;
                min-width:105px;
                text-align:center;
            ">
                <div style="font-size:23px;">📚</div>
                <b style="color:#193653;">DX</b>
                <p>디지털 전환 역량</p>
            </div>

        </div>
        """, unsafe_allow_html=True)

        # 02 + 03
        st.markdown("<br>", unsafe_allow_html=True)

        track_col, field_col = st.columns(
            [1.05, 1.8],
            gap="medium"
        )

        with track_col:

            st.markdown("""
            <div class="intro-heading">
                <span class="section-number">02.</span>
                교육 트랙 소개
            </div>
            """, unsafe_allow_html=True)

            t1, t2 = st.columns(2, gap="small")

            with t1:

                st.markdown("""
                <div class="track-card track-ai">

                    <div style="font-size:30px;">💻</div>

                    <h3>AI 개발자</h3>

                    <p>
                        AI 모델과 서비스 개발을 통해<br>
                        실무형 AI 서비스 구현 역량을 강화
                    </p>

                </div>
                """, unsafe_allow_html=True)

            with t2:

                st.markdown("""
                <div class="track-card track-dx">

                    <div style="font-size:30px;">📊</div>

                    <h3>DX 컨설턴트</h3>

                    <p>
                        데이터 분석과 AI를 활용한<br>
                        기업 문제 해결 및 디지털 전환 기획
                    </p>

                </div>
                """, unsafe_allow_html=True)

        with field_col:

            st.markdown("""
            <div class="intro-heading">
                <span class="section-number">03.</span>
                주요 교육 분야
            </div>
            """, unsafe_allow_html=True)

            f1, f2 = st.columns(2, gap="small")

            with f1:

                st.markdown("""
                <div class="field-card">
                    <div class="field-icon">🐍</div>
                    <div>
                        <strong>프로그래밍·데이터 분석</strong>
                        <small>Python, 데이터 처리 및 시각화</small>
                    </div>
                </div>

                <div class="field-card">
                    <div class="field-icon">🤖</div>
                    <div>
                        <strong>생성형 AI</strong>
                        <small>LLM 및 프롬프트 엔지니어링</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with f2:

                st.markdown("""
                <div class="field-card">
                    <div class="field-icon">🧠</div>
                    <div>
                        <strong>머신러닝·딥러닝</strong>
                        <small>AI 모델 학습과 평가</small>
                    </div>
                </div>

                <div class="field-card">
                    <div class="field-icon">☁️</div>
                    <div>
                        <strong>클라우드</strong>
                        <small>클라우드 인프라와 서비스</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 04. 교육 진행 과정
        st.markdown("""
        <div class="intro-heading">
            <span class="section-number">04.</span>
            교육 진행 과정
        </div>
        """, unsafe_allow_html=True)

        p1, arrow1, p2, arrow2, p3 = st.columns(
            [1.5, 0.2, 1.5, 0.2, 1.5],
            gap="small"
        )

        with p1:

            st.markdown("""
            <div class="process-card">
                <div class="process-item">
                    <div class="process-icon">📖</div>
                    <div>
                        <strong>① 이론 및 실습</strong>
                        <small>기초 기술과 핵심 개념 학습</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with arrow1:

            st.markdown(
                '<div class="process-arrow">➜</div>',
                unsafe_allow_html=True
            )

        with p2:

            st.markdown("""
            <div class="process-card">
                <div class="process-item blue">
                    <div class="process-icon">💻</div>
                    <div>
                        <strong>② 미니 프로젝트</strong>
                        <small>학습한 기술을 활용한 문제 해결 경험</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with arrow2:

            st.markdown(
                '<div class="process-arrow">➜</div>',
                unsafe_allow_html=True
            )

        with p3:

            st.markdown("""
            <div class="process-card">
                <div class="process-item blue">
                    <div class="process-icon">🚀</div>
                    <div>
                        <strong>③ 빅 프로젝트</strong>
                        <small>실제 문제 발굴부터 결과물 구현 및 발표</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 05. 핵심 역량
        st.markdown("""
        <div class="intro-heading">
            <span class="section-number">05.</span>
            교육을 통해 기르는 핵심 역량
        </div>
        """, unsafe_allow_html=True)

        skill_items = [
            (
                "💡",
                "문제 해결 역량",
                "실무 문제를 정의하고<br>데이터·AI로 해결"
            ),
            (
                "📊",
                "데이터 활용 역량",
                "데이터 수집·분석·해석을 통한<br>인사이트 도출"
            ),
            (
                "👥",
                "협업·소통 역량",
                "팀 프로젝트를 통한<br>효과적인 협업과 의사소통"
            ),
            (
                "🎯",
                "프로젝트 수행 역량",
                "기획부터 구현, 발표까지<br>완성도 높은 프로젝트 경험"
            )
        ]

        skill_cols = st.columns(4, gap="small")

        for col, item in zip(skill_cols, skill_items):

            emoji, title, desc = item

            with col:

                st.markdown(f"""
                <div class="skill-card">

                    <div class="skill-icon">{emoji}</div>

                    <h4>{title}</h4>

                    <p>{desc}</p>

                </div>
                """, unsafe_allow_html=True)

        # 하단 배너
        st.markdown("""
        <div class="bottom-banner">

            <div style="
                display:flex;
                align-items:center;
                gap:20px;
            ">

                <div style="
                    font-size:35px;
                    border-right:1px solid rgba(255,255,255,0.5);
                    padding-right:20px;
                ">
                    ◢
                </div>

                <div>
                    <h3>
                        Your Next Step with AIVLE School!
                    </h3>

                    <p>
                        AIVLE School과 함께, AI와 DX로 더 큰 성장의 기회를 만들어보세요.
                    </p>
                </div>

            </div>

        </div>
        """, unsafe_allow_html=True)

    # 오른쪽 영역
    with right_col:

        render_right_panel()


# =====================================================
# 10. 학습 Q&A
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

    # 대기 질문 처리
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
# 11. 기타 페이지
# =====================================================

def page_placeholder():

    main_col, right_col = st.columns(
        [2.5, 1],
        gap="large"
    )

    with main_col:

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

    with right_col:

        render_right_panel()


# =====================================================
# 12. 페이지 실행
# =====================================================

render_sidebar()

if st.session_state.page == "홈":

    page_home()

elif st.session_state.page == "소개":

    page_intro()

elif st.session_state.page == "학습 Q&A":

    page_chat()

else:

    page_placeholder()

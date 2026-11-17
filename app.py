
import os
import tempfile
import hashlib
import textwrap
import streamlit as st

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from operator import itemgetter


# =====================================================
# 1. 페이지 설정
# =====================================================

st.set_page_config(
    page_title="AIVLE School 학습 도우미",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. 기본 설정
# =====================================================

CHROMA_DIR = "chroma_db"
COLLECTION = "aivle_docs"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


# =====================================================
# 3. HTML 렌더링 함수
# =====================================================

def render_html(content):

    html = textwrap.dedent(content).strip()

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# =====================================================
# 4. API KEY 읽어오기
# =====================================================

def load_api_key():

    # Streamlit Cloud Secrets
    try:
        key = st.secrets.get("OPENAI_API_KEY", None)

        if key:
            os.environ["OPENAI_API_KEY"] = key
            return

    except Exception:
        pass

    # 환경변수
    if os.getenv("OPENAI_API_KEY"):
        return

    # 로컬 api_key.txt
    filepath = "./api_key.txt"

    if os.path.exists(filepath):

        with open(filepath, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if line and "=" in line:

                    key, value = line.split("=", 1)

                    value = value.strip().strip('"').strip("'")

                    os.environ[key.strip()] = value


load_api_key()

api_key = os.getenv("OPENAI_API_KEY")


# =====================================================
# 5. CSS 디자인
# =====================================================

st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background-color: #edf6f7;
}

.block-container {
    max-width: 1550px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

#MainMenu,
footer {
    visibility: hidden;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #78c5cd;
}

section[data-testid="stSidebar"] > div {
    padding: 25px 15px;
}

/* 사이드바 글씨 */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: white;
}

/* 로고 */
.logo-area {
    background-color: white;
    border-radius: 18px;
    padding: 15px;
    margin-bottom: 30px;
    text-align: center;
}

.logo-area img {
    width: 145px;
    max-width: 100%;
    height: auto;
}

.logo-area p {
    color: #9aa8b0 !important;
    font-size: 11px;
    margin: 0;
}

/* 인사말 */
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

/* 대시보드 카드 */
.dashboard-card {
    border-radius: 23px;
    padding: 24px;
    min-height: 165px;
    box-shadow: 0 5px 20px rgba(50,80,100,0.07);
    margin-bottom: 18px;
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
    line-height: 1.8;
    color: white;
}

/* Quick Menu */
.feature-card {
    background-color: white;
    border-radius: 20px;
    padding: 17px 12px;
    box-shadow: 0 5px 18px rgba(50,80,100,0.06);
    min-height: 110px;
    text-align: center;
    color: #263c54;
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
    margin: 18px 0 15px 0;
}

/* 채팅 영역 */
.chat-box {
    background-color: white;
    border-radius: 25px;
    padding: 22px;
    min-height: 370px;
    box-shadow: 0 5px 20px rgba(50,80,100,0.06);
}

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

/* 프로필 */
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

/* 안내 카드 */
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
}

.stButton > button:hover {
    border-color: #55b9c1;
    color: #269eaa;
    background-color: #f0fbfb;
}

/* 입력창 */
div[data-testid="stTextInput"] input {
    border: none;
    border-radius: 12px;
    background-color: white;
    min-height: 42px;
}

/* 파일 업로더 */
div[data-testid="stFileUploader"] {
    background-color: white;
    border-radius: 13px;
    padding: 10px;
}

/* 채팅 입력창 */
div[data-testid="stChatInput"] {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 6. 세션 상태 초기화
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# =====================================================
# 7. 문서 포맷팅 함수
# =====================================================

def format_docs(docs):

    result = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "출처 미상"
        )

        page = doc.metadata.get(
            "page",
            "페이지 정보 없음"
        )

        result.append(
            f"""
[출처: {source} / 페이지: {page}]

{doc.page_content}
"""
        )

    return "\n\n".join(result)


# =====================================================
# 8. Embedding 모델
# =====================================================

@st.cache_resource
def get_embedding():

    embedding = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    return embedding


# =====================================================
# 9. 벡터 저장소
# =====================================================

@st.cache_resource
def get_vectorstore():

    embedding = get_embedding()

    vectorstore = Chroma(
        collection_name=COLLECTION,
        embedding_function=embedding,
        persist_directory=CHROMA_DIR
    )

    return vectorstore


# =====================================================
# 10. PDF 파일 읽기
# =====================================================

def load_pdf(uploaded_file):

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as temp_file:

            temp_file.write(
                uploaded_file.getvalue()
            )

            temp_path = temp_file.name

        loader = PyMuPDF4LLMLoader(temp_path)

        docs = loader.load()

        for doc in docs:

            doc.metadata["source"] = uploaded_file.name

        return docs

    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


# =====================================================
# 11. 텍스트 분할
# =====================================================

def split_documents(docs):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_documents(docs)

    return chunks


# =====================================================
# 12. 기존 문서 삭제
# =====================================================

def delete_document(filename):

    vectorstore = get_vectorstore()

    result = vectorstore.get(
        where={"source": filename}
    )

    ids = result.get("ids", [])

    if ids:

        vectorstore.delete(ids=ids)

    return len(ids)


# =====================================================
# 13. 문서 업로드 및 벡터화
# =====================================================

def process_document(uploaded_file):

    # PDF 읽기
    docs = load_pdf(uploaded_file)

    # 텍스트 분할
    chunks = split_documents(docs)

    if not chunks:

        raise ValueError(
            "PDF에서 텍스트를 추출하지 못했습니다."
        )

    vectorstore = get_vectorstore()

    filename = uploaded_file.name

    # 동일 파일명 문서 교체
    delete_document(filename)

    # 청크 ID 생성
    ids = []

    for index, chunk in enumerate(chunks):

        unique_text = (
            filename
            + str(index)
            + chunk.page_content
        )

        doc_id = hashlib.sha256(
            unique_text.encode("utf-8")
        ).hexdigest()

        ids.append(doc_id)

    # 벡터 저장
    vectorstore.add_documents(
        documents=chunks,
        ids=ids
    )

    return len(chunks)


# =====================================================
# 14. 등록된 문서 목록
# =====================================================

def get_document_list():

    vectorstore = get_vectorstore()

    result = vectorstore.get(
        include=["metadatas"]
    )

    document_counts = {}

    for metadata in result.get("metadatas", []):

        if metadata:

            filename = metadata.get("source")

            if filename:

                document_counts[filename] = (
                    document_counts.get(filename, 0) + 1
                )

    return document_counts


# =====================================================
# 15. RAG 체인 구성
# =====================================================

@st.cache_resource
def get_chain():

    retriever = get_vectorstore().as_retriever(
        search_kwargs={"k": 3}
    )

    s_msg = """
당신은 AIVLE School 교육생을 위한 학습 도우미입니다.

반드시 제공된 문서를 기반으로 답변하세요.

[답변 규칙]

1. 문서에 있는 정보를 근거로 답변하세요.
2. 문서에 없는 내용을 임의로 만들어내지 마세요.
3. 관련 내용을 찾을 수 없다면
   '등록된 문서에서 해당 내용을 확인할 수 없습니다.'
   라고 답변하세요.
4. 교육생이 이해하기 쉽도록 친절하고 구체적으로 설명하세요.
5. 필요하다면 항목별로 정리하세요.
6. 선배 경험이나 학습 조언도 문서에 근거가 있는 경우에만 답변하세요.

[참고 문서]

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
            "context": itemgetter("input")
            | retriever
            | format_docs,

            "input": itemgetter("input")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# =====================================================
# 16. 참고 문서 검색
# =====================================================

def get_sources(question):

    retriever = get_vectorstore().as_retriever(
        search_kwargs={"k": 3}
    )

    docs = retriever.invoke(question)

    sources = []
    seen = set()

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "출처 미상"
        )

        page = doc.metadata.get(
            "page",
            "페이지 정보 없음"
        )

        key = (source, page)

        if key not in seen:

            seen.add(key)

            sources.append({
                "source": source,
                "page": page
            })

    return sources


# =====================================================
# 17. 사이드바
# =====================================================

with st.sidebar:

    # AIVLE 로고
    render_html("""
    <div class="logo-area">

        <img
            src="https://raw.githubusercontent.com/Jangrae/img/master/aivle.png"
            alt="AIVLE School Logo">

        <p>AIVLE SCHOOL</p>

    </div>
    """)

    # 메뉴
    render_html("""
    <div style="
        color:white;
        font-weight:600;
        line-height:3.5;
        font-size:14px;
    ">

        🏠　홈<br>
        📚　학습 도우미<br>
        📁　학습 자료<br>
        💬　대화 기록

    </div>
    """)

    st.markdown("---")

    st.markdown("### ⚙️ 관리자")

    st.markdown("**📄 백서 및 학습 문서 업로드**")

    uploaded_file = st.file_uploader(
        "PDF 파일 선택",
        type=["pdf"],
        key="pdf_uploader"
    )

    if uploaded_file:

        st.caption(
            f"선택된 파일: {uploaded_file.name}"
        )

        if st.button(
            "📥 문서 업로드 및 벡터화",
            use_container_width=True
        ):

            if not api_key:

                st.error(
                    "OpenAI API Key를 설정해 주세요."
                )

            else:

                try:

                    with st.spinner(
                        "문서를 읽고 벡터화하고 있습니다..."
                    ):

                        chunk_count = process_document(
                            uploaded_file
                        )

                    st.success(
                        f"업로드 완료! {chunk_count}개 청크 저장"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"문서 처리 오류: {str(e)}"
                    )

    st.markdown("---")

    st.markdown("**📚 등록된 문서 관리**")

    if api_key:

        try:

            documents = get_document_list()

            if documents:

                selected_document = st.selectbox(
                    "문서 선택",
                    list(documents.keys())
                )

                st.caption(
                    f"저장된 청크: "
                    f"{documents[selected_document]}개"
                )

                if st.button(
                    "🗑️ 선택 문서 삭제",
                    use_container_width=True
                ):

                    delete_document(selected_document)

                    st.success(
                        "문서가 삭제되었습니다."
                    )

                    st.rerun()

            else:

                st.info("등록된 문서가 없습니다.")

        except Exception as e:

            st.error(str(e))

    st.markdown("---")

    if st.button(
        "🗑️ 대화 전체 삭제",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    render_html("""
    <div style="
        margin-top:45px;
        color:white;
        font-size:12px;
        line-height:1.7;
    ">
        AIVLE School<br>
        Learning Assistant
    </div>
    """)


# =====================================================
# 18. 메인 화면 레이아웃
# =====================================================

left, right = st.columns(
    [7, 3],
    gap="large"
)


# =====================================================
# 19. 중앙 대시보드
# =====================================================

with left:

    # 인사말과 검색창
    title_col, search_col = st.columns(
        [5, 4]
    )

    with title_col:

        render_html("""
        <div class="greeting">
            Hello, AIVLE! 👋
        </div>

        <div class="sub-greeting">
            오늘도 새로운 지식을 함께 배워봐요.
        </div>
        """)

    with search_col:

        with st.form("search_form"):

            search_value = st.text_input(
                "검색",
                placeholder="궁금한 내용을 검색해 보세요.",
                label_visibility="collapsed"
            )

            search_submitted = st.form_submit_button(
                "검색",
                use_container_width=True
            )

        if search_submitted and search_value.strip():

            st.session_state.pending_prompt = (
                search_value.strip()
            )

    # Welcome 카드
    card1, card2 = st.columns(2)

    with card1:

        render_html("""
        <div class="dashboard-card welcome-card">

            <h3>Welcome back! ✨</h3>

            <p>
                AIVLE School 학습 도우미입니다.<br>
                교육 과정, 강의 내용, 미니프로젝트 등<br>
                궁금한 내용을 자유롭게 질문해 보세요!
            </p>

            <div style="
                font-size:27px;
                text-align:right;
            ">
                📘 🤖
            </div>

        </div>
        """)

    with card2:

        render_html("""
        <div class="dashboard-card result-card">

            <h3>Learning Guide 📊</h3>

            <p>
                여러분의 학습을 도와드릴게요.<br>
                문서 기반 RAG 시스템을 활용하여<br>
                필요한 정보를 빠르게 찾아보세요.
            </p>

            <div style="
                font-size:27px;
                text-align:right;
            ">
                💡 📚
            </div>

        </div>
        """)

    # Quick Menu
    render_html("""
    <div class="section-title">
        Quick Menu
    </div>
    """)

    f1, f2, f3 = st.columns(3)

    with f1:

        render_html("""
        <div class="feature-card">

            <div class="feature-icon">📚</div>

            <div class="feature-title">
                학습 자료
            </div>

            <div class="feature-desc">
                교육 문서 기반 질문
            </div>

        </div>
        """)

    with f2:

        render_html("""
        <div class="feature-card">

            <div class="feature-icon">🧠</div>

            <div class="feature-title">
                학습 Q&A
            </div>

            <div class="feature-desc">
                AI 문서 검색 및 답변
            </div>

        </div>
        """)

    with f3:

        render_html("""
        <div class="feature-card">

            <div class="feature-icon">🚀</div>

            <div class="feature-title">
                미니프로젝트
            </div>

            <div class="feature-desc">
                프로젝트 정보 확인
            </div>

        </div>
        """)

    # 채팅 영역 제목
    render_html("""
    <div class="section-title">
        💬 AI Learning Assistant
    </div>

    <div class="chat-box">

        <div class="chat-heading">
            🤖 AIVLE School 학습 도우미
        </div>

        <div class="chat-description">
            궁금한 내용을 질문하면 관련 문서를 찾아
            답변해 드립니다.
        </div>

    </div>
    """)

    # 이전 대화 출력
    if not st.session_state.messages:

        st.info(
            "안녕하세요! 😊 무엇이 궁금하신가요? "
            "아래 입력창에 질문을 작성해 주세요."
        )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if (
                message["role"] == "assistant"
                and message.get("sources")
            ):

                with st.expander("📚 참고 문서 확인"):

                    for source in message["sources"]:

                        st.markdown(
                            f"- {source['source']} "
                            f"(페이지: {source['page']})"
                        )


# =====================================================
# 20. 오른쪽 영역
# =====================================================

with right:

    # 프로필
    render_html("""
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
    render_html("""
    <div class="info-card">

        <div class="info-title">
            📘 학습 도우미 안내
        </div>

        <p>
            AIVLE School 교육 자료를 기반으로
            질문에 대한 답변을 제공합니다.
        </p>

        <b style="
            color:#29445b;
            font-size:12px;
        ">
            RAG 기반 문서 검색
        </b>

        <p>
            관련 문서를 검색하고 답변을 생성합니다.
        </p>

    </div>
    """)

    # 추천 질문
    render_html("""
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

    for i, question in enumerate(questions):

        if st.button(
            question,
            key=f"recommend_{i}",
            use_container_width=True
        ):

            st.session_state.pending_prompt = question

            st.rerun()

    # 최근 활동
    render_html("<br>")

    render_html("""
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
        msg["content"]
        for msg in reversed(st.session_state.messages)
        if msg["role"] == "user"
    ]

    if recent_questions:

        for question in recent_questions[:5]:

            st.caption(
                "💬 " + question[:35]
            )

    else:

        st.caption(
            "아직 대화 기록이 없습니다."
        )


# =====================================================
# 21. 질문 입력 및 RAG 답변
# =====================================================

user_input = st.chat_input(
    "질문을 입력하세요."
)

prompt = None

# 추천 질문 또는 검색창 질문
if st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt

    st.session_state.pending_prompt = None

# 직접 입력한 질문
elif user_input:

    prompt = user_input.strip()


if prompt:

    if not api_key:

        st.error(
            "OpenAI API Key를 설정한 후 이용해 주세요."
        )

    else:

        try:

            documents = get_document_list()

            if not documents:

                st.warning(
                    "등록된 문서가 없습니다. "
                    "관리자 영역에서 AIVLE School 백서를 "
                    "먼저 업로드해 주세요."
                )

            else:

                # 사용자 질문 저장
                st.session_state.messages.append({
                    "role": "user",
                    "content": prompt
                })

                # 참고 문서 검색
                sources = get_sources(prompt)

                # RAG 체인 실행
                chain = get_chain()

                with st.chat_message("assistant"):

                    with st.spinner(
                        "관련 문서를 검색하고 있습니다..."
                    ):

                        response_stream = chain.stream({
                            "input": prompt
                        })

                        full_response = st.write_stream(
                            response_stream
                        )

                    # 참고 문서 표시
                    if sources:

                        with st.expander(
                            "📚 참고 문서 확인"
                        ):

                            for source in sources:

                                st.markdown(
                                    f"- **{source['source']}** "
                                    f"(페이지: {source['page']})"
                                )

                # 답변 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": sources
                })

        except Exception as e:

            st.error(
                f"답변 생성 중 오류가 발생했습니다: {str(e)}"
            )

    st.rerun()

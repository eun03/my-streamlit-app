
import os
import hashlib
from io import BytesIO

import streamlit as st

from pypdf import PdfReader
from docx import Document as DocxDocument

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter


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

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
SEARCH_K = 4


# =====================================================
# 3. API KEY 설정
# =====================================================

def get_api_key():

    # Streamlit Community Cloud Secrets
    try:
        key = st.secrets.get("OPENAI_API_KEY", None)

        if key:
            return key

    except Exception:
        pass

    # 환경변수
    return os.getenv("OPENAI_API_KEY")


api_key = get_api_key()

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key


# =====================================================
# 4. CSS 디자인
# =====================================================

st.markdown("""
<style>

/* 전체 배경 */
.stApp {
    background-color: #edf6f7;
}

/* 메인 화면 */
.block-container {
    max-width: 1550px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* 상단 메뉴 */
.stAppHeader {
    background-color: transparent;
}

/* 기본 메뉴 숨기기 */
#MainMenu, footer {
    visibility: hidden;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #78c5cd;
    min-width: 230px;
}

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
    background-color: white;
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

/* 채팅 컨테이너 */
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

/* 정보 카드 */
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

/* 입력창 */
div[data-testid="stTextInput"] input {
    border: none;
    border-radius: 12px;
    background-color: white;
    min-height: 42px;
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

/* 채팅 말풍선 */
div[data-testid="stChatMessage"] {
    border-radius: 15px;
    padding: 13px;
    margin-bottom: 12px;
}

/* 구분선 */
hr {
    border-color: #e9eff2;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 5. 세션 상태 초기화
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# =====================================================
# 6. Embedding 및 Vector DB
# =====================================================

@st.cache_resource
def get_embeddings():

    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )


@st.cache_resource
def get_vectorstore():

    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )


# =====================================================
# 7. 문서 텍스트 추출
# =====================================================

def extract_documents(uploaded_file):

    filename = uploaded_file.name
    file_bytes = uploaded_file.getvalue()

    documents = []

    # PDF
    if filename.lower().endswith(".pdf"):

        reader = PdfReader(BytesIO(file_bytes))

        for page_num, page in enumerate(reader.pages, start=1):

            text = page.extract_text() or ""

            if text.strip():

                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": filename,
                            "page": page_num
                        }
                    )
                )

    # TXT
    elif filename.lower().endswith(".txt"):

        try:
            text = file_bytes.decode("utf-8-sig")

        except UnicodeDecodeError:
            text = file_bytes.decode("cp949")

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": filename,
                    "page": 1
                }
            )
        )

    # DOCX
    elif filename.lower().endswith(".docx"):

        docx_file = DocxDocument(BytesIO(file_bytes))

        text = "\n".join(
            paragraph.text
            for paragraph in docx_file.paragraphs
            if paragraph.text.strip()
        )

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": filename,
                    "page": 1
                }
            )
        )

    else:

        raise ValueError("지원하지 않는 문서 형식입니다.")

    documents = [
        doc for doc in documents
        if doc.page_content.strip()
    ]

    if not documents:
        raise ValueError(
            "문서에서 텍스트를 추출하지 못했습니다. "
            "스캔된 PDF라면 OCR 처리가 필요합니다."
        )

    return documents


# =====================================================
# 8. 문서 청크 분할
# =====================================================

def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    return chunks


# =====================================================
# 9. 기존 문서 삭제
# =====================================================

def delete_document(filename):

    vectorstore = get_vectorstore()

    result = vectorstore.get(
        where={
            "source": filename
        },
        include=["metadatas"]
    )

    ids = result.get("ids", [])

    if ids:

        vectorstore.delete(ids=ids)

    return len(ids)


# =====================================================
# 10. 문서 업로드 및 벡터화
# =====================================================

def upload_and_process(uploaded_file):

    filename = uploaded_file.name

    # 1. 텍스트 추출
    documents = extract_documents(uploaded_file)

    # 2. 청크 분할
    chunks = split_documents(documents)

    if not chunks:
        raise ValueError("문서 청크를 생성하지 못했습니다.")

    # 3. 문서 교체 시 기존 데이터 삭제
    delete_document(filename)

    # 4. 고유 ID 생성
    ids = []

    for index, chunk in enumerate(chunks):

        content_hash = hashlib.sha256(
            (
                filename
                + str(index)
                + chunk.page_content
            ).encode("utf-8")
        ).hexdigest()

        ids.append(content_hash)

    # 5. 벡터 DB 저장
    vectorstore = get_vectorstore()

    vectorstore.add_documents(
        documents=chunks,
        ids=ids
    )

    return len(chunks)


# =====================================================
# 11. 저장된 문서 목록 조회
# =====================================================

def get_document_list():

    vectorstore = get_vectorstore()

    result = vectorstore.get(
        include=["metadatas"]
    )

    metadata_list = result.get("metadatas", [])

    document_counts = {}

    for metadata in metadata_list:

        if not metadata:
            continue

        filename = metadata.get("source")

        if filename:

            document_counts[filename] = (
                document_counts.get(filename, 0) + 1
            )

    return document_counts


# =====================================================
# 12. RAG 검색
# =====================================================

def retrieve_documents(question):

    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": SEARCH_K
        }
    )

    docs = retriever.invoke(question)

    return docs


# =====================================================
# 13. 문서 컨텍스트 구성
# =====================================================

def format_docs(docs):

    formatted = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "출처 미상"
        )

        page = doc.metadata.get(
            "page",
            "페이지 정보 없음"
        )

        formatted.append(
            f"""
[출처: {source} / 페이지: {page}]

{doc.page_content}
"""
        )

    return "\n\n".join(formatted)


# =====================================================
# 14. RAG 답변 생성
# =====================================================

def generate_answer(question):

    docs = retrieve_documents(question)

    if not docs:

        return (
            "죄송합니다. 현재 등록된 AIVLE School 문서에서 "
            "관련 정보를 찾을 수 없습니다."
        ), []

    context = format_docs(docs)

    system_message = """
당신은 AIVLE School 교육생을 위한 전문 학습 도우미입니다.

반드시 제공된 문서 내용을 근거로 답변하세요.

[답변 규칙]

1. 제공된 문서에 있는 정보를 우선적으로 사용하세요.
2. 문서에 없는 내용을 사실처럼 만들어내지 마세요.
3. 질문과 관련된 내용이 문서에 없다면
   "등록된 문서에서 해당 내용을 확인할 수 없습니다."
   라고 답변하세요.
4. 교육생이 이해하기 쉽게 친절하고 구체적으로 설명하세요.
5. 여러 정보가 있다면 항목별로 정리하세요.
6. 경험이나 조언이 필요한 질문도 문서에 관련 내용이
   있을 때만 근거를 바탕으로 답변하세요.
7. 답변에 활용한 문서의 파일명과 페이지를 표시하세요.

[참고 문서]

{context}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}")
    ])

    llm = ChatOpenAI(
        model=CHAT_MODEL,
        streaming=True,
        temperature=0
    )

    chain = prompt | llm

    response = chain.stream({
        "context": context,
        "input": question
    })

    return response, docs


# =====================================================
# 15. 사이드바 - 관리자 영역
# =====================================================

with st.sidebar:

    # 로고
    st.html("""
    <div class="logo-area">
        <img
            src="https://raw.githubusercontent.com/Jangrae/img/master/aivle.png"
            width="145">
        <p>AIVLE SCHOOL</p>
    </div>
    """)

    # 메뉴
    st.html("""
    <div class="menu-item menu-active">
        🏠　홈
    </div>

    <div class="menu-item">
        📚　학습 도우미
    </div>

    <div class="menu-item">
        📁　학습 자료
    </div>

    <div class="menu-item">
        💬　대화 기록
    </div>
    """)

    st.markdown("---")

    st.markdown("### ⚙️ 관리자 영역")

    # 문서 업로드
    st.markdown("**📄 백서 및 학습 문서 업로드**")

    uploaded_file = st.file_uploader(
        "PDF, TXT, DOCX 파일 선택",
        type=["pdf", "txt", "docx"],
        key="document_uploader"
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
                    "OpenAI API Key를 먼저 설정해 주세요."
                )

            else:

                try:

                    with st.spinner(
                        "문서 추출 및 벡터화 진행 중..."
                    ):

                        chunk_count = upload_and_process(
                            uploaded_file
                        )

                    st.success(
                        f"업로드 완료! 총 {chunk_count}개 청크 저장"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"문서 처리 실패: {str(e)}"
                    )

    st.markdown("---")

    # 등록 문서 관리
    st.markdown("**📚 등록된 문서 관리**")

    if api_key:

        try:

            document_list = get_document_list()

            if document_list:

                st.caption(
                    f"총 {len(document_list)}개 문서 등록"
                )

                selected_document = st.selectbox(
                    "관리할 문서 선택",
                    options=list(document_list.keys()),
                    key="selected_document"
                )

                st.caption(
                    f"저장된 청크: "
                    f"{document_list[selected_document]}개"
                )

                if st.button(
                    "🗑️ 선택 문서 삭제",
                    use_container_width=True
                ):

                    deleted_count = delete_document(
                        selected_document
                    )

                    st.success(
                        f"{deleted_count}개 청크 삭제 완료"
                    )

                    st.rerun()

            else:

                st.info(
                    "등록된 문서가 없습니다."
                )

        except Exception as e:

            st.error(
                f"문서 목록 조회 실패: {str(e)}"
            )

    else:

        st.warning(
            "API Key 설정 후 문서를 관리할 수 있습니다."
        )

    st.markdown("---")

    # 대화 삭제
    if st.button(
        "🗑️ 대화 전체 삭제",
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


# =====================================================
# 16. 메인 화면
# =====================================================

left, right = st.columns(
    [7, 3],
    gap="large"
)


# =====================================================
# 17. 중앙 대시보드
# =====================================================

with left:

    title_col, search_col = st.columns([5, 4])

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

    # 환영 카드
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

    # Quick Menu
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

    # 채팅 영역
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

        # API Key 확인
        if not api_key:

            st.warning(
                "OpenAI API Key가 설정되지 않았습니다. "
                "Secrets에 API Key를 등록해 주세요."
            )

        # 최초 안내
        if not st.session_state.messages:

            st.info(
                "안녕하세요! 😊 무엇이 궁금하신가요? "
                "아래 입력창에 질문을 작성해 주세요."
            )

        # 기존 대화 출력
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
                                f"- **{source['source']}** "
                                f"(페이지: {source['page']})"
                            )

        # 질문 입력
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


# =====================================================
# 18. 오른쪽 프로필 및 추천 질문
# =====================================================

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

    # 안내 카드
    st.html("""
    <div class="info-card">

        <div class="info-title">
            📘 학습 도우미 안내
        </div>

        <p>
            AIVLE School 교육 자료를 기반으로
            질문에 대한 답변을 제공합니다.
        </p>

        <b style="color:#29445b;font-size:12px;">
            RAG 기반 문서 검색
        </b>

        <p>
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

    # 최근 활동
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
        msg["content"]
        for msg in reversed(st.session_state.messages)
        if msg["role"] == "user"
    ]

    if recent_questions:

        for q in recent_questions[:5]:

            st.caption("💬 " + q[:35])

    else:

        st.caption("아직 대화 기록이 없습니다.")


# =====================================================
# 19. 질문 처리 및 RAG 답변 생성
# =====================================================

prompt = None

# 직접 입력한 질문
if submitted and question.strip():

    prompt = question.strip()

# 추천 질문 및 검색창 질문
elif st.session_state.pending_prompt:

    prompt = st.session_state.pending_prompt


if prompt:

    st.session_state.pending_prompt = None

    if not api_key:

        st.error(
            "OpenAI API Key를 설정한 후 이용해 주세요."
        )

    else:

        # 문서 등록 여부 확인
        try:

            document_list = get_document_list()

            if not document_list:

                st.warning(
                    "아직 등록된 문서가 없습니다. "
                    "관리자 영역에서 AIVLE School 백서를 "
                    "먼저 업로드해 주세요."
                )

            else:

                # 사용자 질문 저장
                st.session_state.messages.append({
                    "role": "user",
                    "content": prompt
                })

                # AI 응답
                with st.chat_message("assistant"):

                    with st.spinner(
                        "관련 문서를 검색하고 있습니다..."
                    ):

                        response_stream, docs = generate_answer(
                            prompt
                        )

                    full_response = st.write_stream(
                        response_stream
                    )

                    # 참고 문서 정보
                    sources = []

                    seen_sources = set()

                    for doc in docs:

                        source = doc.metadata.get(
                            "source",
                            "출처 미상"
                        )

                        page = doc.metadata.get(
                            "page",
                            "페이지 정보 없음"
                        )

                        source_key = (source, page)

                        if source_key not in seen_sources:

                            seen_sources.add(source_key)

                            sources.append({
                                "source": source,
                                "page": page
                            })

                    if sources:

                        with st.expander(
                            "📚 참고 문서 확인",
                            expanded=False
                        ):

                            for source in sources:

                                st.markdown(
                                    f"- **{source['source']}** "
                                    f"(페이지: {source['page']})"
                                )

                # AI 응답 저장
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
